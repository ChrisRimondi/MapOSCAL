"""
Execution plan generator for MapOSCAL.

This module provides functionality to generate execution plans for Argo CD
Application analysis based on discovered resources and workloads.
"""

from typing import Dict, List, Optional, Any
from .models import ExecutionPlan, WorkloadTarget, ImageTarget, Step, StepStatus
from ..argo.workload_grouper import WorkloadGroup


class PlanGenerator:
    """Generates execution plans for Argo CD Application analysis."""
    
    def __init__(self):
        """Initialize the plan generator."""
        # Define the standard execution steps
        self.standard_steps = [
            "render",
            "inventory", 
            "images",
            "oci_labels",
            "source_link",
            "source_analysis",
            "control_mapping",
            "sbom",
            "provenance",
            "oscal_emit"
        ]
        
        # Define step dependencies
        self.step_dependencies = {
            "oscal_emit": ["oci_labels", "control_mapping"],
            "control_mapping": ["source_analysis"],
            "source_analysis": ["source_link"],
            "source_link": ["oci_labels"],
        }
    
    def generate_plan(self, application_name: str, workload_groups: List[WorkloadGroup], 
                     namespace_policies: Dict[str, Any], standalone_resources: List[Any]) -> ExecutionPlan:
        """Generate an execution plan for Argo CD Application analysis.
        
        Args:
            application_name: Name of the Argo CD Application
            workload_groups: List of discovered workload groups
            namespace_policies: Namespace-level policies
            standalone_resources: Resources not part of any workload group
            
        Returns:
            Execution plan ready for execution
        """
        # Create the base execution plan
        plan = ExecutionPlan(
            application=application_name,
            steps=self.standard_steps
        )
        
        # Create targets structure
        targets = {
            "workloads": [],
            "repos": []
        }
        
        # Process workload groups
        for group in workload_groups:
            workload_target = self._create_workload_target(group)
            targets["workloads"].append(workload_target)
        
        # Process namespace policies as capabilities (future enhancement)
        # For now, we'll focus on workloads
        
        # Process standalone resources (future enhancement)
        
        plan.targets = targets
        
        return plan
    
    def _create_workload_target(self, group: WorkloadGroup) -> Dict[str, Any]:
        """Create a workload target from a workload group.
        
        Args:
            group: Workload group to convert to target
            
        Returns:
            Workload target dictionary
        """
        # Create steps for the workload
        workload_steps = {
            "render": self._create_step("render", enabled=True),
            "inventory": self._create_step("inventory", enabled=True),
            "oscal_emit": self._create_step("oscal_emit", enabled=True, 
                                          depends_on=["oci_labels", "control_mapping"])
        }
        
        # Create image targets
        image_targets = []
        for image_ref in group.container_images:
            image_target = self._create_image_target(image_ref)
            image_targets.append(image_target)
        
        return {
            "name": group.name,
            "namespace": group.namespace,
            "steps": {step_id: step.to_dict() for step_id, step in workload_steps.items()},
            "images": [img.to_dict() for img in image_targets],
            "resource_types": group.resource_types
        }
    
    def _create_image_target(self, image_ref: str) -> ImageTarget:
        """Create an image target for a container image.
        
        Args:
            image_ref: Container image reference
            
        Returns:
            Image target object
        """
        # Create steps for the image
        image_steps = {
            "oci_labels": self._create_step("oci_labels", enabled=True),
            "sbom": self._create_step("sbom", enabled=False),  # Disabled by default
            "provenance": self._create_step("provenance", enabled=False)  # Disabled by default
        }
        
        # Create repo placeholder (will be filled during execution)
        repo_info = {
            "key": None,  # Will be populated from OCI labels
            "steps": {
                "source_analysis": self._create_step("source_analysis", enabled=True).to_dict(),
                "control_mapping": self._create_step("control_mapping", enabled=True, 
                                                  depends_on=["source_analysis"]).to_dict()
            }
        }
        
        return ImageTarget(
            ref=image_ref,
            steps=image_steps,
            repo=repo_info
        )
    
    def _create_step(self, step_id: str, enabled: bool = True, 
                    depends_on: Optional[List[str]] = None) -> Step:
        """Create a step with the specified configuration.
        
        Args:
            step_id: Step identifier
            enabled: Whether the step is enabled
            depends_on: List of step dependencies
            
        Returns:
            Step object
        """
        return Step(
            id=step_id,
            enabled=enabled,
            depends_on=depends_on or []
        )
    
    def validate_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Validate an execution plan for correctness.
        
        Args:
            plan: Execution plan to validate
            
        Returns:
            Validation results
        """
        errors = []
        warnings = []
        
        # Check basic structure
        if not plan.application:
            errors.append("Application name is required")
        
        if not plan.steps:
            errors.append("At least one step must be defined")
        
        if not plan.targets:
            errors.append("At least one target must be defined")
        
        # Check workload targets
        workloads = plan.targets.get("workloads", [])
        if not workloads:
            warnings.append("No workload targets defined")
        
        for workload in workloads:
            workload_errors = self._validate_workload_target(workload)
            errors.extend(workload_errors)
        
        # Check for circular dependencies
        circular_deps = self._check_circular_dependencies(plan)
        if circular_deps:
            errors.append(f"Circular dependencies detected: {circular_deps}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_workload_target(self, workload: Dict[str, Any]) -> List[str]:
        """Validate a workload target.
        
        Args:
            workload: Workload target to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required fields
        if not workload.get("name"):
            errors.append("Workload name is required")
        
        if not workload.get("namespace"):
            errors.append("Workload namespace is required")
        
        # Check steps
        steps = workload.get("steps", {})
        if not steps:
            errors.append("Workload must have at least one step")
        
        # Check images
        images = workload.get("images", [])
        if not images:
            warnings.append(f"Workload {workload.get('name', 'unknown')} has no container images")
        
        return errors
    
    def _check_circular_dependencies(self, plan: ExecutionPlan) -> List[str]:
        """Check for circular dependencies in the plan.
        
        Args:
            plan: Execution plan to check
            
        Returns:
            List of circular dependency chains
        """
        # This is a simplified implementation
        # In a real implementation, you'd use a proper graph algorithm
        # For now, we'll just check the predefined dependencies
        
        circular_chains = []
        
        # Check if any step depends on itself (directly or indirectly)
        for step_id in plan.steps:
            if self._has_circular_dependency(step_id, step_id, set(), plan):
                circular_chains.append(step_id)
        
        return circular_chains
    
    def _has_circular_dependency(self, current_step: str, target_step: str, 
                                visited: set, plan: ExecutionPlan) -> bool:
        """Check if a step has a circular dependency.
        
        Args:
            current_step: Current step being checked
            target_step: Target step to find
            visited: Set of visited steps
            plan: Execution plan
            
        Returns:
            True if circular dependency exists
        """
        if current_step in visited:
            return False
        
        visited.add(current_step)
        
        # Check dependencies of current step
        for workload in plan.targets.get("workloads", []):
            for step_id, step_data in workload.get("steps", {}).items():
                if step_id == current_step:
                    depends_on = step_data.get("depends_on", [])
                    for dep in depends_on:
                        if dep == target_step:
                            return True
                        if self._has_circular_dependency(dep, target_step, visited, plan):
                            return True
        
        return False
    
    def create_minimal_plan(self, application_name: str, workload_groups: List[WorkloadGroup]) -> ExecutionPlan:
        """Create a minimal execution plan with only essential steps enabled.
        
        Args:
            application_name: Name of the Argo CD Application
            workload_groups: List of discovered workload groups
            
        Returns:
            Minimal execution plan
        """
        # Create a plan with only essential steps enabled
        minimal_steps = ["render", "inventory", "images", "oscal_emit"]
        
        plan = ExecutionPlan(
            application=application_name,
            steps=minimal_steps
        )
        
        # Create minimal targets
        targets = {
            "workloads": [],
            "repos": []
        }
        
        for group in workload_groups:
            workload_target = self._create_minimal_workload_target(group)
            targets["workloads"].append(workload_target)
        
        plan.targets = targets
        return plan
    
    def _create_minimal_workload_target(self, group: WorkloadGroup) -> Dict[str, Any]:
        """Create a minimal workload target with only essential steps.
        
        Args:
            group: Workload group to convert to target
            
        Returns:
            Minimal workload target dictionary
        """
        # Only enable essential steps
        workload_steps = {
            "render": self._create_step("render", enabled=True),
            "inventory": self._create_step("inventory", enabled=True),
            "oscal_emit": self._create_step("oscal_emit", enabled=True)
        }
        
        # Create minimal image targets
        image_targets = []
        for image_ref in group.container_images:
            image_target = self._create_minimal_image_target(image_ref)
            image_targets.append(image_target)
        
        return {
            "name": group.name,
            "namespace": group.namespace,
            "steps": {step_id: step.to_dict() for step_id, step in workload_steps.items()},
            "images": [img.to_dict() for img in image_targets],
            "resource_types": group.resource_types
        }
    
    def _create_minimal_image_target(self, image_ref: str) -> ImageTarget:
        """Create a minimal image target with only essential steps.
        
        Args:
            image_ref: Container image reference
            
        Returns:
            Minimal image target object
        """
        # Only enable essential steps
        image_steps = {
            "oci_labels": self._create_step("oci_labels", enabled=False),  # Disabled in minimal plan
            "sbom": self._create_step("sbom", enabled=False),
            "provenance": self._create_step("provenance", enabled=False)
        }
        
        return ImageTarget(
            ref=image_ref,
            steps=image_steps,
            repo=None
        )
