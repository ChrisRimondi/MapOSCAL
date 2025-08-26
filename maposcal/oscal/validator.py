"""
OSCAL Validator for MapOSCAL.

This module provides validation capabilities for OSCAL Component Definitions,
ensuring they comply with OSCAL schema requirements.
"""

import json
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class OSCALValidator:
    """Validator for OSCAL Component Definitions."""
    
    def __init__(self):
        """Initialize the validator."""
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_component_definition(self, oscal_data: Dict[str, Any]) -> bool:
        """
        Validate an OSCAL Component Definition.
        
        Args:
            oscal_data: OSCAL data as dictionary
            
        Returns:
            True if valid, False otherwise
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        try:
            # Check top-level structure
            if not self._validate_top_level(oscal_data):
                return False
            
            # Get component definition
            comp_def = oscal_data.get("component-definition", {})
            
            # Validate metadata
            if not self._validate_metadata(comp_def.get("metadata", {})):
                return False
            
            # Validate components
            if not self._validate_components(comp_def.get("components", [])):
                return False
            
            # Validate capabilities
            if not self._validate_capabilities(comp_def.get("capabilities", [])):
                return False
            
            # Validate control implementations (placeholder for future RAG flow)
            if not self._validate_control_implementations(comp_def.get("control-implementations", [])):
                return False
            
            # Check for warnings
            if self.validation_warnings:
                logger.warning(f"Validation completed with {len(self.validation_warnings)} warnings")
                for warning in self.validation_warnings:
                    logger.warning(f"  - {warning}")
            
            if self.validation_errors:
                logger.error(f"Validation failed with {len(self.validation_errors)} errors")
                for error in self.validation_errors:
                    logger.error(f"  - {error}")
                return False
            
            logger.info("OSCAL Component Definition validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            self.validation_errors.append(f"Validation exception: {str(e)}")
            return False
    
    def _validate_top_level(self, oscal_data: Dict[str, Any]) -> bool:
        """Validate top-level OSCAL structure."""
        
        if "component-definition" not in oscal_data:
            self.validation_errors.append("Missing 'component-definition' at top level")
            return False
        
        comp_def = oscal_data["component-definition"]
        
        # Check required fields
        required_fields = ["uuid", "metadata", "components"]
        for field in required_fields:
            if field not in comp_def:
                self.validation_errors.append(f"Missing required field '{field}' in component definition")
                return False
        
        return True
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata section."""
        
        if not metadata:
            self.validation_errors.append("Metadata section is empty")
            return False
        
        # Check required metadata fields
        required_fields = ["title", "oscal-version"]
        for field in required_fields:
            if field not in metadata:
                self.validation_errors.append(f"Missing required metadata field '{field}'")
                return False
        
        # Validate OSCAL version
        oscal_version = metadata.get("oscal-version")
        if oscal_version not in ["1.0.0", "1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.1.0", "1.1.1", "1.1.2", "1.1.3"]:
            self.validation_warnings.append(f"OSCAL version '{oscal_version}' may not be supported")
        
        # Check for MapOSCAL-specific properties
        properties = metadata.get("properties", [])
        maposcal_props = [p for p in properties if p.get("name", "").startswith("maposcal-")]
        if not maposcal_props:
            self.validation_warnings.append("No MapOSCAL-specific properties found in metadata")
        
        return True
    
    def _validate_components(self, components: List[Dict[str, Any]]) -> bool:
        """Validate components section."""
        
        if not components:
            self.validation_warnings.append("No components defined")
            return True  # Components are optional in some cases
        
        for i, component in enumerate(components):
            if not self._validate_single_component(component, f"component[{i}]"):
                return False
        
        return True
    
    def _validate_single_component(self, component: Dict[str, Any], component_path: str) -> bool:
        """Validate a single component."""
        
        # Check required component fields
        required_fields = ["uuid", "title", "type"]
        for field in required_fields:
            if field not in component:
                self.validation_errors.append(f"Missing required field '{field}' in {component_path}")
                return False
        
        # Validate UUID format
        uuid_val = component.get("uuid")
        if not self._is_valid_uuid(uuid_val):
            self.validation_errors.append(f"Invalid UUID format in {component_path}: {uuid_val}")
            return False
        
        # Check component type
        comp_type = component.get("type")
        valid_types = ["service", "application", "system", "hardware", "software"]
        if comp_type not in valid_types:
            self.validation_warnings.append(f"Component type '{comp_type}' in {component_path} may not be standard")
        
        # Validate properties if present
        props = component.get("props", [])
        for j, prop in enumerate(props):
            if not isinstance(prop, dict) or "name" not in prop or "value" not in prop:
                self.validation_errors.append(f"Invalid property format in {component_path}.props[{j}]")
                return False
        
        return True
    
    def _validate_capabilities(self, capabilities: List[Dict[str, Any]]) -> bool:
        """Validate capabilities section."""
        
        if not capabilities:
            self.validation_warnings.append("No capabilities defined")
            return True  # Capabilities are optional
        
        for i, capability in enumerate(capabilities):
            if not self._validate_single_capability(capability, f"capability[{i}]"):
                return False
        
        return True
    
    def _validate_single_capability(self, capability: Dict[str, Any], capability_path: str) -> bool:
        """Validate a single capability."""
        
        # Check required capability fields
        required_fields = ["uuid", "name"]
        for field in required_fields:
            if field not in capability:
                self.validation_errors.append(f"Missing required field '{field}' in {capability_path}")
                return False
        
        # Validate UUID format
        uuid_val = capability.get("uuid")
        if not self._is_valid_uuid(uuid_val):
            self.validation_errors.append(f"Invalid UUID format in {capability_path}: {uuid_val}")
            return False
        
        return True
    
    def _validate_control_implementations(self, control_impls: List[Dict[str, Any]]) -> bool:
        """Validate control implementations section (placeholder for future RAG flow)."""
        
        if not control_impls:
            # Control implementations are optional for now
            return True
        
        for i, control_impl in enumerate(control_impls):
            if not self._validate_single_control_implementation(control_impl, f"control-implementation[{i}]"):
                return False
        
        return True
    
    def _validate_single_control_implementation(self, control_impl: Dict[str, Any], control_path: str) -> bool:
        """Validate a single control implementation (placeholder for future RAG flow)."""
        
        # Basic validation for now - will be enhanced when RAG flow is implemented
        required_fields = ["uuid", "control-id"]
        for field in required_fields:
            if field not in control_impl:
                self.validation_errors.append(f"Missing required field '{field}' in {control_path}")
                return False
        
        # Validate UUID format
        uuid_val = control_impl.get("uuid")
        if not self._is_valid_uuid(uuid_val):
            self.validation_errors.append(f"Invalid UUID format in {control_path}: {uuid_val}")
            return False
        
        return True
    
    def _is_valid_uuid(self, uuid_val: str) -> bool:
        """Check if a string is a valid UUID."""
        if not isinstance(uuid_val, str):
            return False
        
        # Basic UUID format check (8-4-4-4-12 format)
        import re
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(uuid_val))
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation results."""
        return {
            "valid": len(self.validation_errors) == 0,
            "error_count": len(self.validation_errors),
            "warning_count": len(self.validation_warnings),
            "errors": self.validation_errors.copy(),
            "warnings": self.validation_warnings.copy()
        }


def validate_oscal_file(file_path: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Convenience function to validate an OSCAL file.
    
    Args:
        file_path: Path to the OSCAL JSON file
        
    Returns:
        Tuple of (is_valid, validation_summary)
    """
    try:
        # Read the file
        with open(file_path, 'r') as f:
            oscal_data = json.load(f)
        
        # Validate
        validator = OSCALValidator()
        is_valid = validator.validate_component_definition(oscal_data)
        summary = validator.get_validation_summary()
        
        return is_valid, summary
        
    except FileNotFoundError:
        logger.error(f"OSCAL file not found: {file_path}")
        return False, {"error": "File not found"}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in OSCAL file: {e}")
        return False, {"error": f"Invalid JSON: {e}"}
    except Exception as e:
        logger.error(f"Error validating OSCAL file: {e}")
        return False, {"error": f"Validation error: {e}"}
