"""
Workload grouper for MapOSCAL.

This module provides functionality to group related Kubernetes resources
into logical workload units for OSCAL component generation.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from .manifest_processor import WorkloadInfo, ServiceInfo, ConfigMapInfo, SecretInfo, ContainerInfo


@dataclass
class WorkloadGroup:
    """Represents a group of related Kubernetes resources."""
    
    name: str
    namespace: str
    primary_workload: WorkloadInfo
    related_services: List[ServiceInfo] = None
    related_config_maps: List[ConfigMapInfo] = None
    related_secrets: List[SecretInfo] = None
    related_resources: List[Any] = None
    container_images: List[str] = None
    resource_types: List[str] = None
    
    def __post_init__(self):
        if self.related_services is None:
            self.related_services = []
        if self.related_config_maps is None:
            self.related_config_maps = []
        if self.related_secrets is None:
            self.related_secrets = []
        if self.related_resources is None:
            self.related_resources = []
        if self.container_images is None:
            self.container_images = []
        if self.resource_types is None:
            self.resource_types = []


@dataclass
class NamespacePolicy:
    """Represents namespace-level policies and configurations."""
    
    namespace: str
    network_policies: List[Dict[str, Any]] = None
    pod_security_standards: List[str] = None
    resource_quotas: List[Dict[str, Any]] = None
    limit_ranges: List[Dict[str, Any]] = None
    other_policies: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.network_policies is None:
            self.network_policies = []
        if self.pod_security_standards is None:
            self.pod_security_standards = []
        if self.resource_quotas is None:
            self.resource_quotas = []
        if self.limit_ranges is None:
            self.limit_ranges = []
        if self.other_policies is None:
            self.other_policies = []


class WorkloadGrouper:
    """Groups related Kubernetes resources into logical workload units."""
    
    def __init__(self):
        """Initialize the workload grouper."""
        self.workload_groups: List[WorkloadGroup] = []
        self.namespace_policies: Dict[str, NamespacePolicy] = {}
        self.standalone_resources: List[Any] = []
    
    def group_resources(self, processed_manifests: Dict[str, Any]) -> Dict[str, Any]:
        """Group processed manifests into logical workload units.
        
        Args:
            processed_manifests: Output from ManifestProcessor.process_manifests()
            
        Returns:
            Dictionary containing grouped resources and policies
        """
        workloads = processed_manifests.get('workloads', [])
        services = processed_manifests.get('services', [])
        config_maps = processed_manifests.get('config_maps', [])
        secrets = processed_manifests.get('secrets', [])
        other_resources = processed_manifests.get('other_resources', [])
        
        # Reset state
        self.workload_groups = []
        self.namespace_policies = {}
        self.standalone_resources = []
        
        # Group workloads with related resources
        for workload in workloads:
            self._create_workload_group(workload, services, config_maps, secrets)
        
        # Process namespace policies
        self._process_namespace_policies(other_resources)
        
        # Identify standalone resources
        self._identify_standalone_resources(processed_manifests)
        
        return {
            "workload_groups": self.workload_groups,
            "namespace_policies": self.namespace_policies,
            "standalone_resources": self.standalone_resources,
            "summary": self._generate_grouping_summary()
        }
    
    def _create_workload_group(self, workload: WorkloadInfo, services: List[ServiceInfo], 
                              config_maps: List[ConfigMapInfo], secrets: List[SecretInfo]) -> None:
        """Create a workload group for a specific workload.
        
        Args:
            workload: Primary workload to group
            services: List of all services
            config_maps: List of all config maps
            secrets: List of all secrets
        """
        # Find related services
        related_services = self._find_related_services(workload, services)
        
        # Find related config maps and secrets
        related_config_maps = self._find_related_config_maps(workload, config_maps)
        related_secrets = self._find_related_secrets(workload, secrets)
        
        # Extract container images
        container_images = self._extract_container_images(workload)
        
        # Determine resource types
        resource_types = [workload.kind]
        
        # Create workload group
        group = WorkloadGroup(
            name=workload.name,
            namespace=workload.namespace,
            primary_workload=workload,
            related_services=related_services,
            related_config_maps=related_config_maps,
            related_secrets=related_secrets,
            container_images=container_images,
            resource_types=resource_types
        )
        
        self.workload_groups.append(group)
    
    def _find_related_services(self, workload: WorkloadInfo, services: List[ServiceInfo]) -> List[ServiceInfo]:
        """Find services related to a workload.
        
        Args:
            workload: Workload to find services for
            services: List of all services
            
        Returns:
            List of related services
        """
        related_services = []
        
        for service in services:
            if service.namespace != workload.namespace:
                continue
            
            # Check if service selector matches workload labels
            if self._service_matches_workload(service, workload):
                related_services.append(service)
        
        return related_services
    
    def _service_matches_workload(self, service: ServiceInfo, workload: WorkloadInfo) -> bool:
        """Check if a service selector matches a workload.
        
        Args:
            service: Service to check
            workload: Workload to check against
            
        Returns:
            True if service matches workload
        """
        if not service.selector:
            return False
        
        # Get workload labels from metadata
        workload_labels = workload.raw_manifest.get('metadata', {}).get('labels', {})
        
        # Check if all service selector key-value pairs match workload labels
        for key, value in service.selector.items():
            if key not in workload_labels or workload_labels[key] != value:
                return False
        
        return True
    
    def _find_related_config_maps(self, workload: WorkloadInfo, config_maps: List[ConfigMapInfo]) -> List[ConfigMapInfo]:
        """Find config maps related to a workload.
        
        Args:
            workload: Workload to find config maps for
            config_maps: List of all config maps
            
        Returns:
            List of related config maps
        """
        related_config_maps = []
        
        for config_map in config_maps:
            if config_map.namespace != workload.namespace:
                continue
            
            # Check if config map is referenced in workload volumes or env vars
            if self._config_map_referenced_in_workload(config_map, workload):
                related_config_maps.append(config_map)
        
        return related_config_maps
    
    def _config_map_referenced_in_workload(self, config_map: ConfigMapInfo, workload: WorkloadInfo) -> bool:
        """Check if a config map is referenced in a workload.
        
        Args:
            config_map: Config map to check
            workload: Workload to check against
            
        Returns:
            True if config map is referenced
        """
        # Check volumes
        for volume in workload.volumes:
            if volume.get('configMap', {}).get('name') == config_map.name:
                return True
        
        # Check environment variables
        for container in workload.containers + workload.init_containers:
            for env_var in container.env:
                if env_var.get('valueFrom', {}).get('configMapKeyRef', {}).get('name') == config_map.name:
                    return True
        
        return False
    
    def _find_related_secrets(self, workload: WorkloadInfo, secrets: List[SecretInfo]) -> List[SecretInfo]:
        """Find secrets related to a workload.
        
        Args:
            workload: Workload to find secrets for
            secrets: List of all secrets
            
        Returns:
            List of related secrets
        """
        related_secrets = []
        
        for secret in secrets:
            if secret.namespace != workload.namespace:
                continue
            
            # Check if secret is referenced in workload volumes or env vars
            if self._secret_referenced_in_workload(secret, workload):
                related_secrets.append(secret)
        
        return related_secrets
    
    def _secret_referenced_in_workload(self, secret: SecretInfo, workload: WorkloadInfo) -> bool:
        """Check if a secret is referenced in a workload.
        
        Args:
            secret: Secret to check
            workload: Workload to check against
            
        Returns:
            True if secret is referenced
        """
        # Check volumes
        for volume in workload.volumes:
            if volume.get('secret', {}).get('secretName') == secret.name:
                return True
        
        # Check environment variables
        for container in workload.containers + workload.init_containers:
            for env_var in container.env:
                if env_var.get('valueFrom', {}).get('secretKeyRef', {}).get('name') == secret.name:
                    return True
        
        return False
    
    def _extract_container_images(self, workload: WorkloadInfo) -> List[str]:
        """Extract container images from a workload.
        
        Args:
            workload: Workload to extract images from
            
        Returns:
            List of container image references
        """
        images = set()
        
        for container in workload.containers + workload.init_containers:
            if container.image:
                images.add(container.image)
        
        return list(images)
    
    def _process_namespace_policies(self, other_resources: List[Any]) -> None:
        """Process namespace-level policies and configurations.
        
        Args:
            other_resources: List of other resources to check for policies
        """
        # This is a simplified implementation
        # In a real implementation, you'd parse NetworkPolicy, PodSecurityPolicy, etc.
        pass
    
    def _identify_standalone_resources(self, processed_manifests: Dict[str, Any]) -> None:
        """Identify resources that don't belong to any workload group.
        
        Args:
            processed_manifests: Output from ManifestProcessor.process_manifests()
        """
        # Find resources that aren't part of any workload group
        all_resources = set()
        grouped_resources = set()
        
        # Add all resources to the set
        for group in self.workload_groups:
            all_resources.add(f"{group.namespace}/{group.name}")
            for service in group.related_services:
                all_resources.add(f"{service.namespace}/{service.name}")
            for config_map in group.related_config_maps:
                all_resources.add(f"{config_map.namespace}/{config_map.name}")
            for secret in group.related_secrets:
                all_resources.add(f"{secret.namespace}/{secret.name}")
        
        # This is a simplified approach - in practice you'd need more sophisticated logic
        pass
    
    def _generate_grouping_summary(self) -> Dict[str, Any]:
        """Generate a summary of the grouping results.
        
        Returns:
            Summary dictionary with grouping statistics
        """
        total_images = set()
        for group in self.workload_groups:
            total_images.update(group.container_images)
        
        return {
            "total_workload_groups": len(self.workload_groups),
            "total_namespace_policies": len(self.namespace_policies),
            "total_standalone_resources": len(self.standalone_resources),
            "total_container_images": len(total_images),
            "namespaces": list(set(group.namespace for group in self.workload_groups)),
            "workload_types": {
                group.primary_workload.kind: len([g for g in self.workload_groups if g.primary_workload.kind == group.primary_workload.kind])
                for group in self.workload_groups
            }
        }
    
    def get_workload_group_by_name(self, name: str, namespace: str) -> Optional[WorkloadGroup]:
        """Get a workload group by name and namespace.
        
        Args:
            name: Name of the workload group
            namespace: Namespace of the workload group
            
        Returns:
            WorkloadGroup if found, None otherwise
        """
        for group in self.workload_groups:
            if group.name == name and group.namespace == namespace:
                return group
        return None
    
    def get_workload_groups_by_namespace(self, namespace: str) -> List[WorkloadGroup]:
        """Get all workload groups in a specific namespace.
        
        Args:
            namespace: Namespace to filter by
            
        Returns:
            List of workload groups in the namespace
        """
        return [group for group in self.workload_groups if group.namespace == namespace]
