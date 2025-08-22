"""
State manager for MapOSCAL execution progress.

This module provides functionality to track and persist execution state
for resumable Argo CD Application analysis.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from .models import ExecutionState, Step, StepStatus


class StateManager:
    """Manages execution state for resumable operations."""
    
    def __init__(self, application_name: str, base_dir: str = ".maposcal"):
        """Initialize state manager for a specific application.
        
        Args:
            application_name: Name of the Argo CD Application
            base_dir: Base directory for MapOSCAL state files
        """
        self.application_name = application_name
        self.base_dir = Path(base_dir)
        
        # Application-specific state directory
        if application_name:
            self.state_dir = self.base_dir / "applications" / application_name
        else:
            self.state_dir = self.base_dir / "applications" / "default"
        
        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # State file path
        self.state_file = self.state_dir / "state.json"
        self.backup_file = self.state_dir / "state.backup.json"
    
    def create_new_state(self, plan_file: str) -> ExecutionState:
        """Create a new execution state for a plan.
        
        Args:
            plan_file: Path to the execution plan file
            
        Returns:
            New execution state
        """
        state = ExecutionState(
            plan_file=plan_file,
            started_at=datetime.utcnow(),
            step_states={},
            overall_status=StepStatus.PENDING
        )
        
        self.save_state(state)
        return state
    
    def load_state(self) -> Optional[ExecutionState]:
        """Load existing execution state.
        
        Returns:
            Execution state if exists, None otherwise
        """
        if not self.state_file.exists():
            return None
        
        try:
            # Try to load from main state file
            return ExecutionState.load_from_file(str(self.state_file))
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            # Try backup file if main file is corrupted
            if self.backup_file.exists():
                try:
                    return ExecutionState.load_from_file(str(self.backup_file))
                except (json.JSONDecodeError, KeyError, FileNotFoundError):
                    pass
            
            # If both files are corrupted, return None
            return None
    
    def save_state(self, state: ExecutionState) -> None:
        """Save execution state with backup.
        
        Args:
            state: Execution state to save
        """
        # Create backup of existing state
        if self.state_file.exists():
            try:
                self.state_file.rename(self.backup_file)
            except OSError:
                # If backup fails, remove old backup and try again
                if self.backup_file.exists():
                    self.backup_file.unlink()
                self.state_file.rename(self.backup_file)
        
        # Save new state
        state.save_to_file(str(self.state_file))
    
    def update_step_status(self, step_id: str, status: StepStatus, 
                          error_message: Optional[str] = None,
                          artifact_hash: Optional[str] = None) -> None:
        """Update the status of a specific step.
        
        Args:
            step_id: ID of the step to update
            status: New status for the step
            error_message: Error message if step failed
            artifact_hash: Hash of generated artifacts
        """
        state = self.load_state()
        if not state:
            raise RuntimeError("No execution state found")
        
        # Get or create step state
        if step_id not in state.step_states:
            state.step_states[step_id] = Step(id=step_id)
        
        step = state.step_states[step_id]
        step.status = status
        
        # Update timestamps
        if status == StepStatus.RUNNING and not step.started_at:
            step.started_at = datetime.utcnow()
        elif status in [StepStatus.DONE, StepStatus.FAILED, StepStatus.SKIPPED]:
            step.completed_at = datetime.utcnow()
        
        # Update other fields
        if error_message:
            step.error_message = error_message
        if artifact_hash:
            step.artifact_hash = artifact_hash
        
        # Update overall status
        self._update_overall_status(state)
        
        # Save updated state
        self.save_state(state)
    
    def _update_overall_status(self, state: ExecutionState) -> None:
        """Update the overall execution status based on step states.
        
        Args:
            state: Execution state to update
        """
        if not state.step_states:
            state.overall_status = StepStatus.PENDING
            return
        
        # Count step statuses
        status_counts = {}
        for step in state.step_states.values():
            status = step.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Determine overall status
        if StepStatus.FAILED in status_counts:
            state.overall_status = StepStatus.FAILED
        elif StepStatus.RUNNING in status_counts:
            state.overall_status = StepStatus.RUNNING
        elif StepStatus.PENDING in status_counts:
            state.overall_status = StepStatus.PENDING
        else:
            # All steps are done or skipped
            state.overall_status = StepStatus.DONE
    
    def get_pending_steps(self) -> List[str]:
        """Get list of steps that are pending execution.
        
        Returns:
            List of step IDs that are pending
        """
        state = self.load_state()
        if not state:
            return []
        
        return [
            step_id for step_id, step in state.step_states.items()
            if step.status == StepStatus.PENDING
        ]
    
    def get_failed_steps(self) -> List[str]:
        """Get list of steps that failed.
        
        Returns:
            List of step IDs that failed
        """
        state = self.load_state()
        if not state:
            return []
        
        return [
            step_id for step_id, step in state.step_states.items()
            if step.status == StepStatus.FAILED
        ]
    
    def get_completed_steps(self) -> List[str]:
        """Get list of steps that completed successfully.
        
        Returns:
            List of step IDs that completed
        """
        state = self.load_state()
        if not state:
            return []
        
        return [
            step_id for step_id, step in state.step_states.items()
            if step.status == StepStatus.DONE
        ]
    
    def can_resume(self) -> bool:
        """Check if execution can be resumed.
        
        Returns:
            True if execution can be resumed
        """
        state = self.load_state()
        if not state:
            return False
        
        # Can resume if there are pending steps and no failed steps
        pending_steps = self.get_pending_steps()
        failed_steps = self.get_failed_steps()
        
        return len(pending_steps) > 0 and len(failed_steps) == 0
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of execution progress.
        
        Returns:
            Dictionary with execution summary
        """
        state = self.load_state()
        if not state:
            return {"status": "no_state", "message": "No execution state found"}
        
        total_steps = len(state.step_states)
        completed_steps = len(self.get_completed_steps())
        failed_steps = len(self.get_failed_steps())
        pending_steps = len(self.get_pending_steps())
        running_steps = len([
            step_id for step_id, step in state.step_states.items()
            if step.status == StepStatus.RUNNING
        ])
        
        return {
            "application": self.application_name,
            "overall_status": state.overall_status.value,
            "started_at": state.started_at.isoformat() if state.started_at else None,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "pending_steps": pending_steps,
            "running_steps": running_steps,
            "progress_percentage": round((completed_steps / total_steps * 100) if total_steps > 0 else 0, 1),
            "can_resume": self.can_resume()
        }
    
    def reset_state(self) -> None:
        """Reset the execution state (remove state files).
        
        Use with caution - this will remove all progress information.
        """
        if self.state_file.exists():
            self.state_file.unlink()
        if self.backup_file.exists():
            self.backup_file.unlink()
    
    def cleanup_old_states(self, max_age_days: int = 7) -> int:
        """Clean up old state files to manage disk space.
        
        Args:
            max_age_days: Maximum age of state files in days
            
        Returns:
            Number of state files cleaned up
        """
        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for state_file in self.state_dir.glob("state*.json"):
            try:
                if state_file.stat().st_mtime < cutoff_time:
                    state_file.unlink()
                    cleaned_count += 1
            except OSError:
                # Skip files that can't be deleted
                continue
        
        return cleaned_count
