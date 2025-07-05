"""
Tests for the validation module.

This module tests the Pydantic models and validation functions used for
OSCAL component definitions.
"""

import pytest
import uuid
from pydantic import ValidationError
from maposcal.generator.validation import (
    Prop,
    Annotation,
    Statement,
    ControlMapping,
    validate_control_mapping,
    validate_unique_uuids,
    validate_control_status,
    validate_control_configuration,
    validate_oscal_structure,
    validate_implemented_requirement,
)


class TestProp:
    """Test the Prop model validation."""

    def test_prop_with_string_value(self):
        """Test Prop with string value."""
        prop = Prop(name="test-prop", value="test-value", ns="test-ns")
        assert prop.name == "test-prop"
        assert prop.value == "test-value"
        assert prop.ns == "test-ns"

    def test_prop_with_list_value(self):
        """Test Prop with list of strings."""
        prop = Prop(name="test-prop", value=["value1", "value2"], ns="test-ns")
        assert prop.value == ["value1", "value2"]

    def test_prop_with_object_list_value(self):
        """Test Prop with list of objects (for control-configuration)."""
        config_objects = [
            {"file_path": "config.yaml", "key_path": "auth.enabled", "line_number": 10},
            {"file_path": "settings.json", "key_path": "security.level", "line_number": 25}
        ]
        prop = Prop(name="control-configuration", value=config_objects, ns="test-ns")
        assert prop.value == config_objects

    def test_prop_with_dict_value(self):
        """Test Prop with dictionary value."""
        dict_value = {"key": "value", "nested": {"data": "test"}}
        prop = Prop(name="test-prop", value=dict_value, ns="test-ns")
        assert prop.value == dict_value

    def test_prop_invalid_value_type(self):
        """Test Prop with invalid value type."""
        with pytest.raises(ValidationError):
            Prop(name="test-prop", value=123, ns="test-ns")

    def test_prop_mixed_list_types(self):
        """Test Prop with mixed list types (should fail)."""
        with pytest.raises(ValidationError):
            Prop(name="test-prop", value=["string", 123], ns="test-ns")

    def test_prop_mixed_object_list_types(self):
        """Test Prop with mixed object list types (should fail)."""
        with pytest.raises(ValidationError):
            Prop(name="test-prop", value=[{"key": "value"}, "string"], ns="test-ns")


class TestAnnotation:
    """Test the Annotation model validation."""

    def test_annotation_with_string_value(self):
        """Test Annotation with string value (converts to list)."""
        annotation = Annotation(name="test-annotation", value="test-value", ns="test-ns")
        assert annotation.value == ["test-value"]

    def test_annotation_with_list_value(self):
        """Test Annotation with list of strings."""
        annotation = Annotation(name="test-annotation", value=["value1", "value2"], ns="test-ns")
        assert annotation.value == ["value1", "value2"]

    def test_annotation_with_mixed_list_types(self):
        """Test Annotation with mixed list types (should fail)."""
        with pytest.raises(ValidationError):
            Annotation(name="test-annotation", value=["string", 123], ns="test-ns")

    def test_annotation_with_invalid_value_type(self):
        """Test Annotation with invalid value type."""
        with pytest.raises(ValidationError):
            Annotation(name="test-annotation", value={"key": "value"}, ns="test-ns")


class TestStatement:
    """Test the Statement model validation."""

    def test_statement_with_valid_uuid(self):
        """Test Statement with valid UUID."""
        test_uuid = str(uuid.uuid4())
        statement = Statement(
            **{
                "statement-id": "test-statement",
                "uuid": test_uuid,
                "description": "Test statement description"
            }
        )
        assert statement.statement_id == "test-statement"
        assert statement.uuid == test_uuid
        assert statement.description == "Test statement description"

    def test_statement_with_invalid_uuid(self):
        """Test Statement with invalid UUID."""
        with pytest.raises(ValidationError):
            Statement(
                **{
                    "statement-id": "test-statement",
                    "uuid": "invalid-uuid",
                    "description": "Test statement description"
                }
            )


