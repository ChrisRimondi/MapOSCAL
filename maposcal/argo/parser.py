"""
Argo CD Application parser for MapOSCAL.

This module provides functionality to parse Argo CD Application resources
and extract basic information about the application and its source.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class ArgoCDApplication:
    """Represents an Argo CD Application resource."""
    
    name: str
    namespace: str
    source_path: str
    destination_namespace: str
    source_repo: Optional[str] = None
    source_target_revision: Optional[str] = None
    raw_manifest: Optional[Dict[str, Any]] = None


@dataclass
class ParsedManifest:
    """Represents a parsed Kubernetes manifest."""
    
    kind: str
    api_version: str
    name: str
    namespace: str
    metadata: Dict[str, Any]
    spec: Optional[Dict[str, Any]] = None
    raw_content: Optional[Dict[str, Any]] = None


class ArgoCDParser:
    """Parser for Argo CD Application resources and Kubernetes manifests."""
    
    def __init__(self, repo_path: str):
        """Initialize parser with repository path.
        
        Args:
            repo_path: Path to the repository containing Argo CD manifests
        """
        self.repo_path = Path(repo_path)
        self.applications: List[ArgoCDApplication] = []
        self.manifests: List[ParsedManifest] = []
        
    def parse_repository(self) -> List[ArgoCDApplication]:
        """Parse the repository for Argo CD Application resources.
        
        Returns:
            List of discovered Argo CD Applications
        """
        self.applications = []
        
        # Look for Argo CD Application resources in common locations
        search_paths = [
            self.repo_path / "manifests",
            self.repo_path / "argocd",
            self.repo_path / "deploy",
            self.repo_path / "k8s",
            self.repo_path,  # Root directory
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                self._scan_directory_for_applications(search_path)
        
        return self.applications
    
    def _scan_directory_for_applications(self, directory: Path) -> None:
        """Scan a directory for Argo CD Application resources.
        
        Args:
            directory: Directory to scan
        """
        for file_path in directory.rglob("*.yaml"):
            try:
                with open(file_path, 'r') as f:
                    content = yaml.safe_load(f)
                
                if content and isinstance(content, dict):
                    # Check if this is a list of resources
                    if content.get('kind') == 'List':
                        items = content.get('items', [])
                        for item in items:
                            if item.get('kind') == 'Application':
                                self._parse_application(item, file_path)
                    elif content.get('kind') == 'Application':
                        self._parse_application(content, file_path)
                        
            except (yaml.YAMLError, IOError) as e:
                # Log warning but continue processing
                print(f"Warning: Could not parse {file_path}: {e}")
                continue
    
    def _parse_application(self, app_data: Dict[str, Any], file_path: Path) -> None:
        """Parse an Argo CD Application resource.
        
        Args:
            app_data: Parsed YAML data for the Application
            file_path: Path to the file containing the Application
        """
        metadata = app_data.get('metadata', {})
        spec = app_data.get('spec', {})
        source = spec.get('source', {})
        destination = spec.get('destination', {})
        
        # Check if we already have an application with this name and namespace
        app_key = f"{metadata.get('name', '')}-{metadata.get('namespace', '')}"
        existing_apps = [app for app in self.applications if f"{app.name}-{app.namespace}" == app_key]
        
        if existing_apps:
            # Skip duplicate applications
            return
        
        application = ArgoCDApplication(
            name=metadata.get('name', ''),
            namespace=metadata.get('namespace', ''),
            source_path=source.get('path', ''),
            destination_namespace=destination.get('namespace', ''),
            source_repo=source.get('repoURL'),
            source_target_revision=source.get('targetRevision'),
            raw_manifest=app_data
        )
        
        self.applications.append(application)
    
    def process_application_manifests(self, application: ArgoCDApplication) -> List[ParsedManifest]:
        """Process manifests referenced by an Argo CD Application.
        
        Args:
            application: Argo CD Application to process
            
        Returns:
            List of parsed manifests
        """
        manifests = []
        
        if not application.source_path:
            return manifests
        
        # Construct the path to the manifests directory
        manifests_path = self.repo_path / application.source_path
        
        if not manifests_path.exists():
            print(f"Warning: Manifests path {manifests_path} does not exist")
            return manifests
        
        # Scan for Kubernetes manifests
        for file_path in manifests_path.rglob("*.yaml"):
            try:
                with open(file_path, 'r') as f:
                    content = yaml.safe_load(f)
                
                if content and isinstance(content, dict):
                    # Handle both single resources and Lists
                    if content.get('kind') == 'List':
                        items = content.get('items', [])
                        for item in items:
                            manifest = self._parse_manifest(item, file_path)
                            if manifest:
                                manifests.append(manifest)
                    else:
                        manifest = self._parse_manifest(content, file_path)
                        if manifest:
                            manifests.append(manifest)
                            
            except (yaml.YAMLError, IOError) as e:
                print(f"Warning: Could not parse {file_path}: {e}")
                continue
        
        return manifests
    
    def _parse_manifest(self, manifest_data: Dict[str, Any], file_path: Path) -> Optional[ParsedManifest]:
        """Parse a Kubernetes manifest.
        
        Args:
            manifest_data: Parsed YAML data for the manifest
            file_path: Path to the file containing the manifest
            
        Returns:
            Parsed manifest or None if invalid
        """
        if not manifest_data.get('kind') or not manifest_data.get('apiVersion'):
            return None
        
        metadata = manifest_data.get('metadata', {})
        
        # Determine namespace (use default if not specified)
        namespace = metadata.get('namespace', 'default')
        
        manifest = ParsedManifest(
            kind=manifest_data['kind'],
            api_version=manifest_data['apiVersion'],
            name=metadata.get('name', ''),
            namespace=namespace,
            metadata=metadata,
            spec=manifest_data.get('spec'),
            raw_content=manifest_data
        )
        
        return manifest
    
    def extract_container_images(self, manifests: List[ParsedManifest]) -> List[str]:
        """Extract container images from Kubernetes manifests.
        
        Args:
            manifests: List of parsed manifests
            
        Returns:
            List of container image references
        """
        images = set()
        
        for manifest in manifests:
            if manifest.kind in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob']:
                # Extract images from pod spec
                spec = manifest.spec
                if not spec:
                    continue
                
                # Handle different workload types
                if manifest.kind == 'CronJob':
                    template_spec = spec.get('jobTemplate', {}).get('spec', {}).get('template', {}).get('spec', {})
                elif manifest.kind in ['Deployment', 'StatefulSet', 'DaemonSet']:
                    template_spec = spec.get('template', {}).get('spec', {})
                else:  # Job
                    template_spec = spec.get('template', {}).get('spec', {})
                
                # Extract container images
                containers = template_spec.get('containers', [])
                init_containers = template_spec.get('initContainers', [])
                
                for container in containers + init_containers:
                    image = container.get('image')
                    if image:
                        images.add(image)
        
        return list(images)
    
    def get_application_summary(self) -> Dict[str, Any]:
        """Get a summary of all discovered applications and manifests.
        
        Returns:
            Summary dictionary with application and manifest counts
        """
        total_manifests = sum(len(self.process_application_manifests(app)) for app in self.applications)
        total_images = set()
        
        for app in self.applications:
            manifests = self.process_application_manifests(app)
            images = self.extract_container_images(manifests)
            total_images.update(images)
        
        return {
            "applications": len(self.applications),
            "total_manifests": total_manifests,
            "total_images": len(total_images),
            "applications_detail": [
                {
                    "name": app.name,
                    "namespace": app.namespace,
                    "source_path": app.source_path,
                    "destination_namespace": app.destination_namespace,
                    "manifests": len(self.process_application_manifests(app)),
                    "images": len(self.extract_container_images(self.process_application_manifests(app)))
                }
                for app in self.applications
            ]
        }
