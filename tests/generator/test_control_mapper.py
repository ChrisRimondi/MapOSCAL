"""
Tests for the template-based control mapping functionality.

This module tests the new template-based approach that ensures structural integrity
while allowing the LLM to focus on content generation.
"""

import uuid
from maposcal.generator.control_mapper import (
    create_control_template,
    merge_llm_content,
    validate_content_quality,
)


class TestControlTemplate:
    """Test the control template creation functionality."""

    def test_create_control_template(self):
        """Test creating a control template with all required structural elements."""
        control_id = "AC-1"
        control_name = "Access Control Policy and Procedures"
        control_description = "The organization develops, documents, and disseminates access control policy."
        main_uuid = str(uuid.uuid4())
        statement_uuid = str(uuid.uuid4())

        template = create_control_template(
            control_id, control_name, control_description, main_uuid, statement_uuid
        )

        # Check required top-level fields
        assert template["uuid"] == main_uuid
        assert template["control-id"] == control_id

        # Check required props
        props = template["props"]
        prop_names = {prop["name"] for prop in props}
        required_props = {
            "control-status",
            "control-name",
            "control-description",
            "control-explanation",
            "control-configuration",
        }
        assert required_props.issubset(prop_names)

        # Check control-name and control-description are populated
        for prop in props:
            if prop["name"] == "control-name":
                assert prop["value"] == control_name
            elif prop["name"] == "control-description":
                assert prop["value"] == control_description
            elif prop["name"] == "control-status":
                assert prop["value"] == "applicable and not satisfied"  # Default

        # Check statements
        assert len(template["statements"]) == 1
        statement = template["statements"][0]
        assert statement["statement-id"] == f"{control_id}_smt.a"
        assert statement["uuid"] == statement_uuid
        assert statement["description"] == ""  # LLM fills this

        # Check annotations
        assert len(template["annotations"]) == 1
        annotation = template["annotations"][0]
        assert annotation["name"] == "source-code-reference"
        assert annotation["value"] == []  # Will be populated based on evidence


class TestContentMerging:
    """Test the LLM content merging functionality."""

    def test_merge_llm_content(self):
        """Test merging LLM-generated content into template."""
        # Create template
        control_id = "AC-1"
        control_name = "Access Control Policy and Procedures"
        control_description = "The organization develops, documents, and disseminates access control policy."
        main_uuid = str(uuid.uuid4())
        statement_uuid = str(uuid.uuid4())

        template = create_control_template(
            control_id, control_name, control_description, main_uuid, statement_uuid
        )

        # Create LLM content
        llm_content = {
            "control-status": "applicable and inherently satisfied",
            "control-explanation": "The system implements comprehensive access control through JWT authentication.",
            "control-configuration": [
                {
                    "file_path": "auth.py",
                    "key_path": "authentication.enabled",
                    "line_number": 42,
                }
            ],
            "statement-description": "Access control is implemented using JWT tokens with role-based permissions.",
        }

        # Create mock evidence chunks
        relevant_chunks = [
            {"source_file": "auth.py", "content": "JWT authentication code"},
            {"source_file": "config.yaml", "content": "Authentication configuration"},
        ]

        # Merge content
        result = merge_llm_content(template, llm_content, relevant_chunks)

        # Verify content was merged correctly
        for prop in result["props"]:
            if prop["name"] == "control-status":
                assert prop["value"] == "applicable and inherently satisfied"
            elif prop["name"] == "control-explanation":
                assert (
                    prop["value"]
                    == "The system implements comprehensive access control through JWT authentication."
                )
            elif prop["name"] == "control-configuration":
                assert len(prop["value"]) == 1
                assert prop["value"][0]["file_path"] == "auth.py"

        # Verify statement description was updated
        assert (
            result["statements"][0]["description"]
            == "Access control is implemented using JWT tokens with role-based permissions."
        )

        # Verify source code references were populated
        source_files = result["annotations"][0]["value"]
        assert "auth.py" in source_files
        assert "config.yaml" in source_files

        # Verify structural integrity is maintained
        assert result["uuid"] == main_uuid
        assert result["control-id"] == control_id


class TestContentValidation:
    """Test the content quality validation functionality."""

    def test_validate_content_quality_valid(self):
        """Test content validation with valid content."""
        llm_content = {
            "control-status": "applicable and inherently satisfied",
            "control-explanation": "The system implements comprehensive access control through JWT authentication and role-based permissions.",
            "control-configuration": [],
            "statement-description": "Access control is implemented using JWT tokens with role-based permissions and secure session management.",
        }

        is_valid, issues = validate_content_quality(llm_content)
        assert is_valid
        assert len(issues) == 0

    def test_validate_content_quality_missing_status(self):
        """Test content validation with missing control status."""
        llm_content = {
            "control-explanation": "The system implements access control.",
            "control-configuration": [],
            "statement-description": "Access control is implemented.",
        }

        is_valid, issues = validate_content_quality(llm_content)
        assert not is_valid
        assert "Missing control-status" in issues

    def test_validate_content_quality_invalid_status(self):
        """Test content validation with invalid control status."""
        llm_content = {
            "control-status": "invalid status",
            "control-explanation": "The system implements access control.",
            "control-configuration": [],
            "statement-description": "Access control is implemented.",
        }

        is_valid, issues = validate_content_quality(llm_content)
        assert not is_valid
        assert "Invalid control-status" in issues[0]

    def test_validate_content_quality_short_explanation(self):
        """Test content validation with short explanation."""
        llm_content = {
            "control-status": "applicable and inherently satisfied",
            "control-explanation": "Short",
            "control-configuration": [],
            "statement-description": "Access control is implemented.",
        }

        is_valid, issues = validate_content_quality(llm_content)
        assert not is_valid
        assert "Control explanation is too short or missing" in issues

    def test_validate_content_quality_configuration_consistency(self):
        """Test content validation with configuration consistency."""
        llm_content = {
            "control-status": "applicable but only satisfied through configuration",
            "control-explanation": "The system implements access control through configuration.",
            "control-configuration": [],  # Empty when status contains "configuration"
            "statement-description": "Access control is implemented through configuration.",
        }

        is_valid, issues = validate_content_quality(llm_content)
        assert not is_valid
        assert (
            "Control status indicates configuration but no configuration provided"
            in issues
        )

    def test_validate_content_quality_valid_with_configuration(self):
        """Test content validation with valid configuration."""
        llm_content = {
            "control-status": "applicable but only satisfied through configuration",
            "control-explanation": "The system implements access control through configuration.",
            "control-configuration": [
                {
                    "file_path": "config.yaml",
                    "key_path": "auth.enabled",
                    "line_number": 10,
                }
            ],
            "statement-description": "Access control is implemented through configuration.",
        }

        is_valid, issues = validate_content_quality(llm_content)
        assert is_valid
        assert len(issues) == 0