class TestControlMapping:
    """Test the ControlMapping model validation."""

    def test_control_mapping_with_minimal_required_props(self):
        """Test ControlMapping with minimal required properties."""
        test_uuid = str(uuid.uuid4())
        props = [
            Prop(name="control-status", value="applicable and inherently satisfied", ns="test-ns"),
            Prop(name="control-name", value="Test Control", ns="test-ns"),
            Prop(name="control-description", value="Test control description", ns="test-ns"),
            Prop(name="control-explanation", value="Test control explanation", ns="test-ns"),
            Prop(name="control-configuration", value=[], ns="test-ns"),
        ]

        control_mapping = ControlMapping(
            **{
                "uuid": test_uuid,
                "control-id": "AC-1",
                "props": props
            }
        )
        assert control_mapping.uuid == test_uuid
        assert control_mapping.control_id == "AC-1"
        assert len(control_mapping.props) == 5

    def test_control_mapping_with_optional_fields(self):
        """Test ControlMapping with optional annotations and statements."""
        test_uuid = str(uuid.uuid4())
        statement_uuid = str(uuid.uuid4())

        props = [
            Prop(name="control-status", value="applicable and inherently satisfied", ns="test-ns"),
            Prop(name="control-name", value="Test Control", ns="test-ns"),
            Prop(name="control-description", value="Test control description", ns="test-ns"),
            Prop(name="control-explanation", value="Test control explanation", ns="test-ns"),
            Prop(name="control-configuration", value=[], ns="test-ns"),
        ]

        annotations = [
            Annotation(name="test-annotation", value="test-value", ns="test-ns")
        ]

        statements = [
            Statement(
                **{
                    "statement-id": "test-statement",
                    "uuid": statement_uuid,
                    "description": "Test statement description"
                }
            )
        ]

        control_mapping = ControlMapping(
            **{
                "uuid": test_uuid,
                "control-id": "AC-1",
                "props": props,
                "annotations": annotations,
                "statements": statements
            }
        )
        assert len(control_mapping.annotations) == 1
        assert len(control_mapping.statements) == 1

    def test_control_mapping_missing_required_props(self):
        """Test ControlMapping with missing required properties."""
        test_uuid = str(uuid.uuid4())
        props = [
            Prop(name="control-status", value="applicable and inherently satisfied", ns="test-ns"),
            # Missing control-name, control-description, control-explanation, control-configuration
        ]

        with pytest.raises(ValidationError):
            ControlMapping(
                **{
                    "uuid": test_uuid,
                    "control-id": "AC-1",
                    "props": props
                }
            )

    def test_control_mapping_invalid_control_status(self):
        """Test ControlMapping with invalid control status."""
        test_uuid = str(uuid.uuid4())
        props = [
            Prop(name="control-status", value="invalid-status", ns="test-ns"),
            Prop(name="control-name", value="Test Control", ns="test-ns"),
            Prop(name="control-description", value="Test control description", ns="test-ns"),
            Prop(name="control-explanation", value="Test control explanation", ns="test-ns"),
            Prop(name="control-configuration", value=[], ns="test-ns"),
        ]

        with pytest.raises(ValidationError):
            ControlMapping(
                **{
                    "uuid": test_uuid,
                    "control-id": "AC-1",
                    "props": props
                }
            )

    def test_control_mapping_with_valid_configuration(self):
        """Test ControlMapping with valid configuration structure."""
        test_uuid = str(uuid.uuid4())
        config_objects = [
            {"file_path": "config.yaml", "key_path": "auth.enabled", "line_number": 10},
            {"file_path": "settings.json", "key_path": "security.level", "line_number": 25}
        ]
        
        props = [
            Prop(name="control-status", value="applicable and inherently satisfied", ns="test-ns"),
            Prop(name="control-name", value="Test Control", ns="test-ns"),
            Prop(name="control-description", value="Test control description", ns="test-ns"),
            Prop(name="control-explanation", value="Test control explanation", ns="test-ns"),
            Prop(name="control-configuration", value=config_objects, ns="test-ns"),
        ]

        control_mapping = ControlMapping(
            **{
                "uuid": test_uuid,
                "control-id": "AC-1",
                "props": props
            }
        )
        assert len(control_mapping.props) == 5


