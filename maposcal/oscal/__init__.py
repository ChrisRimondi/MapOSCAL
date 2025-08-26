"""
maposcal.oscal
~~~~~~~~~~~~~~~~

OSCAL (Open Security Controls Assessment Language) integration for MapOSCAL.

This module provides OSCAL data models, serialization, and validation capabilities
for generating compliant OSCAL Component Definitions from Argo CD applications.

Key Components:
- OSCAL data models using compliance-trestle
- JSON serialization for OSCAL output
- Schema validation and compliance checking
- Integration with MapOSCAL execution results
"""

from .models import (
    OSCALComponentDefinition,
    OSCALComponent,
    OSCALCapability,
    OSCALControlImplementation,
    OSCALMetadata
)

from .serializer import OSCALSerializer
from .validator import OSCALValidator

__all__ = [
    'OSCALComponentDefinition',
    'OSCALComponent', 
    'OSCALCapability',
    'OSCALControlImplementation',
    'OSCALMetadata',
    'OSCALSerializer',
    'OSCALValidator'
]
