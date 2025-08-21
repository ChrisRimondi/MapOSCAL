"""
Argo CD Application support module for MapOSCAL.

This module provides functionality to parse Argo CD Application resources,
process Kubernetes manifests, and group related workloads for OSCAL generation.
"""

from .parser import ArgoCDParser
from .manifest_processor import ManifestProcessor
from .workload_grouper import WorkloadGrouper

__all__ = [
    "ArgoCDParser",
    "ManifestProcessor", 
    "WorkloadGrouper",
]