class TestValidationFunctions:
    """Test the validation functions."""

    def test_validate_control_mapping_valid(self):
        """Test validate_control_mapping with valid data."""
        test_uuid = str(uuid.uuid4())
        data = {
            "uuid": test_uuid,
            "control-id": "AC-1",
            "props": [
                {"name": "control-status", "value": "applicable and inherently satisfied", "ns": "test-ns"},
                {"name": "control-name", "value": "Test Control", "ns": "test-ns"},
                {"name": "control-description", "value": "Test control description", "ns": "test-ns"},
                {"name": "control-explanation", "value": "Test control explanation", "ns": "test-ns"},
                {"name": "control-configuration", "value": [], "ns": "test-ns"},
            ]
        }
        
        is_valid, error = validate_control_mapping(data)
        assert is_valid
        assert error is None

    def test_validate_control_mapping_invalid(self):
        """Test validate_control_mapping with invalid data."""
        data = {
            "uuid": "invalid-uuid",
            "control-id": "AC-1",
            "props": []
        }
        
        is_valid, error = validate_control_mapping(data)
        assert not is_valid
        assert error is not None

    def test_validate_unique_uuids_valid(self):
        """Test validate_unique_uuids with unique UUIDs."""
        test_uuid1 = str(uuid.uuid4())
        test_uuid2 = str(uuid.uuid4())
        
        mappings = [
            {"uuid": test_uuid1, "control-id": "AC-1"},
            {"uuid": test_uuid2, "control-id": "AC-2"},
        ]
        
        is_valid, error = validate_unique_uuids(mappings)
        assert is_valid
        assert error is None

    def test_validate_unique_uuids_duplicate(self):
        """Test validate_unique_uuids with duplicate UUIDs."""
        test_uuid = str(uuid.uuid4())
        
        mappings = [
            {"uuid": test_uuid, "control-id": "AC-1"},
            {"uuid": test_uuid, "control-id": "AC-2"},
        ]
        
        is_valid, error = validate_unique_uuids(mappings)
        assert not is_valid
        assert "Duplicate UUID" in error

    def test_validate_control_status_valid(self):
        """Test validate_control_status with valid status."""
        requirement = {
            "props": [
                {"name": "control-status", "value": "applicable and inherently satisfied", "ns": "test-ns"}
            ]
        }
        
        is_valid, error = validate_control_status(requirement)
        assert is_valid
        assert error is None

    def test_validate_control_status_invalid(self):
        """Test validate_control_status with invalid status."""
        requirement = {
            "props": [
                {"name": "control-status", "value": "invalid-status", "ns": "test-ns"}
            ]
        }
        
        is_valid, error = validate_control_status(requirement)
        assert not is_valid
        assert "Invalid control-status value" in error

    def test_validate_control_status_missing(self):
        """Test validate_control_status with missing status."""
        requirement = {
            "props": [
                {"name": "control-name", "value": "Test Control", "ns": "test-ns"}
            ]
        }
        
        is_valid, error = validate_control_status(requirement)
        assert not is_valid
        assert "Missing 'control-status' property" in error

    def test_validate_control_configuration_valid(self):
        """Test validate_control_configuration with valid structure."""
        requirement = {
            "props": [
                {"name": "control-configuration", "value": [
                    {"file_path": "config.yaml", "key_path": "auth.enabled", "line_number": 10}
                ], "ns": "test-ns"}
            ]
        }
        
        is_valid, violations = validate_control_configuration(requirement)
        assert is_valid
        assert len(violations) == 0

    def test_validate_control_configuration_invalid_structure(self):
        """Test validate_control_configuration with invalid structure."""
        requirement = {
            "props": [
                {"name": "control-status", "value": "applicable but only satisfied through configuration", "ns": "test-ns"},
                {"name": "control-configuration", "value": [
                    {"file_path": "test.py"}  # Missing required fields
                ], "ns": "test-ns"}
            ]
        }

        is_valid, violations = validate_control_configuration(requirement)
        assert not is_valid
        assert len(violations) > 0

    def test_validate_oscal_structure_valid(self):
        """Test validate_oscal_structure with valid structure."""
        requirement = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "props": [
                {"name": "control-status", "value": "applicable and inherently satisfied", "ns": "test-ns"},
                {"name": "control-name", "value": "Test Control", "ns": "test-ns"},
                {"name": "control-description", "value": "Test control description", "ns": "test-ns"},
                {"name": "control-explanation", "value": "Test control explanation", "ns": "test-ns"},
                {"name": "control-configuration", "value": [], "ns": "test-ns"},
            ]
        }
        
        is_valid, violations = validate_oscal_structure(requirement)
        assert is_valid
        assert len(violations) == 0

    def test_validate_oscal_structure_invalid(self):
        """Test validate_oscal_structure with invalid structure."""
        requirement = {
            "uuid": "invalid-uuid",
            "control-id": "AC-1",
            "props": []
        }
        
        is_valid, violations = validate_oscal_structure(requirement)
        assert not is_valid
        assert len(violations) > 0

    def test_validate_implemented_requirement_valid(self):
        """Test validate_implemented_requirement with valid requirement."""
        requirement = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "props": [
                {"name": "control-status", "value": "applicable and inherently satisfied", "ns": "test-ns"},
                {"name": "control-name", "value": "Test Control", "ns": "test-ns"},
                {"name": "control-description", "value": "Test control description", "ns": "test-ns"},
                {"name": "control-explanation", "value": "Test control explanation", "ns": "test-ns"},
                {"name": "control-configuration", "value": [], "ns": "test-ns"},
            ]
        }
        
        is_valid, violations = validate_implemented_requirement(requirement)
        assert is_valid
        assert len(violations) == 0

    def test_validate_implemented_requirement_invalid(self):
        """Test validate_implemented_requirement with invalid requirement."""
        requirement = {
            "uuid": "invalid-uuid",
            "control-id": "AC-1",
            "props": []
        }
        
        is_valid, violations = validate_implemented_requirement(requirement)
        assert not is_valid
        assert len(violations) > 0

    def test_validate_implemented_requirement_multiple_violations(self):
        """Test validate_implemented_requirement with multiple violations."""
        requirement = {
            "uuid": "invalid-uuid",
            "control-id": "AC-1",
            "props": [
                {"name": "control-status", "value": "invalid-status", "ns": "test-ns"},
                {"name": "control-configuration", "value": [
                    {"file_path": "test.py"}  # Missing required fields
                ], "ns": "test-ns"}
            ]
        }
        
        is_valid, violations = validate_implemented_requirement(requirement)
        assert not is_valid
        assert len(violations) >= 2  # Should have multiple violations


