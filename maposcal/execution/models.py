"""
Data models for execution plans and state management.

This module defines the core classes used to represent execution plans,
workload targets, image targets, and execution state for the Argo CD
Application analysis workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json


class StepStatus(Enum):
    """Status of an execution step."""
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Step:
    """Represents an execution step with configuration and dependencies."""
    
    id: str
    enabled: bool = True
    depends_on: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    artifact_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary for serialization."""
        return {
            "id": self.id,
            "enabled": self.enabled,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "artifact_hash": self.artifact_hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Step":
        """Create step from dictionary."""
        return cls(
            id=data["id"],
            enabled=data.get("enabled", True),
            depends_on=data.get("depends_on", []),
            status=StepStatus(data.get("status", "pending")),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error_message=data.get("error_message"),
            artifact_hash=data.get("artifact_hash"),
        )


@dataclass
class ImageTarget:
    """Represents a container image target for analysis."""
    
    ref: str  # Full image reference (e.g., ghcr.io/acme/orders@sha256:abcd...)
    steps: Dict[str, Step] = field(default_factory=dict)
    repo: Optional[Dict[str, Any]] = None  # Repository information from OCI labels
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert image target to dictionary for serialization."""
        return {
            "ref": self.ref,
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()},
            "repo": self.repo,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageTarget":
        """Create image target from dictionary."""
        return cls(
            ref=data["ref"],
            steps={step_id: Step.from_dict(step_data) for step_id, step_data in data.get("steps", {}).items()},
            repo=data.get("repo"),
        )


@dataclass
class WorkloadTarget:
    """Represents a workload target for analysis."""
    
    name: str
    namespace: str
    steps: Dict[str, Step] = field(default_factory=dict)
    images: List[ImageTarget] = field(default_factory=list)
    resource_types: List[str] = field(default_factory=list)  # Deployment, StatefulSet, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workload target to dictionary for serialization."""
        return {
            "name": self.name,
            "namespace": self.namespace,
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()},
            "images": [image.to_dict() for image in self.images],
            "resource_types": self.resource_types,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkloadTarget":
        """Create workload target from dictionary."""
        return cls(
            name=data["name"],
            namespace=data["namespace"],
            steps={step_id: Step.from_dict(step_data) for step_id, step_data in data.get("steps", {}).items()},
            images=[ImageTarget.from_dict(image_data) for image_data in data.get("images", [])],
            resource_types=data.get("resource_types", []),
        )


@dataclass
class ExecutionPlan:
    """Represents a complete execution plan for Argo CD Application analysis."""
    
    version: int = 1
    application: str = ""
    application_namespace: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)
    steps: List[str] = field(default_factory=list)  # List of step IDs
    targets: Dict[str, Any] = field(default_factory=dict)  # workloads, repos, etc.
    config: Dict[str, Any] = field(default_factory=dict)  # Configuration for analysis steps
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution plan to dictionary for serialization."""
        return {
            "version": self.version,
            "application": self.application,
            "application_namespace": self.application_namespace,
            "generated_at": self.generated_at.isoformat(),
            "steps": self.steps,
            "targets": self.targets,
            "config": self.config,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionPlan":
        """Create execution plan from dictionary."""
        return cls(
            version=data.get("version", 1),
            application=data.get("application", ""),
            application_namespace=data.get("application_namespace", ""),
            generated_at=datetime.fromisoformat(data["generated_at"]) if data.get("generated_at") else datetime.utcnow(),
            steps=data.get("steps", []),
            targets=data.get("targets", {}),
            config=data.get("config", {}),
        )
    
    def to_yaml(self) -> str:
        """Convert execution plan to YAML string."""
        import yaml
        # Use SafeDumper to avoid Python object references
        return yaml.dump(self.to_dict(), Dumper=yaml.SafeDumper, default_flow_style=False, sort_keys=False)
    
    def save_to_file(self, filepath: str) -> None:
        """Save execution plan to YAML file."""
        with open(filepath, 'w') as f:
            f.write(self.to_yaml())
    
    def get_cache_base_path(self) -> str:
        """Get the base cache path for this application.
        
        Returns:
            Base cache path for application artifacts
        """
        if not self.application:
            return ".maposcal/artifacts/default"
        return f".maposcal/artifacts/applications/{self.application}"
    
    def get_state_file_path(self) -> str:
        """Get the state file path for this application.
        
        Returns:
            Path to the application state file
        """
        if not self.application:
            return ".maposcal/applications/default/state.json"
        return f".maposcal/applications/{self.application}/state.json"


@dataclass
class ExecutionState:
    """Represents the current state of plan execution."""
    
    plan_file: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    step_states: Dict[str, Step] = field(default_factory=dict)
    overall_status: StepStatus = StepStatus.PENDING
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution state to dictionary for serialization."""
        return {
            "plan_file": self.plan_file,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "step_states": {step_id: step.to_dict() for step_id, step in self.step_states.items()},
            "overall_status": self.overall_status.value,
            "error_message": self.error_message,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionState":
        """Create execution state from dictionary."""
        return cls(
            plan_file=data["plan_file"],
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            step_states={step_id: Step.from_dict(step_data) for step_id, step_data in data.get("step_states", {}).items()},
            overall_status=StepStatus(data.get("overall_status", "pending")),
            error_message=data.get("error_message"),
        )
    
    def save_to_file(self, filepath: str) -> None:
        """Save execution state to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "ExecutionState":
        """Load execution state from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
