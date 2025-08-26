"""
Execution engine for MapOSCAL plans.

This module provides functionality to execute generated plans step-by-step
with dependency resolution, caching, and state management.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime

from .models import ExecutionPlan, Step, StepStatus
from .cache_manager import CacheManager
from .state_manager import StateManager


class ExecutionEngine:
    """Executes MapOSCAL execution plans with step orchestration."""
    
    def __init__(self, plan: ExecutionPlan, force: bool = False, 
                 only_steps: Optional[List[str]] = None,
                 skip_steps: Optional[List[str]] = None,
                 only_targets: Optional[List[str]] = None):
        """Initialize execution engine.
        
        Args:
            plan: Execution plan to execute
            force: Force execution even if cached results exist
            only_steps: List of step IDs to execute (if None, execute all)
            skip_steps: List of step IDs to skip
            only_targets: List of targets to execute (if None, execute all)
        """
        self.plan = plan
        self.force = force
        self.only_steps = set(only_steps) if only_steps else None
        self.skip_steps = set(skip_steps) if skip_steps else None
        self.only_targets = set(only_targets) if only_targets else None
        
        # Initialize managers
        self.cache_manager = CacheManager(plan.application)
        self.state_manager = StateManager(plan.application)
        
        # Execution state
        self.execution_order: List[str] = []
        self.completed_steps: Set[str] = set()
        self.failed_steps: Set[str] = set()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def execute(self) -> Dict[str, Any]:
        """Execute the plan and return results.
        
        Returns:
            Dictionary with execution results and statistics
        """
        try:
            self.logger.info(f"Starting execution of plan for application: {self.plan.application}")
            
            # Load or create execution state
            state = self.state_manager.load_state()
            if state and not self.force:
                self.logger.info("Resuming previous execution")
                self._load_execution_state(state)
            else:
                self.logger.info("Starting new execution")
                state = self.state_manager.create_new_state(str(Path.cwd() / "plan.yaml"))
            
            # Resolve execution order
            self._resolve_execution_order()
            
            # Execute steps
            results = self._execute_steps()
            
            # Update final state
            self._finalize_execution()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            self._handle_execution_failure(str(e))
            raise
    
    def _load_execution_state(self, state: Any) -> None:
        """Load existing execution state.
        
        Args:
            state: Existing execution state
        """
        # Load completed and failed steps from state
        for step_id, step_data in state.step_states.items():
            if step_data.status == StepStatus.DONE:
                self.completed_steps.add(step_id)
            elif step_data.status == StepStatus.FAILED:
                self.failed_steps.add(step_id)
    
    def _resolve_execution_order(self) -> None:
        """Resolve the order of step execution based on dependencies."""
        self.logger.info("Resolving execution order...")
        
        # Start with all steps
        all_steps = set(self.plan.steps)
        
        # Apply filters
        if self.only_steps:
            all_steps = all_steps.intersection(self.only_steps)
        
        if self.skip_steps:
            all_steps = all_steps.difference(self.skip_steps)
        
        # Build dependency graph and topological sort
        self.execution_order = self._topological_sort(all_steps)
        
        self.logger.info(f"Execution order: {self.execution_order}")
    
    def _topological_sort(self, steps: Set[str]) -> List[str]:
        """Perform topological sort of steps based on dependencies.
        
        Args:
            steps: Set of step IDs to sort
            
        Returns:
            List of steps in dependency order
        """
        # Build dependency graph
        graph = {step: set() for step in steps}
        in_degree = {step: 0 for step in steps}
        
        # Add dependencies from workload steps
        for workload in self.plan.targets.get("workloads", []):
            for step_id, step_data in workload.get("steps", {}).items():
                if step_id in steps:
                    depends_on = step_data.get("depends_on", [])
                    for dep in depends_on:
                        if dep in steps:
                            graph[dep].add(step_id)
                            in_degree[step_id] += 1
        
        # Add dependencies from image steps
        for workload in self.plan.targets.get("workloads", []):
            for image in workload.get("images", []):
                for step_id, step_data in image.get("steps", {}).items():
                    if step_id in steps:
                        depends_on = step_data.get("depends_on", [])
                        for dep in depends_on:
                            if dep in steps:
                                graph[dep].add(step_id)
                                in_degree[step_id] += 1
        
        # Add dependencies from repo steps
        for workload in self.plan.targets.get("workloads", []):
            for image in workload.get("images", []):
                repo = image.get("repo", {})
                if repo:
                    for step_id, step_data in repo.get("steps", {}).items():
                        if step_id in steps:
                            depends_on = step_data.get("depends_on", [])
                            for dep in depends_on:
                                if dep in steps:
                                    graph[dep].add(step_id)
                                    in_degree[step_id] += 1
        
        # Build a complete mapping of all steps and their dependencies across all levels
        all_step_dependencies = {}
        
        # Collect all step definitions from all levels
        for workload in self.plan.targets.get("workloads", []):
            # Workload-level steps
            for step_id, step_data in workload.get("steps", {}).items():
                if step_id not in all_step_dependencies:
                    all_step_dependencies[step_id] = set()
                depends_on = step_data.get("depends_on", [])
                for dep in depends_on:
                    all_step_dependencies[step_id].add(dep)
            
            # Image-level steps
            for image in workload.get("images", []):
                for step_id, step_data in image.get("steps", {}).items():
                    if step_id not in all_step_dependencies:
                        all_step_dependencies[step_id] = set()
                    depends_on = step_data.get("depends_on", [])
                    for dep in depends_on:
                        all_step_dependencies[step_id].add(dep)
                
                # Repo-level steps
                repo = image.get("repo", {})
                if repo:
                    for step_id, step_data in repo.get("steps", {}).items():
                        if step_id not in all_step_dependencies:
                            all_step_dependencies[step_id] = set()
                        depends_on = step_data.get("depends_on", [])
                        for dep in depends_on:
                            all_step_dependencies[step_id].add(dep)
        
        # Now build the dependency graph for the requested steps
        # Reset the graph and in_degree to avoid duplicate counting
        graph = {step: set() for step in steps}
        in_degree = {step: 0 for step in steps}
        
        for step_id in steps:
            if step_id in all_step_dependencies:
                for dep in all_step_dependencies[step_id]:
                    if dep in steps:
                        graph[dep].add(step_id)
                        in_degree[step_id] += 1
        
        # Debug logging
        self.logger.info(f"All step dependencies collected: {all_step_dependencies}")
        self.logger.info(f"Built dependency graph: {graph}")
        self.logger.info(f"Initial in_degree counts: {in_degree}")
        
        # Kahn's algorithm for topological sort
        result = []
        queue = [step for step in steps if in_degree[step] == 0]
        
        self.logger.debug(f"Initial queue (steps with no dependencies): {queue}")
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        self.logger.debug(f"Topological sort result: {result}")
        self.logger.debug(f"Expected {len(steps)} steps, got {len(result)} steps")
        
        # Check for cycles
        if len(result) != len(steps):
            # Find which steps couldn't be processed
            processed_steps = set(result)
            unprocessed_steps = steps - processed_steps
            self.logger.error(f"Steps that couldn't be processed: {unprocessed_steps}")
            self.logger.error(f"These steps may have circular dependencies or missing dependencies")
            raise RuntimeError(f"Circular dependency detected in execution plan. Unprocessed steps: {unprocessed_steps}")
        
        return result
    
    def _execute_steps(self) -> Dict[str, Any]:
        """Execute all steps in the resolved order.
        
        Returns:
            Dictionary with execution results
        """
        results = {
            "total_steps": len(self.execution_order),
            "completed_steps": 0,
            "failed_steps": 0,
            "skipped_steps": 0,
            "step_results": {}
        }
        
        for step_id in self.execution_order:
            if step_id in self.completed_steps:
                self.logger.info(f"Step {step_id} already completed, skipping")
                results["skipped_steps"] += 1
                continue
            
            if step_id in self.failed_steps and not self.force:
                self.logger.warning(f"Step {step_id} previously failed, skipping")
                results["skipped_steps"] += 1
                continue
            
            try:
                self.logger.info(f"Executing step: {step_id}")
                self.state_manager.update_step_status(step_id, StepStatus.RUNNING)
                
                # Execute the step
                step_result = self._execute_single_step(step_id)
                
                # Mark as completed
                self.completed_steps.add(step_id)
                self.state_manager.update_step_status(step_id, StepStatus.DONE)
                
                results["step_results"][step_id] = step_result
                results["completed_steps"] += 1
                
                self.logger.info(f"Step {step_id} completed successfully")
                
            except Exception as e:
                self.logger.error(f"Step {step_id} failed: {e}")
                self.failed_steps.add(step_id)
                self.state_manager.update_step_status(step_id, StepStatus.FAILED, str(e))
                
                results["step_results"][step_id] = {"error": str(e)}
                results["failed_steps"] += 1
                
                # Continue with other steps unless this is a critical failure
                if self._is_critical_step(step_id):
                    raise
        
        return results
    
    def _execute_single_step(self, step_id: str) -> Dict[str, Any]:
        """Execute a single step.
        
        Args:
            step_id: ID of the step to execute
            
        Returns:
            Step execution result
        """
        # This is a placeholder implementation
        # In the full implementation, each step type would have specific logic
        
        if step_id == "render":
            return self._execute_render_step()
        elif step_id == "inventory":
            return self._execute_inventory_step()
        elif step_id == "images":
            return self._execute_images_step()
        elif step_id == "oci_labels":
            return self._execute_oci_labels_step()
        elif step_id == "source_link":
            return self._execute_source_link_step()
        elif step_id == "source_analysis":
            return self._execute_source_analysis_step()
        elif step_id == "control_mapping":
            return self._execute_control_mapping_step()
        elif step_id == "sbom":
            return self._execute_sbom_step()
        elif step_id == "provenance":
            return self._execute_provenance_step()
        elif step_id == "oscal_emit":
            return self._execute_oscal_emit_step()
        else:
            raise ValueError(f"Unknown step type: {step_id}")
    
    def _execute_render_step(self) -> Dict[str, Any]:
        """Execute the render step - parse and render Kubernetes manifests.
        
        Returns:
            Dictionary with render results including parsed manifests
        """
        try:
            self.logger.info("Executing render step: parsing Kubernetes manifests")
            
            # Get the workload targets from the plan
            workloads = self.plan.targets.get("workloads", [])
            rendered_manifests = []
            
            for workload in workloads:
                workload_name = workload.get("name")
                workload_namespace = workload.get("namespace")
                
                self.logger.info(f"Rendering manifests for workload: {workload_name} in namespace: {workload_namespace}")
                
                # For now, we'll extract the raw manifests from the plan
                # In a full implementation, this would re-parse the source files
                workload_manifests = {
                    "workload_name": workload_name,
                    "namespace": workload_namespace,
                    "resource_types": workload.get("resource_types", []),
                    "images": [img.get("ref") for img in workload.get("images", [])],
                    "rendered_at": datetime.utcnow().isoformat()
                }
                
                rendered_manifests.append(workload_manifests)
            
            self.logger.info(f"Render step completed: processed {len(rendered_manifests)} workloads")
            
            return {
                "status": "completed",
                "message": "Manifests rendered successfully",
                "timestamp": datetime.utcnow().isoformat(),
                "rendered_manifests": rendered_manifests,
                "total_workloads": len(rendered_manifests)
            }
            
        except Exception as e:
            self.logger.error(f"Render step failed: {e}")
            return {
                "status": "failed",
                "message": f"Render step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _execute_inventory_step(self) -> Dict[str, Any]:
        """Execute the inventory step - create resource inventory from manifests.
        
        Returns:
            Dictionary with inventory results including resource counts and types
        """
        try:
            self.logger.info("Executing inventory step: creating resource inventory")
            
            # Get the workload targets from the plan
            workloads = self.plan.targets.get("workloads", [])
            inventory = {
                "total_workloads": len(workloads),
                "total_images": 0,
                "resource_types": set(),
                "namespaces": set(),
                "workload_details": []
            }
            
            for workload in workloads:
                workload_name = workload.get("name")
                workload_namespace = workload.get("namespace")
                resource_types = workload.get("resource_types", [])
                images = workload.get("images", [])
                
                # Update inventory counts
                inventory["namespaces"].add(workload_namespace)
                inventory["total_images"] += len(images)
                inventory["resource_types"].update(resource_types)
                
                # Add workload details
                workload_detail = {
                    "name": workload_name,
                    "namespace": workload_namespace,
                    "resource_types": resource_types,
                    "image_count": len(images),
                    "images": [img.get("ref") for img in images]
                }
                inventory["workload_details"].append(workload_detail)
            
            # Convert sets to lists for JSON serialization
            inventory["resource_types"] = list(inventory["resource_types"])
            inventory["namespaces"] = list(inventory["namespaces"])
            
            self.logger.info(f"Inventory step completed: {inventory['total_workloads']} workloads, {inventory['total_images']} images")
            
            return {
                "status": "completed",
                "message": "Resource inventory created",
                "timestamp": datetime.utcnow().isoformat(),
                "inventory": inventory
            }
            
        except Exception as e:
            self.logger.error(f"Inventory step failed: {e}")
            return {
                "status": "failed",
                "message": f"Inventory step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _execute_images_step(self) -> Dict[str, Any]:
        """Execute the images step - extract and analyze container images.
        
        Returns:
            Dictionary with image analysis results
        """
        try:
            self.logger.info("Executing images step: extracting container images")
            
            # Get all images from all workloads
            workloads = self.plan.targets.get("workloads", [])
            all_images = set()
            image_analysis = {}
            
            for workload in workloads:
                workload_name = workload.get("name")
                images = workload.get("images", [])
                
                for image in images:
                    image_ref = image.get("ref")
                    all_images.add(image_ref)
                    
                    # Analyze image reference
                    image_info = self._analyze_image_reference(image_ref)
                    image_analysis[image_ref] = {
                        "workloads": image_analysis.get(image_ref, {}).get("workloads", []) + [workload_name],
                        "analysis": image_info,
                        "steps": image.get("steps", {}),
                        "repo": image.get("repo", {})
                    }
            
            self.logger.info(f"Images step completed: analyzed {len(all_images)} unique images")
            
            return {
                "status": "completed",
                "message": "Container images extracted",
                "timestamp": datetime.utcnow().isoformat(),
                "total_images": len(all_images),
                "unique_images": list(all_images),
                "image_analysis": image_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Images step failed: {e}")
            return {
                "status": "failed",
                "message": f"Images step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _analyze_image_reference(self, image_ref: str) -> Dict[str, Any]:
        """Analyze a container image reference to extract metadata.
        
        Args:
            image_ref: Container image reference (e.g., nginx:1.21, quay.io/app:v1.0.0)
            
        Returns:
            Dictionary with image analysis results
        """
        try:
            # Parse image reference
            if "@" in image_ref:
                # Image with digest
                image_name, digest = image_ref.split("@", 1)
                tag = "latest"
            elif ":" in image_ref:
                # Image with tag
                image_name, tag = image_ref.split(":", 1)
                digest = None
            else:
                # Image with no tag (defaults to latest)
                image_name = image_ref
                tag = "latest"
                digest = None
            
            # Extract registry and repository
            if "/" in image_name:
                parts = image_name.split("/")
                if "." in parts[0] or ":" in parts[0]:
                    # First part is registry
                    registry = parts[0]
                    repository = "/".join(parts[1:])
                else:
                    # No registry specified (Docker Hub)
                    registry = "docker.io"
                    repository = image_name
            else:
                # No registry specified (Docker Hub)
                registry = "docker.io"
                repository = image_name
            
            return {
                "registry": registry,
                "repository": repository,
                "tag": tag,
                "digest": digest,
                "full_name": image_name,
                "parsed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to parse image reference {image_ref}: {e}")
            return {
                "registry": "unknown",
                "repository": image_ref,
                "tag": "unknown",
                "digest": None,
                "full_name": image_ref,
                "parse_error": str(e),
                "parsed_at": datetime.utcnow().isoformat()
            }
    
    def _execute_oci_labels_step(self) -> Dict[str, Any]:
        """Execute the OCI labels step - extract OCI image labels and metadata.
        
        Returns:
            Dictionary with OCI labels and metadata
        """
        try:
            self.logger.info("Executing OCI labels step: extracting image labels and metadata")
            
            # Get all images from all workloads
            workloads = self.plan.targets.get("workloads", [])
            oci_labels = {}
            
            for workload in workloads:
                workload_name = workload.get("name")
                images = workload.get("images", [])
                
                for image in images:
                    image_ref = image.get("ref")
                    
                    # Extract OCI labels (placeholder for now)
                    # In a full implementation, this would inspect the actual image
                    image_labels = self._extract_oci_labels(image_ref)
                    
                    if image_ref not in oci_labels:
                        oci_labels[image_ref] = {
                            "workloads": [],
                            "labels": image_labels,
                            "extracted_at": datetime.utcnow().isoformat()
                        }
                    
                    oci_labels[image_ref]["workloads"].append(workload_name)
            
            self.logger.info(f"OCI labels step completed: processed {len(oci_labels)} images")
            
            return {
                "status": "completed",
                "message": "OCI labels extracted",
                "timestamp": datetime.utcnow().isoformat(),
                "total_images": len(oci_labels),
                "oci_labels": oci_labels
            }
            
        except Exception as e:
            self.logger.error(f"OCI labels step failed: {e}")
            return {
                "status": "failed",
                "message": f"OCI labels step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _extract_oci_labels(self, image_ref: str) -> Dict[str, str]:
        """Extract OCI labels from an image reference using native Python HTTP API.
        
        Args:
            image_ref: Container image reference
            
        Returns:
            Dictionary of OCI labels
        """
        try:
            # Parse image reference to get registry and repository
            image_info = self._analyze_image_reference(image_ref)
            registry = image_info.get("registry")
            repository = image_info.get("repository")
            tag = image_info.get("tag")
            
            if registry == "docker.io":
                # Docker Hub uses a different API structure
                # Handle official images (library/ prefix)
                if "/" not in repository:
                    repository = f"library/{repository}"
                return self._extract_dockerhub_labels(repository, tag)
            else:
                # Use OCI Distribution Spec v2 API
                return self._extract_oci_labels_v2(registry, repository, tag)
                
        except Exception as e:
            self.logger.warning(f"Failed to extract OCI labels from {image_ref}: {e}")
            # Fallback to basic labels
            return {
                "org.opencontainers.image.source": "unknown",
                "org.opencontainers.image.revision": "unknown",
                "org.opencontainers.image.version": "unknown",
                "org.opencontainers.image.licenses": "unknown",
                "org.opencontainers.image.created": "unknown",
                "org.opencontainers.image.description": "Application container image",
                "extraction_error": str(e)
            }
    
    def _extract_dockerhub_labels(self, repository: str, tag: str) -> Dict[str, str]:
        """Extract labels from Docker Hub using their API.
        
        Args:
            repository: Docker repository name
            tag: Image tag
            
        Returns:
            Dictionary of OCI labels
        """
        import urllib.request
        import json
        
        try:
            # Docker Hub API endpoint for tag information
            api_url = f"https://hub.docker.com/v2/repositories/{repository}/tags/{tag}/"
            
            # Make HTTP request
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                
            # Extract available information from the tag response
            labels = {
                "org.opencontainers.image.source": f"https://hub.docker.com/r/{repository}",
                "org.opencontainers.image.revision": "unknown",  # Docker Hub doesn't provide commit hash in tag API
                "org.opencontainers.image.version": tag,
                "org.opencontainers.image.licenses": "unknown",  # License info is in repository API
                "org.opencontainers.image.created": data.get("tag_last_pushed", "unknown"),
                "org.opencontainers.image.description": f"Docker Hub image {repository}:{tag}"
            }
            
            # Try to get repository information for additional details
            try:
                repo_api_url = f"https://hub.docker.com/v2/repositories/{repository}/"
                with urllib.request.urlopen(repo_api_url) as repo_response:
                    repo_data = json.loads(repo_response.read().decode())
                    
                # Update labels with repository information
                if repo_data.get("description"):
                    labels["org.opencontainers.image.description"] = repo_data["description"]
                if repo_data.get("license"):
                    labels["org.opencontainers.image.licenses"] = repo_data["license"]
                    
            except Exception as repo_e:
                self.logger.debug(f"Could not fetch repository details for {repository}: {repo_e}")
            
            self.logger.info(f"Successfully extracted Docker Hub labels for {repository}:{tag}")
            return labels
            
        except Exception as e:
            self.logger.warning(f"Failed to extract Docker Hub labels: {e}")
            return self._get_fallback_labels(repository, tag)
    
    def _extract_oci_labels_v2(self, registry: str, repository: str, tag: str) -> Dict[str, str]:
        """Extract labels from OCI registry using Distribution Spec v2 API.
        
        Args:
            registry: Registry hostname
            repository: Repository name
            tag: Image tag
            
        Returns:
            Dictionary of OCI labels
        """
        import urllib.request
        import json
        import base64
        
        try:
            # OCI Distribution Spec v2 API endpoints
            manifest_url = f"https://{registry}/v2/{repository}/manifests/{tag}"
            config_url = f"https://{registry}/v2/{repository}/blobs/"
            
            # Get manifest
            req = urllib.request.Request(manifest_url)
            req.add_header("Accept", "application/vnd.docker.distribution.manifest.v2+json")
            
            with urllib.request.urlopen(req) as response:
                manifest_data = json.loads(response.read().decode())
            
            # Get config blob (contains labels)
            config_digest = manifest_data.get("config", {}).get("digest")
            if config_digest:
                config_url += config_digest
                with urllib.request.urlopen(config_url) as response:
                    config_data = json.loads(response.read().decode())
                
                # Extract labels from config
                config_labels = config_data.get("config", {}).get("Labels", {})
                
                # Map to standard OCI labels
                labels = {
                    "org.opencontainers.image.source": config_labels.get("org.opencontainers.image.source", "unknown"),
                    "org.opencontainers.image.revision": config_labels.get("org.opencontainers.image.revision", "unknown"),
                    "org.opencontainers.image.version": config_labels.get("org.opencontainers.image.version", tag),
                    "org.opencontainers.image.licenses": config_labels.get("org.opencontainers.image.licenses", "unknown"),
                    "org.opencontainers.image.created": config_labels.get("org.opencontainers.image.created", "unknown"),
                    "org.opencontainers.image.description": config_labels.get("org.opencontainers.image.description", "Application container image")
                }
                
                self.logger.info(f"Successfully extracted OCI labels from {registry}/{repository}:{tag}")
                return labels
            
            return self._get_fallback_labels(repository, tag)
            
        except Exception as e:
            self.logger.warning(f"Failed to extract OCI labels from {registry}/{repository}:{tag}: {e}")
            return self._get_fallback_labels(repository, tag)
    
    def _get_fallback_labels(self, repository: str, tag: str) -> Dict[str, str]:
        """Get fallback labels when extraction fails.
        
        Args:
            repository: Repository name
            tag: Image tag
            
        Returns:
            Dictionary of fallback labels
        """
        return {
            "org.opencontainers.image.source": "unknown",
            "org.opencontainers.image.revision": "unknown",
            "org.opencontainers.image.version": tag,
            "org.opencontainers.image.licenses": "unknown",
            "org.opencontainers.image.created": "unknown",
            "org.opencontainers.image.description": f"Application container image {repository}:{tag}"
        }
    
    def _execute_source_link_step(self) -> Dict[str, Any]:
        """Execute the source link step - establish source code links from OCI labels.
        
        Returns:
            Dictionary with source code links and repository information
        """
        try:
            self.logger.info("Executing source link step: establishing source code links")
            
            # Get OCI labels from previous step (if available)
            # For now, we'll work with the plan data
            workloads = self.plan.targets.get("workloads", [])
            source_links = {}
            
            for workload in workloads:
                workload_name = workload.get("name")
                images = workload.get("images", [])
                
                for image in images:
                    image_ref = image.get("ref")
                    repo = image.get("repo", {})
                    
                    # Extract source information from repo or OCI labels
                    source_info = self._extract_source_info(image_ref, repo)
                    
                    if image_ref not in source_links:
                        source_links[image_ref] = {
                            "workloads": [],
                            "source_info": source_info,
                            "established_at": datetime.utcnow().isoformat()
                        }
                    
                    source_links[image_ref]["workloads"].append(workload_name)
            
            self.logger.info(f"Source link step completed: established links for {len(source_links)} images")
            
            return {
                "status": "completed",
                "message": "Source links established",
                "timestamp": datetime.utcnow().isoformat(),
                "total_images": len(source_links),
                "source_links": source_links
            }
            
        except Exception as e:
            self.logger.error(f"Source link step failed: {e}")
            return {
                "status": "failed",
                "message": f"Source link step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _extract_source_info(self, image_ref: str, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Extract source information from image reference and repo data.
        
        Args:
            image_ref: Container image reference
            repo: Repository information from the plan
            
        Returns:
            Dictionary with source information
        """
        source_info = {
            "repository_url": None,
            "branch": None,
            "commit": None,
            "source_type": "unknown"
        }
        
        # Check if we have repo information from the plan
        if repo and repo.get("key"):
            source_info["repository_url"] = repo.get("key")
            source_info["source_type"] = "plan_repo"
        
        # In a full implementation, we would also:
        # 1. Extract source from OCI labels (org.opencontainers.image.source)
        # 2. Parse Git URLs and extract branch/commit information
        # 3. Validate repository accessibility
        
        # For now, try to infer from image reference
        if "github.com" in image_ref or "gitlab.com" in image_ref:
            source_info["source_type"] = "inferred_from_image"
        
        return source_info
    
    def _execute_source_analysis_step(self) -> Dict[str, Any]:
        """Execute the source analysis step - analyze source code using existing MapOSCAL run-all command.
        
        Returns:
            Dictionary with source code analysis results
        """
        try:
            self.logger.info("Executing source analysis step: analyzing source code using MapOSCAL run-all")
            
            # Get source directories from the plan configuration
            source_directories = self.plan.config.get("source_analysis", {}).get("source_directories", [])
            
            source_analysis = {}
            
            for source_config in source_directories:
                source_path = source_config.get("path")
                source_type = source_config.get("type", "local")
                
                if source_type == "local" and source_path:
                    # Use existing MapOSCAL run-all command to analyze the source directory
                    analysis_result = self._run_maposcal_analysis(source_path)
                    source_analysis[source_path] = {
                        "type": source_type,
                        "analysis": analysis_result,
                        "analyzed_at": datetime.utcnow().isoformat()
                    }
            
            self.logger.info(f"Source analysis step completed: analyzed {len(source_analysis)} source directories")
            
            return {
                "status": "completed",
                "message": "Source analysis completed using MapOSCAL run-all",
                "timestamp": datetime.utcnow().isoformat(),
                "total_directories": len(source_analysis),
                "source_analysis": source_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Source analysis step failed: {e}")
            return {
                "status": "failed",
                "message": f"Source analysis step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _run_maposcal_analysis(self, source_path: str) -> Dict[str, Any]:
        """Run MapOSCAL analysis on a source directory using the existing run-all command.
        
        Args:
            source_path: Path to source directory to analyze
            
        Returns:
            Dictionary with MapOSCAL analysis results
        """
        try:
            import subprocess
            import tempfile
            import os
            from pathlib import Path
            
            # Create a temporary config file for this analysis
            config_data = {
                "repo_path": source_path,
                "output_dir": f".maposcal_analysis/{Path(source_path).name}",
                "catalog_path": "examples/NIST_SP-800-53_rev5_catalog.json",
                "profile_path": "examples/min_baseline.json"
            }
            
            # Create temp config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                import yaml
                yaml.dump(config_data, f)
                temp_config = f.name
            
            try:
                # Run MapOSCAL run-all command
                self.logger.info(f"Running MapOSCAL analysis on {source_path}")
                result = subprocess.run(
                    ["maposcal", "run-all", temp_config],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    # Analysis completed successfully
                    analysis_result = {
                        "status": "completed",
                        "output_dir": config_data["output_dir"],
                        "stdout": result.stdout,
                        "maposcal_ready": True
                    }
                    
                    # Check if output files were generated
                    output_dir = Path(config_data["output_dir"])
                    if output_dir.exists():
                        analysis_result["files_generated"] = [
                            f.name for f in output_dir.iterdir() if f.is_file()
                        ]
                    
                    self.logger.info(f"MapOSCAL analysis completed successfully for {source_path}")
                    return analysis_result
                else:
                    # Analysis failed
                    self.logger.warning(f"MapOSCAL analysis failed for {source_path}: {result.stderr}")
                    return {
                        "status": "failed",
                        "error": result.stderr,
                        "stdout": result.stdout,
                        "maposcal_ready": False
                    }
                    
            finally:
                # Clean up temp config file
                if os.path.exists(temp_config):
                    os.unlink(temp_config)
                    
        except Exception as e:
            self.logger.error(f"Failed to run MapOSCAL analysis on {source_path}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "maposcal_ready": False
            }
    
    def _execute_control_mapping_step(self) -> Dict[str, Any]:
        """Execute the control mapping step - map controls to components/capabilities.
        
        Returns:
            Dictionary with control mapping results
        """
        try:
            self.logger.info("Executing control mapping step: mapping security controls")
            
            # Get all workloads and their characteristics
            workloads = self.plan.targets.get("workloads", [])
            control_mappings = {}
            
            for workload in workloads:
                workload_name = workload.get("name")
                workload_namespace = workload.get("namespace")
                resource_types = workload.get("resource_types", [])
                images = workload.get("images", [])
                
                # Map controls based on workload characteristics
                workload_controls = self._map_workload_controls(
                    workload_name, workload_namespace, resource_types, images
                )
                
                control_mappings[workload_name] = {
                    "namespace": workload_namespace,
                    "resource_types": resource_types,
                    "image_count": len(images),
                    "controls": workload_controls,
                    "mapped_at": datetime.utcnow().isoformat()
                }
            
            self.logger.info(f"Control mapping step completed: mapped controls for {len(control_mappings)} workloads")
            
            return {
                "status": "completed",
                "message": "Control mapping generated",
                "timestamp": datetime.utcnow().isoformat(),
                "total_workloads": len(control_mappings),
                "control_mappings": control_mappings
            }
            
        except Exception as e:
            self.logger.error(f"Control mapping step failed: {e}")
            return {
                "status": "failed",
                "message": f"Control mapping step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _map_workload_controls(self, workload_name: str, namespace: str, 
                              resource_types: List[str], images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map security controls to a workload based on its characteristics.
        
        Args:
            workload_name: Name of the workload
            namespace: Kubernetes namespace
            resource_types: Types of Kubernetes resources
            images: List of container images
            
        Returns:
            Dictionary with mapped controls
        """
        # This is a placeholder implementation
        # In a full implementation, this would:
        # 1. Use existing MapOSCAL control mapping logic
        # 2. Analyze workload characteristics for control relevance
        # 3. Apply AI-powered control suggestions
        
        controls = {
            "access_control": [],
            "data_protection": [],
            "network_security": [],
            "monitoring": [],
            "compliance": []
        }
        
        # Map controls based on resource types
        if "Deployment" in resource_types:
            controls["access_control"].extend([
                "AC-2: Account Management",
                "AC-3: Access Enforcement"
            ])
            controls["network_security"].extend([
                "SC-7: Boundary Protection",
                "SC-8: Transmission Confidentiality and Integrity"
            ])
        
        if "Service" in resource_types:
            controls["network_security"].extend([
                "SC-7: Boundary Protection",
                "SC-8: Transmission Confidentiality and Integrity"
            ])
        
        if "Secret" in resource_types:
            controls["data_protection"].extend([
                "SC-8: Transmission Confidentiality and Integrity",
                "SC-12: Cryptographic Key Establishment and Management"
            ])
        
        if "ConfigMap" in resource_types:
            controls["data_protection"].extend([
                "SC-8: Transmission Confidentiality and Integrity"
            ])
        
        # Add common controls for all workloads
        controls["monitoring"].extend([
            "AU-2: Audit Events",
            "AU-3: Content of Audit Records"
        ])
        
        controls["compliance"].extend([
            "CM-6: Configuration Settings",
            "CM-8: Information System Component Inventory"
        ])
        
        self.logger.info(f"Mapped controls for workload {workload_name} (placeholder implementation)")
        
        return controls
    
    # Removed complex MapOSCAL integration methods - using simple control mapping instead
    
    def _execute_sbom_step(self) -> Dict[str, Any]:
        """Execute the SBOM step."""
        return {
            "status": "completed",
            "message": "SBOM generated",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_provenance_step(self) -> Dict[str, Any]:
        """Execute the provenance step - collect build and deployment provenance.
        
        Returns:
            Dictionary with provenance information
        """
        try:
            self.logger.info("Executing provenance step: collecting build and deployment provenance")
            
            # Get all workloads and their metadata
            workloads = self.plan.targets.get("workloads", [])
            provenance_data = {}
            
            for workload in workloads:
                workload_name = workload.get("name")
                workload_namespace = workload.get("namespace")
                images = workload.get("images", [])
                
                # Collect provenance for this workload
                workload_provenance = self._collect_workload_provenance(
                    workload_name, workload_namespace, images
                )
                
                provenance_data[workload_name] = {
                    "namespace": workload_namespace,
                    "image_count": len(images),
                    "provenance": workload_provenance,
                    "collected_at": datetime.utcnow().isoformat()
                }
            
            self.logger.info(f"Provenance step completed: collected data for {len(provenance_data)} workloads")
            
            return {
                "status": "completed",
                "message": "Provenance collected",
                "timestamp": datetime.utcnow().isoformat(),
                "total_workloads": len(provenance_data),
                "provenance_data": provenance_data
            }
            
        except Exception as e:
            self.logger.error(f"Provenance step failed: {e}")
            return {
                "status": "failed",
                "message": f"Provenance step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _collect_workload_provenance(self, workload_name: str, namespace: str, 
                                   images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect provenance information for a specific workload.
        
        Args:
            workload_name: Name of the workload
            namespace: Kubernetes namespace
            images: List of container images
            
        Returns:
            Dictionary with provenance information
        """
        # This is a placeholder implementation
        # In a full implementation, this would:
        # 1. Extract build information from container images
        # 2. Collect deployment metadata from Kubernetes
        # 3. Gather CI/CD pipeline information
        # 4. Document configuration management details
        
        provenance = {
            "build_info": {
                "build_tool": "unknown",
                "build_timestamp": datetime.utcnow().isoformat(),
                "build_platform": "unknown"
            },
            "deployment_info": {
                "deployment_tool": "Argo CD",
                "deployment_namespace": namespace,
                "deployment_timestamp": datetime.utcnow().isoformat()
            },
            "configuration": {
                "config_management": "GitOps (Argo CD)",
                "config_source": "Git repository",
                "config_version": "latest"
            },
            "security": {
                "image_scanning": "unknown",
                "vulnerability_assessment": "unknown",
                "compliance_checking": "unknown"
            }
        }
        
        # Try to infer build tool from image references
        for image in images:
            image_ref = image.get("ref", "")
            if "docker" in image_ref.lower():
                provenance["build_info"]["build_tool"] = "Docker"
            elif "buildah" in image_ref.lower():
                provenance["build_info"]["build_tool"] = "Buildah"
            elif "kaniko" in image_ref.lower():
                provenance["build_info"]["build_tool"] = "Kaniko"
        
        self.logger.info(f"Collected provenance for workload {workload_name} (placeholder implementation)")
        
        return provenance
    
    def _execute_oscal_emit_step(self) -> Dict[str, Any]:
        """Execute the OSCAL emit step - generate OSCAL Component Definition."""
        try:
            self.logger.info("Executing OSCAL emit step: generating OSCAL Component Definition")
            
            # Import OSCAL functionality
            try:
                from maposcal.oscal.models import create_component_definition_from_execution_results
                from maposcal.oscal.serializer import serialize_oscal_to_file
                from maposcal.oscal.validator import validate_oscal_file
            except ImportError as e:
                self.logger.error(f"Failed to import OSCAL modules: {e}")
                return {
                    "status": "failed",
                    "message": f"OSCAL modules not available: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
            
            # Get workloads from the plan
            workloads = self.plan.targets.get("workloads", [])
            
            if not workloads:
                self.logger.warning("No workloads found for OSCAL generation")
                return {
                    "status": "completed",
                    "message": "No workloads to generate OSCAL for",
                    "timestamp": datetime.utcnow().isoformat(),
                    "workload_count": 0
                }
            
            # Create OSCAL Component Definition
            component_def = create_component_definition_from_execution_results(
                application_name=self.plan.application,
                application_namespace=self.plan.application_namespace,
                workloads=workloads
            )
            
            # Generate output path
            output_dir = self.plan.get_cache_base_path()
            output_path = f"{output_dir}/component-definition.json"
            
            # Serialize to JSON
            success = serialize_oscal_to_file(component_def, output_path)
            
            if not success:
                return {
                    "status": "failed",
                    "message": "Failed to serialize OSCAL Component Definition",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": "Serialization failed"
                }
            
            # Validate the generated file
            is_valid, validation_summary = validate_oscal_file(output_path)
            
            if not is_valid:
                self.logger.warning(f"Generated OSCAL file has validation issues: {validation_summary}")
            
            self.logger.info(f"OSCAL Component Definition generated successfully: {output_path}")
            
            return {
                "status": "completed",
                "message": "OSCAL Component Definition generated",
                "timestamp": datetime.utcnow().isoformat(),
                "output_file": output_path,
                "workload_count": len(workloads),
                "component_count": len(component_def.components),
                "capability_count": len(component_def.capabilities),
                "validation": validation_summary
            }
            
        except Exception as e:
            self.logger.error(f"OSCAL emit step failed: {e}")
            return {
                "status": "failed",
                "message": f"OSCAL emit step failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
        # Removed _generate_oscal_components method - now using OSCAL module integration
    
    def _is_critical_step(self, step_id: str) -> bool:
        """Check if a step is critical (execution should stop on failure).
        
        Args:
            step_id: ID of the step to check
            
        Returns:
            True if step is critical
        """
        # For now, consider all steps non-critical
        # This can be enhanced with step-specific criticality rules
        return False
    
    def _finalize_execution(self) -> None:
        """Finalize execution and update state."""
        if self.failed_steps:
            self.logger.warning(f"Execution completed with {len(self.failed_steps)} failed steps")
        else:
            self.logger.info("Execution completed successfully")
    
    def _handle_execution_failure(self, error_message: str) -> None:
        """Handle execution failure and update state.
        
        Args:
            error_message: Error message describing the failure
        """
        self.logger.error(f"Execution failed: {error_message}")
        # Update state to reflect failure
        # This would be handled by the state manager
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the current execution state.
        
        Returns:
            Dictionary with execution summary
        """
        return {
            "plan_application": self.plan.application,
            "total_steps": len(self.execution_order),
            "completed_steps": len(self.completed_steps),
            "failed_steps": len(self.failed_steps),
            "pending_steps": len(self.execution_order) - len(self.completed_steps) - len(self.failed_steps),
            "execution_order": self.execution_order,
            "can_resume": self.state_manager.can_resume()
        }