class TestValidationEdgeCases:
    """Test edge cases and error conditions."""

    def test_none_values(self):
        """Test validation with None values."""
        requirement = {
            "uuid": None,
            "control-id": None,
            "props": None
        }
        
        is_valid, violations = validate_implemented_requirement(requirement)
        assert not is_valid
        assert len(violations) > 0

    def test_empty_props(self):
        """Test validation with empty props list."""
        requirement = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "props": []
        }
        
        is_valid, violations = validate_implemented_requirement(requirement)
        assert not is_valid
        assert len(violations) > 0

    def test_malformed_props(self):
        """Test validation with malformed props."""
        requirement = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "props": [
                {"name": "control-status", "value": "applicable and inherently satisfied"},  # Missing ns
                {"name": "control-name", "ns": "test-ns"},  # Missing value
            ]
        }
        
        is_valid, violations = validate_implemented_requirement(requirement)
        assert not is_valid
        assert len(violations) > 0

    def test_very_long_values(self):
        """Test validation with very long values."""
        long_value = "x" * 10000
        requirement = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "props": [
                {"name": "control-status", "value": "applicable and inherently satisfied", "ns": "test-ns"},
                {"name": "control-name", "value": long_value, "ns": "test-ns"},
                {"name": "control-description", "value": long_value, "ns": "test-ns"},
                {"name": "control-explanation", "value": long_value, "ns": "test-ns"},
                {"name": "control-configuration", "value": [], "ns": "test-ns"},
            ]
        }
        
        is_valid, violations = validate_implemented_requirement(requirement)
        # Should still be valid, just with long values
        assert is_valid
        assert len(violations) == 0

    def test_special_characters_in_values(self):
        """Test validation with special characters in values."""
        special_value = "Test with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        requirement = {
            "uuid": str(uuid.uuid4()),
            "control-id": "AC-1",
            "props": [
                {"name": "control-status", "value": "applicable and inherently satisfied", "ns": "test-ns"},
                {"name": "control-name", "value": special_value, "ns": "test-ns"},
                {"name": "control-description", "value": special_value, "ns": "test-ns"},
                {"name": "control-explanation", "value": special_value, "ns": "test-ns"},
                {"name": "control-configuration", "value": [], "ns": "test-ns"},
            ]
        }

        is_valid, violations = validate_implemented_requirement(requirement)
        assert is_valid
        assert len(violations) == 0 