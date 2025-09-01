"""
Tests for compliance-trestle integration.

Tests the conversion from MapOSCAL format to compliance-trestle OSCAL models.
"""

import pytest
import json
import tempfile
import os
import uuid
from unittest.mock import patch

from maposcal.generator.trestle_integration import (
    convert_implemented_requirement,
    create_oscal_component,
    validate_oscal_structure,
    serialize_oscal_component,
    create_oscal_component_from_maposcal_output
)


class TestTrestleIntegration:
    """Test compliance-trestle integration functionality."""
    
    def test_convert_implemented_requirement(self):
        """Test converting a MapOSCAL requirement to compliance-trestle model."""
        # Sample MapOSCAL format requirement with valid UUIDs
        req_dict = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "description": "Access Control Policy and Procedures",
            "props": [
                {
                    "name": "control-status",
                    "value": "applicable and inherently satisfied",
                    "ns": "https://maposcal.org/ns/control-status-reference"
                },
                {
                    "name": "control-explanation",
                    "value": "Access control is implemented through JWT tokens",
                    "ns": "https://maposcal.org/ns/explanation-reference"
                }
            ],
            "statements": [
                {
                    "statement-id": "AC-1_smt.a",
                    "uuid": str(uuid.uuid4()),
                    "description": "Access control policy is implemented"
                }
            ]
        }
        
        # Convert to compliance-trestle model
        impl_req = convert_implemented_requirement(req_dict)
        
        # Verify the conversion
        assert impl_req.uuid == req_dict["uuid"]
        assert impl_req.control_id == req_dict["control-id"]
        assert impl_req.description == req_dict["description"]
        assert len(impl_req.props) == 2
        assert len(impl_req.statements) == 1
        
        # Verify properties
        status_prop = next(p for p in impl_req.props if p.name == "control-status")
        assert status_prop.value == "applicable and inherently satisfied"
        
        # Verify statements
        assert impl_req.statements[0].statement_id == "AC-1_smt.a"
    
    def test_create_oscal_component(self):
        """Test creating a complete OSCAL component definition."""
        # Sample implemented requirements with valid UUIDs
        implemented_requirements = [
            {
                "uuid": str(uuid.uuid4()),
                "control-id": "AC-1",
                "description": "Access Control Policy",
                "props": [
                    {
                        "name": "control-status",
                        "value": "applicable and inherently satisfied",
                        "ns": "https://maposcal.org/ns/control-status-reference"
                    }
                ],
                "statements": [
                    {
                        "statement-id": "AC-1_smt.a",
                        "uuid": str(uuid.uuid4()),
                        "description": "Access control implemented"
                    }
                ]
            }
        ]
        
        # Create OSCAL component
        comp_def = create_oscal_component(
            implemented_requirements,
            component_title="Test Component",
            component_description="Test component description"
        )
        
        # Verify the component structure
        assert comp_def.uuid is not None
        assert comp_def.metadata.title == "Test Component"
        assert comp_def.metadata.version == "1.0.0"
        assert comp_def.metadata.oscal_version.__root__ == "1.1.3"
        
        # Verify components
        assert len(comp_def.components) == 1
        component = comp_def.components[0]
        assert component.title == "Test Component"
        assert component.type == "application"
        
        # Verify control implementations
        assert len(component.control_implementations) == 1
        control_impl = component.control_implementations[0]
        assert control_impl.source == "NIST SP 800-53 Rev. 5"
        assert len(control_impl.implemented_requirements) == 1
    
    def test_validate_oscal_structure(self):
        """Test OSCAL structure validation."""
        # Create a valid component with valid UUIDs
        implemented_requirements = [
            {
                "uuid": str(uuid.uuid4()),
                "control-id": "AC-1",
                "description": "Access Control Policy",
                "props": [
                    {
                        "name": "control-status",
                        "value": "applicable and inherently satisfied",
                        "ns": "https://maposcal.org/ns/control-status-reference"
                    }
                ],
                "statements": [
                    {
                        "statement-id": "AC-1_smt.a",
                        "uuid": str(uuid.uuid4()),
                        "description": "Access control implemented"
                    }
                ]
            }
        ]
        
        comp_def = create_oscal_component(implemented_requirements)
        
        # Validate structure
        assert validate_oscal_structure(comp_def) is True
    
    def test_serialize_oscal_component(self):
        """Test OSCAL component serialization."""
        implemented_requirements = [
            {
                "uuid": str(uuid.uuid4()),
                "control-id": "AC-1",
                "description": "Access Control Policy",
                "props": [
                    {
                        "name": "control-status",
                        "value": "applicable and inherently satisfied",
                        "ns": "https://maposcal.org/ns/control-status-reference"
                    }
                ],
                "statements": [
                    {
                        "statement-id": "AC-1_smt.a",
                        "uuid": str(uuid.uuid4()),
                        "description": "Access control implemented"
                    }
                ]
            }
        ]
        
        comp_def = create_oscal_component(implemented_requirements)
        
        # Serialize to JSON
        json_output = serialize_oscal_component(comp_def, pretty=True)
        
        # Verify it's valid JSON
        parsed = json.loads(json_output)
        assert "component-definition" in parsed
        
        # Verify structure
        comp_def_json = parsed["component-definition"]
        assert "uuid" in comp_def_json
        assert "metadata" in comp_def_json
        assert "components" in comp_def_json
    
    def test_create_oscal_component_from_maposcal_output(self):
        """Test creating OSCAL component from MapOSCAL output format."""
        maposcal_output = {
            "implemented_requirements": [
                {
                    "uuid": str(uuid.uuid4()),
                    "control-id": "AC-1",
                    "description": "Access Control Policy",
                    "props": [
                        {
                            "name": "control-status",
                            "value": "applicable and inherently satisfied",
                            "ns": "https://maposcal.org/ns/control-status-reference"
                        }
                    ],
                    "statements": [
                        {
                            "statement-id": "AC-1_smt.a",
                            "uuid": str(uuid.uuid4()),
                            "description": "Access control implemented"
                        }
                    ]
                }
            ]
        }
        
        comp_def = create_oscal_component_from_maposcal_output(maposcal_output)
        
        # Verify the component was created correctly
        assert comp_def.uuid is not None
        assert len(comp_def.components) == 1
        assert len(comp_def.components[0].control_implementations) == 1
        assert len(comp_def.components[0].control_implementations[0].implemented_requirements) == 1
    
    def test_create_oscal_component_from_empty_output(self):
        """Test handling of empty MapOSCAL output."""
        maposcal_output = {"implemented_requirements": []}
        
        with pytest.raises(ValueError, match="No implemented requirements found"):
            create_oscal_component_from_maposcal_output(maposcal_output)
    
    def test_convert_implemented_requirement_missing_fields(self):
        """Test handling of missing required fields."""
        req_dict = {
            "control-id": "AC-1",
            # Missing uuid
            "description": "Access Control Policy"
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            convert_implemented_requirement(req_dict)

    def test_convert_implemented_requirement_without_statements(self):
        """Test converting a requirement without statements."""
        req_dict = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "description": "Access Control Policy and Procedures",
            "props": [
                {
                    "name": "control-status",
                    "value": "applicable and inherently satisfied",
                    "ns": "https://maposcal.org/ns/control-status-reference"
                }
            ]
            # No statements
        }
        
        # Convert to compliance-trestle model
        impl_req = convert_implemented_requirement(req_dict)
        
        # Verify the conversion
        assert impl_req.uuid == req_dict["uuid"]
        assert impl_req.control_id == req_dict["control-id"]
        assert impl_req.description == req_dict["description"]
        assert len(impl_req.props) == 1
        assert impl_req.statements == []
