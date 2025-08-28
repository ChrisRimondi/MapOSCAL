"""
Kubernetes Analyzer for MapOSCAL.

This module provides specialized analysis of Kubernetes resource YAML files,
creating workload groupings and extracting security-relevant information
for OSCAL component generation.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import yaml
import json
import hashlib
from collections import defaultdict

from maposcal.embeddings import local_embedder, faiss_index, meta_store
from maposcal.utils.metadata import generate_metadata, inject_metadata_into_json

logger = logging.getLogger(__name__)


class K8sResourceParser:
    """
    Parses Kubernetes YAML/JSON files and extracts key resource information.
    """
    
    def __init__(self):
        self.workload_kinds = {
            'Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Pod'
        }
    
    def parse_resources(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Parse multiple K8s resource files and extract key information.
        
        Args:
            file_paths: List of paths to K8s resource files
            
        Returns:
            List of parsed resource dictionaries with key fields
        """
        resources = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Split multi-document YAML files
                documents = list(yaml.safe_load_all(content))
                
                for doc in documents:
                    if doc and isinstance(doc, dict) and 'kind' in doc:
                        resource = self._extract_key_fields(doc, file_path)
                        if resource:
                            resources.append(resource)
                            
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue
        
        return resources
    
    def _extract_key_fields(self, doc: Dict[str, Any], source_file: str) -> Optional[Dict[str, Any]]:
        """
        Extract key fields from a K8s resource.
        
        Args:
            doc: Parsed YAML document
            source_file: Source file path
            
        Returns:
            Dictionary with extracted key fields or None if invalid
        """
        try:
            kind = doc.get('kind')
            metadata = doc.get('metadata', {})
            
            resource = {
                'kind': kind,
                'name': metadata.get('name', ''),
                'namespace': metadata.get('namespace', 'default'),
                'labels': metadata.get('labels', {}),
                'annotations': metadata.get('annotations', {}),
                'source_file': source_file,
                'raw_resource': doc
            }
            
            # Extract selectors for Services
            if kind == 'Service':
                spec = doc.get('spec', {})
                resource['selectors'] = spec.get('selector', {})
                resource['ports'] = spec.get('ports', [])
            
            # Extract pod template for workloads
            elif kind in self.workload_kinds:
                resource['pod_template'] = self._extract_pod_template(doc)
                resource['service_account'] = resource['pod_template'].get('serviceAccountName')
            
            # Extract backend services for Ingress
            elif kind == 'Ingress':
                spec = doc.get('spec', {})
                resource['backend_services'] = self._extract_backend_services(spec)
            
            return resource
            
        except Exception as e:
            logger.warning(f"Failed to extract fields from {kind} resource: {e}")
            return None
    
    def _extract_pod_template(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract pod template information from workload resources.
        
        Args:
            doc: Workload resource document
            
        Returns:
            Dictionary with pod template information
        """
        pod_template = {}
        
        if doc['kind'] == 'Pod':
            # Pod is already the template
            pod_template = {
                'labels': doc.get('metadata', {}).get('labels', {}),
                'containers': doc.get('spec', {}).get('containers', []),
                'initContainers': doc.get('spec', {}).get('initContainers', []),
                'volumes': doc.get('spec', {}).get('volumes', []),
                'serviceAccountName': doc.get('spec', {}).get('serviceAccountName')
            }
        else:
            # Extract from pod template
            spec = doc.get('spec', {})
            template = spec.get('template', {})
            pod_template = {
                'labels': template.get('metadata', {}).get('labels', {}),
                'containers': template.get('spec', {}).get('containers', []),
                'initContainers': template.get('spec', {}).get('initContainers', []),
                'volumes': template.get('spec', {}).get('volumes', []),
                'serviceAccountName': template.get('spec', {}).get('serviceAccountName')
            }
        
        return pod_template
    
    def _extract_backend_services(self, spec: Dict[str, Any]) -> List[str]:
        """
        Extract backend service names from Ingress spec.
        
        Args:
            spec: Ingress spec section
            
        Returns:
            List of backend service names
        """
        backend_services = []
        
        # Handle default backend
        default_backend = spec.get('defaultBackend')
        if default_backend and 'service' in default_backend:
            backend_services.append(default_backend['service']['name'])
        
        # Handle rules
        rules = spec.get('rules', [])
        for rule in rules:
            http = rule.get('http', {})
            paths = http.get('paths', [])
            for path in paths:
                backend = path.get('backend', {})
                if 'service' in backend:
                    backend_services.append(backend['service']['name'])
        
        return backend_services


class WorkloadGrouper:
    """
    Groups K8s resources into logical workloads based on the specified logic.
    """
    
    def __init__(self):
        self.workloads = {}
        self.shared_resources = set()
    
    def group_resources(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Group resources into workloads following the specified logic.
        
        Args:
            resources: List of parsed K8s resources
            
        Returns:
            Dictionary of workload groupings
        """
        # Step 1: Group by namespace
        resources_by_namespace = defaultdict(list)
        for resource in resources:
            namespace = resource.get('namespace', 'default')
            resources_by_namespace[namespace].append(resource)
        
        # Step 2: Process each namespace
        for namespace, namespace_resources in resources_by_namespace.items():
            self._process_namespace(namespace, namespace_resources)
        
        # Step 3: Mark shared resources
        self._mark_shared_resources()
        
        return self.workloads
    
    def _process_namespace(self, namespace: str, resources: List[Dict[str, Any]]):
        """
        Process resources within a namespace to create workloads.
        
        Args:
            namespace: Namespace name
            resources: Resources in the namespace
        """
        # Step 3: Find workload seeds
        workload_seeds = []
        other_resources = []
        
        for resource in resources:
            if resource['kind'] in {'Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Pod'}:
                workload_seeds.append(resource)
            else:
                other_resources.append(resource)
        
        # Step 4-8: Create workloads and attach resources
        for seed in workload_seeds:
            workload_id = f"{namespace}/{seed['kind']}/{seed['name']}"
            workload = self._create_workload(seed, workload_id)
            
            # Attach related resources
            self._attach_services(workload, other_resources)
            self._attach_ingress(workload, other_resources)
            self._attach_config_and_secrets(workload, other_resources)
            self._attach_service_account(workload, other_resources)
            
            self.workloads[workload_id] = workload
    
    def _create_workload(self, seed: Dict[str, Any], workload_id: str) -> Dict[str, Any]:
        """
        Create a new workload from a seed resource.
        
        Args:
            seed: Workload seed resource
            workload_id: Unique workload identifier
            
        Returns:
            New workload dictionary
        """
        workload = {
            'id': workload_id,
            'namespace': seed['namespace'],
            'seed': {
                'kind': seed['kind'],
                'name': seed['name']
            },
            'selectors': seed.get('pod_template', {}).get('labels', {}),
            'services': [],
            'ingress': [],
            'configMaps': [],
            'secrets': [],
            'serviceAccount': None,
            'sharedRefs': []
        }
        
        return workload
    
    def _attach_services(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach Services to workload based on selector matching.
        
        Args:
            workload: Workload to attach services to
            resources: Available resources to check
        """
        workload_selectors = workload['selectors']
        
        for resource in resources:
            if resource['kind'] == 'Service':
                service_selectors = resource.get('selectors', {})
                
                # Check if service selectors are a subset of workload selectors
                if self._selectors_match(service_selectors, workload_selectors):
                    service_info = {
                        'name': resource['name'],
                        'selectors': service_selectors,
                        'ports': resource.get('ports', [])
                    }
                    workload['services'].append(service_info)
    
    def _attach_ingress(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach Ingress resources to workload based on service backend.
        
        Args:
            workload: Workload to attach ingress to
            resources: Available resources to check
        """
        workload_service_names = {service['name'] for service in workload['services']}
        
        for resource in resources:
            if resource['kind'] == 'Ingress':
                backend_services = resource.get('backend_services', [])
                
                # Check if any backend service is in this workload
                if any(service_name in workload_service_names for service_name in backend_services):
                    ingress_info = {
                        'name': resource['name'],
                        'backend_services': backend_services
                    }
                    workload['ingress'].append(ingress_info)
    
    def _attach_config_and_secrets(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach ConfigMaps and Secrets directly referenced by the workload.
        
        Args:
            workload: Workload to attach configs to
            resources: Available resources to check
        """
        pod_template = None
        for resource in resources:
            if (resource['kind'] in {'Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Pod'} and
                resource['name'] == workload['seed']['name']):
                pod_template = resource.get('pod_template', {})
                break
        
        if not pod_template:
            return
        
        # Extract referenced ConfigMaps and Secrets
        referenced_configs = set()
        referenced_secrets = set()
        
        # Check volumes
        for volume in pod_template.get('volumes', []):
            if 'configMap' in volume:
                referenced_configs.add(volume['configMap']['name'])
            elif 'secret' in volume:
                referenced_secrets.add(volume['secret']['secretName'])
        
        # Check environment variables
        for container in pod_template.get('containers', []) + pod_template.get('initContainers', []):
            for env in container.get('env', []):
                if 'valueFrom' in env:
                    value_from = env['valueFrom']
                    if 'configMapKeyRef' in value_from:
                        referenced_configs.add(value_from['configMapKeyRef']['name'])
                    elif 'secretKeyRef' in value_from:
                        referenced_secrets.add(value_from['secretKeyRef']['name'])
            
            for env_from in container.get('envFrom', []):
                if 'configMapRef' in env_from:
                    referenced_configs.add(env_from['configMapRef']['name'])
                elif 'secretRef' in env_from:
                    referenced_secrets.add(env_from['secretRef']['name'])
        
        # Attach referenced resources
        for resource in resources:
            if resource['kind'] == 'ConfigMap' and resource['name'] in referenced_configs:
                workload['configMaps'].append({
                    'name': resource['name'],
                    'data_keys': list(resource.get('raw_resource', {}).get('data', {}).keys())
                })
            
            elif resource['kind'] == 'Secret' and resource['name'] in referenced_secrets:
                workload['secrets'].append({
                    'name': resource['name'],
                    'type': resource.get('raw_resource', {}).get('type', 'Opaque')
                })
    
    def _attach_service_account(self, workload: Dict[str, Any], resources: List[Dict[str, Any]]):
        """
        Attach ServiceAccount if specified in the workload.
        
        Args:
            workload: Workload to attach service account to
            resources: Available resources to check
        """
        service_account_name = None
        for resource in resources:
            if (resource['kind'] in {'Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Pod'} and
                resource['name'] == workload['seed']['name']):
                service_account_name = resource.get('service_account')
                break
        
        if service_account_name:
            for resource in resources:
                if (resource['kind'] == 'ServiceAccount' and 
                    resource['name'] == service_account_name):
                    workload['serviceAccount'] = {
                        'name': resource['name'],
                        'automountServiceAccountToken': resource.get('raw_resource', {}).get('automountServiceAccountToken', True)
                    }
                    break
    
    def _selectors_match(self, service_selectors: Dict[str, str], workload_selectors: Dict[str, str]) -> bool:
        """
        Check if service selectors are a subset of workload selectors.
        
        Args:
            service_selectors: Service selector labels
            workload_selectors: Workload pod template labels
            
        Returns:
            True if selectors match, False otherwise
        """
        if not service_selectors:
            return False
        
        for key, value in service_selectors.items():
            if key not in workload_selectors or workload_selectors[key] != value:
                return False
        
        return True
    
    def _mark_shared_resources(self):
        """
        Mark resources that are shared across multiple workloads.
        """
        # Track resource usage across workloads
        resource_usage = defaultdict(list)
        
        for workload_id, workload in self.workloads.items():
            # Track services
            for service in workload['services']:
                resource_usage[f"Service:{service['name']}"].append(workload_id)
            
            # Track ingress
            for ingress in workload['ingress']:
                resource_usage[f"Ingress:{ingress['name']}"].append(workload_id)
            
            # Track config maps
            for config_map in workload['configMaps']:
                resource_usage[f"ConfigMap:{config_map['name']}"].append(workload_id)
            
            # Track secrets
            for secret in workload['secrets']:
                resource_usage[f"Secret:{secret['name']}"].append(workload_id)
        
        # Mark shared resources
        for resource_key, workload_ids in resource_usage.items():
            if len(workload_ids) > 1:
                self.shared_resources.add(resource_key)
                
                # Add shared flag to all workloads that use this resource
                for workload_id in workload_ids:
                    self.workloads[workload_id]['sharedRefs'].append(resource_key)


class K8sAnalyzer:
    """
    Analyzes Kubernetes resource files and creates workload groupings.
    
    This analyzer follows the v1 workload grouping logic:
    1. Groups resources by namespace
    2. Identifies workload seeds (Deployment, StatefulSet, etc.)
    3. Attaches related resources (Services, Ingress, ConfigMaps, etc.)
    4. Marks shared resources across workloads
    """
    
    def __init__(self, k8s_paths: List[str], output_dir: str, llm_config: dict = None):
        """
        Initialize the K8s analyzer.
        
        Args:
            k8s_paths: List of directories containing K8s resource files
            output_dir: Directory to store analysis results
            llm_config: LLM configuration for analysis
        """
        self.k8s_paths = [Path(path) for path in k8s_paths]
        self.output_dir = Path(output_dir)
        self.llm_config = llm_config
        
        # Initialize components
        self.parser = K8sResourceParser()
        self.grouper = WorkloadGrouper()
        
        # Analysis results
        self.workloads = {}
        self.vectors = []
        self.metadata = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive K8s resource analysis.
        
        Returns:
            Dictionary containing analysis results and metadata
        """
        logger.info("Starting K8s resource analysis")
        
        try:
            # Step 1: Find all K8s resource files
            resource_files = self._find_resource_files()
            logger.info(f"Found {len(resource_files)} K8s resource files")
            
            # Step 2: Parse resources
            resources = self.parser.parse_resources(resource_files)
            logger.info(f"Parsed {len(resources)} K8s resources")
            
            # Step 3: Group into workloads
            self.workloads = self.grouper.group_resources(resources)
            logger.info(f"Created {len(self.workloads)} workload groupings")
            
            # Step 4: Create FAISS index and metadata
            if self.workloads:
                self._create_indices()
            
            # Step 5: Save analysis results
            self._save_analysis_results()
            
            logger.info("K8s analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during K8s analysis: {e}")
            raise
        
        return {
            "workloads": self.workloads,
            "vectors_created": len(self.vectors),
            "metadata_entries": len(self.metadata)
        }
    
    def _find_resource_files(self) -> List[str]:
        """
        Find all K8s resource files in the specified directories.
        
        Returns:
            List of file paths to K8s resource files
        """
        resource_files = []
        k8s_extensions = {'.yaml', '.yml', '.json'}
        
        for k8s_path in self.k8s_paths:
            if not k8s_path.exists():
                logger.warning(f"K8s path does not exist: {k8s_path}")
                continue
            
            if k8s_path.is_file():
                if k8s_path.suffix in k8s_extensions:
                    resource_files.append(str(k8s_path))
            else:
                # Recursively search directories
                for file_path in k8s_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix in k8s_extensions:
                        resource_files.append(str(file_path))
        
        return resource_files
    
    def _create_indices(self):
        """
        Create FAISS indices and metadata for workload analysis.
        """
        # Convert workloads to text for embedding
        workload_texts = []
        
        for workload_id, workload in self.workloads.items():
            # Create a text representation of the workload
            workload_text = self._workload_to_text(workload_id, workload)
            workload_texts.append(workload_text)
            
            # Store metadata
            self.metadata.append({
                'source_file': f"workload_{workload_id}",
                'content': workload_text,
                'summary': f"K8s workload: {workload_id}",
                'workload_id': workload_id,
                'workload_data': workload
            })
        
        # Generate embeddings
        if workload_texts:
            embeddings = local_embedder.embed_chunks(workload_texts)
            index = faiss_index.build_faiss_index(embeddings)
            
            # Save index
            index_path = self.output_dir / "k8s_index.faiss"
            faiss_index.save_index(index, index_path)
            
            # Store vectors for metadata
            self.vectors = embeddings.tolist()
    
    def _workload_to_text(self, workload_id: str, workload: Dict[str, Any]) -> str:
        """
        Convert workload data to text representation for embedding.
        
        Args:
            workload_id: Workload identifier
            workload: Workload data
            
        Returns:
            Text representation of the workload
        """
        lines = [
            f"Workload: {workload_id}",
            f"Namespace: {workload['namespace']}",
            f"Seed: {workload['seed']['kind']} {workload['seed']['name']}",
            f"Selectors: {workload['selectors']}",
            ""
        ]
        
        if workload['services']:
            lines.append("Services:")
            for service in workload['services']:
                lines.append(f"  - {service['name']}: {service['selectors']}")
            lines.append("")
        
        if workload['ingress']:
            lines.append("Ingress:")
            for ingress in workload['ingress']:
                lines.append(f"  - {ingress['name']}: {ingress['backend_services']}")
            lines.append("")
        
        if workload['configMaps']:
            lines.append("ConfigMaps:")
            for config_map in workload['configMaps']:
                lines.append(f"  - {config_map['name']}: {config_map['data_keys']}")
            lines.append("")
        
        if workload['secrets']:
            lines.append("Secrets:")
            for secret in workload['secrets']:
                lines.append(f"  - {secret['name']}: {secret['type']}")
            lines.append("")
        
        if workload['serviceAccount']:
            lines.append(f"ServiceAccount: {workload['serviceAccount']['name']}")
            lines.append("")
        
        if workload['sharedRefs']:
            lines.append("Shared Resources:")
            for shared_ref in workload['sharedRefs']:
                lines.append(f"  - {shared_ref}")
        
        return "\n".join(lines)
    
    def _save_analysis_results(self):
        """
        Save analysis results to output directory.
        """
        # Save workload data
        workloads_path = self.output_dir / "k8s_workloads.json"
        
        # Generate metadata for this operation
        if self.llm_config:
            from maposcal import settings
            provider_config = settings.LLM_PROVIDERS[self.llm_config["provider"]]
            metadata = generate_metadata(
                model=self.llm_config["model"],
                provider=self.llm_config["provider"],
                base_url=provider_config["base_url"],
                command="k8s_process",
            )
            workloads_with_metadata = inject_metadata_into_json(
                {"workloads": self.workloads}, metadata
            )
        else:
            workloads_with_metadata = {"workloads": self.workloads}
        
        with open(workloads_path, 'w') as f:
            json.dump(workloads_with_metadata, f, indent=2)
        
        # Save metadata
        if self.metadata:
            meta_path = self.output_dir / "k8s_meta.json"
            meta_store.save_metadata(self.metadata, meta_path)
        
        logger.info(f"Analysis results saved to {self.output_dir}")
