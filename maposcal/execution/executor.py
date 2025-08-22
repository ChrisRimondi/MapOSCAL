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
        """Execute the render step."""
        return {
            "status": "completed",
            "message": "Manifests rendered successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_inventory_step(self) -> Dict[str, Any]:
        """Execute the inventory step."""
        return {
            "status": "completed",
            "message": "Resource inventory created",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_images_step(self) -> Dict[str, Any]:
        """Execute the images step."""
        return {
            "status": "completed",
            "message": "Container images extracted",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_oci_labels_step(self) -> Dict[str, Any]:
        """Execute the OCI labels step."""
        return {
            "status": "completed",
            "message": "OCI labels extracted",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_source_link_step(self) -> Dict[str, Any]:
        """Execute the source link step."""
        return {
            "status": "completed",
            "message": "Source links established",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_source_analysis_step(self) -> Dict[str, Any]:
        """Execute the source analysis step."""
        return {
            "status": "completed",
            "message": "Source analysis completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_control_mapping_step(self) -> Dict[str, Any]:
        """Execute the control mapping step."""
        return {
            "status": "completed",
            "message": "Control mapping generated",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_sbom_step(self) -> Dict[str, Any]:
        """Execute the SBOM step."""
        return {
            "status": "completed",
            "message": "SBOM generated",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_provenance_step(self) -> Dict[str, Any]:
        """Execute the provenance step."""
        return {
            "status": "completed",
            "message": "Provenance collected",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_oscal_emit_step(self) -> Dict[str, Any]:
        """Execute the OSCAL emit step."""
        return {
            "status": "completed",
            "message": "OSCAL components generated",
            "timestamp": datetime.utcnow().isoformat()
        }
    
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
