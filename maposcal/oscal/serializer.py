"""
OSCAL Serializer for MapOSCAL.

This module handles serialization of OSCAL objects to JSON format,
with integration to compliance-trestle for validation and proper OSCAL structure.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .models import OSCALComponentDefinition, COMPLIANCE_TRESTLE_AVAILABLE

logger = logging.getLogger(__name__)


class OSCALSerializer:
    """Serializer for OSCAL objects to JSON format."""
    
    def __init__(self, use_compliance_trestle: bool = True):
        """
        Initialize the serializer.
        
        Args:
            use_compliance_trestle: Whether to use compliance-trestle for validation
        """
        self.use_compliance_trestle = use_compliance_trestle and COMPLIANCE_TRESTLE_AVAILABLE
        
        if self.use_compliance_trestle:
            logger.info("Using compliance-trestle for OSCAL serialization")
        else:
            logger.info("Using basic JSON serialization (compliance-trestle not available)")
    
    def serialize_component_definition(
        self, 
        component_def: OSCALComponentDefinition,
        output_path: Optional[str] = None
    ) -> str:
        """
        Serialize an OSCAL Component Definition to JSON.
        
        Args:
            component_def: The OSCAL Component Definition to serialize
            output_path: Optional path to save the JSON file
            
        Returns:
            JSON string representation of the component definition
        """
        try:
            if self.use_compliance_trestle:
                return self._serialize_with_compliance_trestle(component_def, output_path)
            else:
                return self._serialize_basic(component_def, output_path)
                
        except Exception as e:
            logger.error(f"Failed to serialize OSCAL Component Definition: {e}")
            # Fallback to basic serialization
            return self._serialize_basic(component_def, output_path)
    
    def _serialize_with_compliance_trestle(
        self, 
        component_def: OSCALComponentDefinition,
        output_path: Optional[str] = None
    ) -> str:
        """Serialize using compliance-trestle for proper OSCAL validation."""
        try:
            from trestle.oscal.component import ComponentDefinition
            from trestle.oscal.common import Metadata, Property
            from trestle.oscal.implementation_common import ControlImplementation
            
            # Convert our models to compliance-trestle models
            trestle_metadata = Metadata(
                title=component_def.metadata.title,
                version=component_def.metadata.version,
                oscal_version=component_def.metadata.oscal_version,
                published=component_def.metadata.published,
                last_modified=component_def.metadata.last_modified
            )
            
            # Add MapOSCAL properties
            for prop_data in component_def.metadata.to_dict().get("properties", []):
                trestle_metadata.props.append(
                    Property(name=prop_data["name"], value=prop_data["value"])
                )
            
            # Create trestle ComponentDefinition
            trestle_component_def = ComponentDefinition(
                uuid=component_def.uuid,
                metadata=trestle_metadata
            )
            
            # Convert components
            for comp in component_def.components:
                from trestle.oscal.component import Component
                trestle_comp = Component(
                    uuid=comp.uuid,
                    title=comp.title,
                    description=comp.description,
                    type=comp.component_type
                )
                
                # Add properties
                for prop_data in comp.props:
                    trestle_comp.props.append(
                        Property(name=prop_data["name"], value=prop_data["value"])
                    )
                
                trestle_component_def.components.append(trestle_comp)
            
            # Convert capabilities
            for cap in component_def.capabilities:
                from trestle.oscal.component import Capability
                trestle_cap = Capability(
                    uuid=cap.uuid,
                    name=cap.name,
                    description=cap.description
                )
                
                # Add properties
                for prop_data in cap.props:
                    trestle_cap.props.append(
                        Property(name=prop_data["name"], value=prop_data["value"])
                    )
                
                trestle_component_def.capabilities.append(trestle_cap)
            
            # Convert control implementations (placeholder for future RAG flow)
            for ci in component_def.control_implementations:
                trestle_ci = ControlImplementation(
                    uuid=ci.uuid,
                    control_id=ci.control_id,
                    description=ci.description
                )
                trestle_component_def.control_implementations.append(trestle_ci)
            
            # Serialize to JSON
            json_str = trestle_component_def.json(exclude_none=True, indent=2)
            
            # Save to file if output path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(json_str)
                logger.info(f"OSCAL Component Definition saved to: {output_path}")
            
            return json_str
            
        except Exception as e:
            logger.warning(f"compliance-trestle serialization failed: {e}")
            # Fallback to basic serialization
            return self._serialize_basic(component_def, output_path)
    
    def _serialize_basic(
        self, 
        component_def: OSCALComponentDefinition,
        output_path: Optional[str] = None
    ) -> str:
        """Basic JSON serialization without compliance-trestle."""
        
        # Convert to dictionary
        oscal_dict = {
            "component-definition": component_def.to_dict()
        }
        
        # Serialize to JSON
        json_str = json.dumps(oscal_dict, indent=2, default=str)
        
        # Save to file if output path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json_str)
            logger.info(f"OSCAL Component Definition saved to: {output_path}")
        
        return json_str
    
    def validate_json_structure(self, json_str: str) -> bool:
        """
        Basic validation of JSON structure.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            data = json.loads(json_str)
            
            # Check required top-level structure
            if "component-definition" not in data:
                logger.error("Missing 'component-definition' in OSCAL JSON")
                return False
            
            comp_def = data["component-definition"]
            
            # Check required fields
            required_fields = ["uuid", "metadata", "components"]
            for field in required_fields:
                if field not in comp_def:
                    logger.error(f"Missing required field '{field}' in component definition")
                    return False
            
            # Check metadata structure
            metadata = comp_def["metadata"]
            if "title" not in metadata or "oscal-version" not in metadata:
                logger.error("Missing required metadata fields")
                return False
            
            logger.info("OSCAL JSON structure validation passed")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False


def serialize_oscal_to_file(
    component_def: OSCALComponentDefinition,
    output_path: str,
    use_compliance_trestle: bool = True
) -> bool:
    """
    Convenience function to serialize OSCAL to a file.
    
    Args:
        component_def: The OSCAL Component Definition to serialize
        output_path: Path to save the JSON file
        use_compliance_trestle: Whether to use compliance-trestle
        
    Returns:
        True if successful, False otherwise
    """
    try:
        serializer = OSCALSerializer(use_compliance_trestle=use_compliance_trestle)
        json_str = serializer.serialize_component_definition(component_def, output_path)
        
        # Validate the generated JSON
        if serializer.validate_json_structure(json_str):
            logger.info(f"Successfully generated OSCAL Component Definition: {output_path}")
            return True
        else:
            logger.error("Generated OSCAL JSON failed validation")
            return False
            
    except Exception as e:
        logger.error(f"Failed to serialize OSCAL to file: {e}")
        return False
