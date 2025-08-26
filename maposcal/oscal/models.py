"""
OSCAL Data Models for MapOSCAL.

This module defines the core OSCAL data structures using compliance-trestle
for generating valid OSCAL Component Definitions from Argo CD applications.

OSCAL Version: 1.1.3 (latest stable)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid

# Import compliance-trestle OSCAL models
try:
    from trestle.oscal.component import ComponentDefinition, Component, Capability
    from trestle.oscal.common import Metadata, Property, Link, Role, Party
    from trestle.oscal.assessment_common import AssessmentSubject, AssessmentSubjectTarget
    from trestle.oscal.implementation_common import ImplementedRequirement, ControlImplementation
    COMPLIANCE_TRESTLE_AVAILABLE = True
except ImportError:
    COMPLIANCE_TRESTLE_AVAILABLE = False
    # Fallback dataclasses if compliance-trestle is not available
    ComponentDefinition = None
    Component = None
    Capability = None
    Metadata = None
    Property = None
    Link = None
    Role = None
    Party = None
    AssessmentSubject = None
    AssessmentSubjectTarget = None
    ImplementedRequirement = None
    ControlImplementation = None


@dataclass
class OSCALMetadata:
    """OSCAL metadata for MapOSCAL-generated components."""
    
    title: str
    version: str = "1.0.0"
    oscal_version: str = "1.1.3"
    published: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    
    # MapOSCAL-specific properties
    maposcal_version: str = "0.3.0"
    generator: str = "MapOSCAL Argo CD Integration"
    source_type: str = "Argo CD Application"
    
    # Parties and roles
    parties: List[Dict[str, Any]] = field(default_factory=list)
    roles: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for OSCAL serialization."""
        return {
            "title": self.title,
            "version": self.version,
            "oscal-version": self.oscal_version,
            "published": self.published.isoformat(),
            "last-modified": self.last_modified.isoformat(),
            "properties": [
                {
                    "name": "maposcal-version",
                    "value": self.maposcal_version
                },
                {
                    "name": "generator",
                    "value": self.generator
                },
                {
                    "name": "source-type",
                    "value": self.source_type
                }
            ],
            "parties": self.parties,
            "roles": self.roles
        }


@dataclass
class OSCALComponent:
    """OSCAL Component representing a workload or service."""
    
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    component_type: str = "service"
    
    # Component properties
    props: List[Dict[str, Any]] = field(default_factory=list)
    
    # Links to related resources
    links: List[Dict[str, Any]] = field(default_factory=list)
    
    # Control implementations (placeholder for future RAG flow)
    control_implementations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status and lifecycle
    status: str = "operational"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for OSCAL serialization."""
        return {
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "type": self.component_type,
            "props": self.props,
            "links": self.links,
            "control-implementations": self.control_implementations,
            "status": {"state": self.status}
        }


@dataclass
class OSCALCapability:
    """OSCAL Capability representing cross-cutting concerns."""
    
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Capability properties
    props: List[Dict[str, Any]] = field(default_factory=list)
    
    # Control implementations (placeholder for future RAG flow)
    control_implementations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for OSCAL serialization."""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "props": self.props,
            "control-implementations": self.control_implementations
        }


@dataclass
class OSCALControlImplementation:
    """OSCAL Control Implementation (placeholder for future RAG flow)."""
    
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    control_id: str = ""
    description: str = ""
    implemented_requirements: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for OSCAL serialization."""
        return {
            "uuid": self.uuid,
            "control-id": self.control_id,
            "description": self.description,
            "implemented-requirements": self.implemented_requirements
        }


@dataclass
class OSCALComponentDefinition:
    """OSCAL Component Definition for Argo CD applications."""
    
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: OSCALMetadata = field(default_factory=OSCALMetadata)
    
    # Components (workloads, services)
    components: List[OSCALComponent] = field(default_factory=list)
    
    # Capabilities (cross-cutting concerns)
    capabilities: List[OSCALCapability] = field(default_factory=list)
    
    # Control implementations (placeholder for future RAG flow)
    control_implementations: List[OSCALControlImplementation] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for OSCAL serialization."""
        return {
            "uuid": self.uuid,
            "metadata": self.metadata.to_dict(),
            "components": [comp.to_dict() for comp in self.components],
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "control-implementations": [ci.to_dict() for ci in self.control_implementations]
        }
    
    def add_component(self, component: OSCALComponent) -> None:
        """Add a component to the definition."""
        self.components.append(component)
    
    def add_capability(self, capability: OSCALCapability) -> None:
        """Add a capability to the definition."""
        self.capabilities.append(capability)
    
    def add_control_implementation(self, control_impl: OSCALControlImplementation) -> None:
        """Add a control implementation to the definition."""
        self.control_implementations.append(control_impl)


# Factory functions for creating OSCAL objects
def create_component_from_workload(workload_data: Dict[str, Any]) -> OSCALComponent:
    """Create an OSCAL Component from workload data."""
    
    # Extract workload information
    name = workload_data.get("name", "unknown")
    namespace = workload_data.get("namespace", "default")
    resource_types = workload_data.get("resource_types", [])
    images = workload_data.get("images", [])
    
    # Create component
    component = OSCALComponent(
        title=f"{name} ({namespace})",
        description=f"Kubernetes workload {name} in namespace {namespace}",
        component_type="service"
    )
    
    # Add properties
    component.props.extend([
        {
            "name": "workload-name",
            "value": name
        },
        {
            "name": "namespace",
            "value": namespace
        },
        {
            "name": "resource-types",
            "value": ", ".join(resource_types)
        },
        {
            "name": "image-count",
            "value": str(len(images))
        }
    ])
    
    # Add image information as properties
    for i, image in enumerate(images):
        image_ref = image.get("ref", "unknown")
        component.props.append({
            "name": f"image-{i+1}",
            "value": image_ref
        })
    
    return component


def create_capability_from_type(capability_type: str, description: str) -> OSCALCapability:
    """Create an OSCAL Capability for cross-cutting concerns."""
    
    capability = OSCALCapability(
        name=f"{capability_type} Capability",
        description=description
    )
    
    capability.props.append({
        "name": "capability-type",
        "value": capability_type
    })
    
    return capability


def create_component_definition_from_execution_results(
    application_name: str,
    application_namespace: str,
    workloads: List[Dict[str, Any]]
) -> OSCALComponentDefinition:
    """Create an OSCAL Component Definition from execution results."""
    
    # Create metadata
    metadata = OSCALMetadata(
        title=f"OSCAL Component Definition for {application_name}"
    )
    
    # Create component definition
    component_def = OSCALComponentDefinition(metadata=metadata)
    
    # Add components from workloads
    for workload in workloads:
        component = create_component_from_workload(workload)
        component_def.add_component(component)
    
    # Add common capabilities
    capabilities = [
        ("Network Security", "Network security controls and boundary protection"),
        ("Data Protection", "Data encryption and protection mechanisms"),
        ("Monitoring", "Logging, monitoring, and audit capabilities")
    ]
    
    for cap_type, cap_desc in capabilities:
        capability = create_capability_from_type(cap_type, cap_desc)
        component_def.add_capability(capability)
    
    return component_def
