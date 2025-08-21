"""
Kubernetes manifest processor for MapOSCAL.

This module provides functionality to process Kubernetes manifests,
extract detailed information about resources, and identify relationships
between different Kubernetes objects.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from .parser import ParsedManifest


@dataclass
class ContainerInfo:
    """Information about a container in a pod."""
    
    name: str
    image: str
    ports: List[Dict[str, Any]] = None
    env: List[Dict[str, Any]] = None
    volume_mounts: List[Dict[str, Any]] = None
    security_context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.ports is None:
            self.ports = []
        if self.env is None:
            self.env = []
        if self.volume_mounts is None:
            self.volume_mounts = []


@dataclass
class WorkloadInfo:
    """Information about a workload resource."""
    
    name: str
    namespace: str
    kind: str
    replicas: Optional[int] = None
    containers: List[ContainerInfo] = None
    init_containers: List[ContainerInfo] = None
    volumes: List[Dict[str, Any]] = None
    service_account: Optional[str] = None
    security_context: Optional[Dict[str, Any]] = None
    raw_manifest: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.containers is None:
            self.containers = []
        if self.init_containers is None:
            self.init_containers = []
        if self.volumes is None:
            self.volumes = []


@dataclass
class ServiceInfo:
    """Information about a Service resource."""
    
    name: str
    namespace: str
    type: str
    selector: Dict[str, str]
    ports: List[Dict[str, Any]]
    raw_manifest: Optional[Dict[str, Any]] = None


@dataclass
class ConfigMapInfo:
    """Information about a ConfigMap resource."""
    
    name: str
    namespace: str
    data: Dict[str, str]
    binary_data: Dict[str, str]
    raw_manifest: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.binary_data is None:
            self.binary_data = {}


@dataclass
class SecretInfo:
    """Information about a Secret resource."""
    
    name: str
    namespace: str
    type: str
    data: Dict[str, str]
    string_data: Dict[str, str]
    raw_manifest: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.string_data is None:
            self.string_data = {}


class ManifestProcessor:
    """Processor for Kubernetes manifests with detailed information extraction."""
    
    def __init__(self):
        """Initialize the manifest processor."""
        self.workloads: List[WorkloadInfo] = []
        self.services: List[ServiceInfo] = []
        self.config_maps: List[ConfigMapInfo] = []
        self.secrets: List[SecretInfo] = []
        self.other_resources: List[ParsedManifest] = []
    
    def process_manifests(self, manifests: List[ParsedManifest]) -> Dict[str, Any]:
        """Process a list of manifests and extract detailed information.
        
        Args:
            manifests: List of parsed manifests to process
            
        Returns:
            Dictionary containing processed resource information
        """
        self.workloads = []
        self.services = []
        self.config_maps = []
        self.secrets = []
        self.other_resources = []
        
        for manifest in manifests:
            self._process_single_manifest(manifest)
        
        return {
            "workloads": self.workloads,
            "services": self.services,
            "config_maps": self.config_maps,
            "secrets": self.secrets,
            "other_resources": self.other_resources,
            "summary": self._generate_summary()
        }
    
    def _process_single_manifest(self, manifest: ParsedManifest) -> None:
        """Process a single manifest and categorize it.
        
        Args:
            manifest: Manifest to process
        """
        if manifest.kind in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob']:
            self._process_workload_manifest(manifest)
        elif manifest.kind == 'Service':
            self._process_service_manifest(manifest)
        elif manifest.kind == 'ConfigMap':
            self._process_configmap_manifest(manifest)
        elif manifest.kind == 'Secret':
            self._process_secret_manifest(manifest)
        else:
            self.other_resources.append(manifest)
    
    def _process_workload_manifest(self, manifest: ParsedManifest) -> None:
        """Process a workload manifest (Deployment, StatefulSet, etc.).
        
        Args:
            manifest: Workload manifest to process
        """
        spec = manifest.spec
        if not spec:
            return
        
        # Extract pod template spec
        if manifest.kind == 'CronJob':
            template_spec = spec.get('jobTemplate', {}).get('spec', {}).get('template', {}).get('spec', {})
        elif manifest.kind in ['Deployment', 'StatefulSet', 'DaemonSet']:
            template_spec = spec.get('template', {}).get('spec', {})
        else:  # Job
            template_spec = spec.get('template', {}).get('spec', {})
        
        # Extract containers
        containers = self._extract_containers(template_spec.get('containers', []))
        init_containers = self._extract_containers(template_spec.get('initContainers', []))
        
        # Extract volumes
        volumes = template_spec.get('volumes', [])
        
        # Extract service account
        service_account = template_spec.get('serviceAccountName')
        
        # Extract security context
        security_context = template_spec.get('securityContext')
        
        workload = WorkloadInfo(
            name=manifest.name,
            namespace=manifest.namespace,
            kind=manifest.kind,
            replicas=spec.get('replicas'),
            containers=containers,
            init_containers=init_containers,
            volumes=volumes,
            service_account=service_account,
            security_context=security_context,
            raw_manifest=manifest.raw_content
        )
        
        self.workloads.append(workload)
    
    def _extract_containers(self, container_list: List[Dict[str, Any]]) -> List[ContainerInfo]:
        """Extract container information from a list of containers.
        
        Args:
            container_list: List of container specifications
            
        Returns:
            List of ContainerInfo objects
        """
        containers = []
        
        for container_spec in container_list:
            container = ContainerInfo(
                name=container_spec.get('name', ''),
                image=container_spec.get('image', ''),
                ports=container_spec.get('ports', []),
                env=container_spec.get('env', []),
                volume_mounts=container_spec.get('volumeMounts', []),
                security_context=container_spec.get('securityContext')
            )
            containers.append(container)
        
        return containers
    
    def _process_service_manifest(self, manifest: ParsedManifest) -> None:
        """Process a Service manifest.
        
        Args:
            manifest: Service manifest to process
        """
        spec = manifest.spec
        if not spec:
            return
        
        service = ServiceInfo(
            name=manifest.name,
            namespace=manifest.namespace,
            type=spec.get('type', 'ClusterIP'),
            selector=spec.get('selector', {}),
            ports=spec.get('ports', []),
            raw_manifest=manifest.raw_content
        )
        
        self.services.append(service)
    
    def _process_configmap_manifest(self, manifest: ParsedManifest) -> None:
        """Process a ConfigMap manifest.
        
        Args:
            manifest: ConfigMap manifest to process
        """
        configmap = ConfigMapInfo(
            name=manifest.name,
            namespace=manifest.namespace,
            data=manifest.raw_content.get('data', {}),
            binary_data=manifest.raw_content.get('binaryData', {}),
            raw_manifest=manifest.raw_content
        )
        
        self.config_maps.append(configmap)
    
    def _process_secret_manifest(self, manifest: ParsedManifest) -> None:
        """Process a Secret manifest.
        
        Args:
            manifest: Secret manifest to process
        """
        secret = SecretInfo(
            name=manifest.name,
            namespace=manifest.namespace,
            type=manifest.raw_content.get('type', 'Opaque'),
            data=manifest.raw_content.get('data', {}),
            string_data=manifest.raw_content.get('stringData', {}),
            raw_manifest=manifest.raw_content
        )
        
        self.secrets.append(secret)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of processed resources.
        
        Returns:
            Summary dictionary with resource counts and details
        """
        # Count container images
        all_images = set()
        for workload in self.workloads:
            for container in workload.containers + workload.init_containers:
                if container.image:
                    all_images.add(container.image)
        
        return {
            "total_workloads": len(self.workloads),
            "total_services": len(self.services),
            "total_config_maps": len(self.config_maps),
            "total_secrets": len(self.secrets),
            "total_other_resources": len(self.other_resources),
            "total_container_images": len(all_images),
            "workload_types": {
                workload.kind: len([w for w in self.workloads if w.kind == workload.kind])
                for workload in self.workloads
            },
            "namespaces": list(set(
                [w.namespace for w in self.workloads] +
                [s.namespace for s in self.services] +
                [c.namespace for c in self.config_maps] +
                [s.namespace for s in self.secrets]
            ))
        }
    
    def get_images_by_workload(self) -> Dict[str, List[str]]:
        """Get container images grouped by workload.
        
        Returns:
            Dictionary mapping workload names to lists of container images
        """
        result = {}
        
        for workload in self.workloads:
            images = []
            for container in workload.containers + workload.init_containers:
                if container.image:
                    images.append(container.image)
            result[workload.name] = images
        
        return result
    
    def find_related_resources(self, workload_name: str, namespace: str) -> Dict[str, Any]:
        """Find resources related to a specific workload.
        
        Args:
            workload_name: Name of the workload
            namespace: Namespace of the workload
            
        Returns:
            Dictionary containing related resources
        """
        # Find the workload
        workload = next((w for w in self.workloads if w.name == workload_name and w.namespace == namespace), None)
        if not workload:
            return {}
        
        # Find related services
        related_services = [
            s for s in self.services 
            if s.namespace == namespace and s.selector.get('app') == workload_name
        ]
        
        # Find related config maps and secrets (this is a simplified approach)
        # In a real implementation, you'd need to analyze volume mounts and env vars
        related_config_maps = []
        related_secrets = []
        
        return {
            "workload": workload,
            "related_services": related_services,
            "related_config_maps": related_config_maps,
            "related_secrets": related_secrets
        }
