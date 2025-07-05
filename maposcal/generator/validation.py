"""
maposcal.generator.validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive validation module for OSCAL component definitions.

This module provides Pydantic V2 schemas and validation functions to ensure
OSCAL component definitions meet structural and content requirements.

Key Features:
- Pydantic V2 field validators for type safety
- Control status validation against allowed values
- Configuration structure validation with file extension checking
- UUID format validation
- Cross-reference validation between control status and configuration
- Comprehensive error reporting with suggestions

Usage:
    from maposcal.generator.validation import validate_implemented_requirement

    is_valid, violations = validate_implemented_requirement(requirement_dict)
    if not is_valid:
        for violation in violations:
            print(f"{violation['field']}: {violation['issue']}")
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Any
import re
import uuid


class Prop(BaseModel):
    """
    OSCAL Property model with flexible value types.

    Supports string, list of strings, list of objects, or single object values
    to accommodate different OSCAL property requirements.
    """

    name: str
    value: Union[str, List[str], List[dict], dict]
    ns: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        """
        Validate property value based on its type.

        Args:
            v: The value to validate

        Returns:
            The validated value

        Raises:
            ValueError: If value format is invalid
        """
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            # For control-configuration, allow objects with file_path, key_path, line_number
            if v and isinstance(v[0], dict):
                # This is likely control-configuration with objects
                for item in v:
                    if not isinstance(item, dict):
                        raise ValueError(
                            "All items in object list must be dictionaries"
                        )
                return v
            else:
                # Regular string list (for source-code-reference)
                if not all(isinstance(item, str) for item in v):
                    raise ValueError("All items in value list must be strings")
                return v
        elif isinstance(v, dict):
            return v
        else:
            raise ValueError(
                "Value must be either a string, list of strings, list of objects, or object"
            )


class Annotation(BaseModel):
    """
    OSCAL Annotation model for metadata and references.

    Values are always converted to lists for consistency.
    """

    name: str
    value: Union[str, List[str]]
    ns: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        """
        Convert single strings to lists and validate list contents.

        Args:
            v: The value to validate

        Returns:
            List of strings

        Raises:
            ValueError: If value format is invalid
        """
        if isinstance(v, str):
            return [v]  # Convert single string to list
        elif isinstance(v, list):
            # Ensure all items in the list are strings
            if not all(isinstance(item, str) for item in v):
                raise ValueError("All items in value list must be strings")
            return v
        else:
            raise ValueError("Value must be either a string or a list of strings")


class Statement(BaseModel):
    """
    OSCAL Statement model for control implementation details.

    Includes UUID validation for statement identifiers.
    """

    statement_id: str = Field(..., alias="statement-id")
    uuid: str
    description: str

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v):
        """
        Validate UUID format.

        Args:
            v: UUID string to validate

        Returns:
            Validated UUID string

        Raises:
            ValueError: If UUID format is invalid
        """
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid UUID format")


class ControlMapping(BaseModel):
    """
    Main OSCAL Control Mapping model.

    Represents a complete implemented requirement with all required properties,
    optional annotations, and optional statements.
    """

    uuid: str
    control_id: str = Field(..., alias="control-id")
    props: List[Prop]
    annotations: Optional[List[Annotation]] = None
    statements: Optional[List[Statement]] = None

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v):
        """
        Validate main control UUID format.

        Args:
            v: UUID string to validate

        Returns:
            Validated UUID string

        Raises:
            ValueError: If UUID format is invalid
        """
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid UUID format")

    @field_validator("props")
    @classmethod
    def validate_required_props(cls, props):
        """
        Ensure all required OSCAL properties are present.

        Required properties:
        - control-status: Current status of the control
        - control-name: Human-readable name of the control
        - control-description: Description of the control
        - control-explanation: Explanation of implementation
        - control-configuration: Configuration details (if applicable)

        Args:
            props: List of Prop objects

        Returns:
            Validated props list

        Raises:
            ValueError: If required properties are missing
        """
        required_props = {
            "control-status",
            "control-name",
            "control-description",
            "control-explanation",
            "control-configuration",
        }
        prop_names = {p.name for p in props}
        missing = required_props - prop_names
        if missing:
            raise ValueError(f"Missing required properties: {missing}")
        return props

    @field_validator("props")
    @classmethod
    def validate_control_status_values(cls, props):
        """
        Validate that control-status has one of the allowed values.

        Allowed values:
        - "applicable and inherently satisfied"
        - "applicable but only satisfied through configuration"
        - "applicable but partially satisfied"
        - "applicable and not satisfied"
        - "not applicable"

        Args:
            props: List of Prop objects

        Returns:
            Validated props list

        Raises:
            ValueError: If control-status value is invalid
        """
        ALLOWED_STATUSES = {
            "applicable and inherently satisfied",
            "applicable but only satisfied through configuration",
            "applicable but partially satisfied",
            "applicable and not satisfied",
            "not applicable",
        }

        for prop in props:
            if prop.name == "control-status":
                if isinstance(prop.value, str):
                    if prop.value not in ALLOWED_STATUSES:
                        raise ValueError(
                            f'Invalid control-status value: {prop.value}. Must be one of: {", ".join(sorted(ALLOWED_STATUSES))}'
                        )
                elif isinstance(prop.value, list):
                    if not prop.value or not all(
                        status in ALLOWED_STATUSES for status in prop.value
                    ):
                        raise ValueError(
                            f'Invalid control-status values: {prop.value}. All values must be one of: {", ".join(sorted(ALLOWED_STATUSES))}'
                        )
                else:
                    raise ValueError(
                        f"Invalid control-status format: {type(prop.value)}. Must be string or list of strings"
                    )
        return props

    @field_validator("props")
    @classmethod
    def validate_configuration_structure(cls, props):
        """
        Validate control-configuration structure and file extensions.

        Validates:
        - Configuration is an array of objects
        - Each object has required keys: file_path, key_path, line_number
        - File paths have allowed extensions
        - Line numbers are integers
        - No documentation files (.md, .txt) are used

        Args:
            props: List of Prop objects

        Returns:
            Validated props list

        Raises:
            ValueError: If configuration structure is invalid
        """
        # Use configurable extensions from settings, with fallback to defaults
        try:
            from maposcal import settings
            ALLOWED_EXTENSIONS = set(settings.config_file_extensions)
        except ImportError:
            # Fallback to default extensions if settings import fails
            ALLOWED_EXTENSIONS = {
                ".yaml", ".yml", ".json", ".toml", ".conf", ".ini", ".properties"
            }
        
        # Add common code file extensions
        ALLOWED_EXTENSIONS.update({
            ".py", ".js", ".ts", ".go", ".java", ".cpp", ".c", ".h", 
            ".cs", ".php", ".rb", ".pl", ".sh", ".bash", ".ps1"
        })

        for prop in props:
            if prop.name == "control-configuration":
                if not isinstance(prop.value, list):
                    raise ValueError("control-configuration.value must be an array")

                # Validate each configuration object
                for i, config_obj in enumerate(prop.value):
                    if not isinstance(config_obj, dict):
                        raise ValueError(
                            f"control-configuration[{i}] must be an object"
                        )

                    # Check required keys
                    required_keys = {"file_path", "key_path", "line_number"}
                    missing_keys = required_keys - set(config_obj.keys())
                    if missing_keys:
                        raise ValueError(
                            f'control-configuration[{i}] missing required keys: {", ".join(missing_keys)}'
                        )

                    # Validate file_path extension
                    file_path = config_obj.get("file_path", "")
                    if file_path:
                        file_ext = (
                            "." + file_path.split(".")[-1].lower()
                            if "." in file_path
                            else ""
                        )
                        if file_ext not in ALLOWED_EXTENSIONS:
                            raise ValueError(
                                f'Invalid file extension in configuration[{i}]: {file_path}. Must end with: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
                            )

                        # Check for disallowed file types
                        if file_path.endswith((".md", ".txt")):
                            raise ValueError(
                                f"Documentation files not allowed in configuration[{i}]: {file_path}"
                            )

                    # Validate line_number is integer
                    line_number = config_obj.get("line_number")
                    if not isinstance(line_number, int):
                        raise ValueError(
                            f"line_number in configuration[{i}] must be an integer, got: {type(line_number)}"
                        )
        return props

    @field_validator("props")
    @classmethod
    def validate_configuration_consistency(cls, props):
        """
        Validate that control-configuration is consistent with control-status.

        Ensures that if control-status contains "configuration",
        control-configuration must be non-empty.

        Args:
            props: List of Prop objects

        Returns:
            Validated props list

        Raises:
            ValueError: If status and configuration are inconsistent
        """
        control_status = None
        control_config = None

        for prop in props:
            if prop.name == "control-status":
                control_status = prop.value
            elif prop.name == "control-configuration":
                control_config = prop.value

        if control_status and control_config is not None:
            # Check if status contains "configuration"
            status_contains_config = False
            if isinstance(control_status, str):
                status_contains_config = "configuration" in control_status.lower()
            elif isinstance(control_status, list):
                status_contains_config = any(
                    "configuration" in str(status).lower() for status in control_status
                )

            if status_contains_config and (
                not control_config or len(control_config) == 0
            ):
                raise ValueError(
                    'control-configuration must be non-empty when status contains "configuration"'
                )

        return props


def validate_control_mapping(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate a control mapping dictionary against the schema.

    This function uses the Pydantic ControlMapping model to validate
    the complete structure of an OSCAL implemented requirement.

    Args:
        data: The control mapping dictionary to validate

    Returns:
        tuple: (is_valid, error_message) where is_valid is boolean
               and error_message is None if valid, or a string describing the error
    """
    try:
        ControlMapping(**data)
        return True, None
    except Exception as e:
        return False, str(e)


def validate_unique_uuids(mappings: List[dict]) -> tuple[bool, Optional[str]]:
    """
    Validate that all UUIDs in a list of control mappings are unique.

    Checks both the main control UUID and any statement UUIDs
    to ensure no duplicates exist across the entire set.

    Args:
        mappings: List of control mapping dictionaries

    Returns:
        tuple: (is_valid, error_message) where is_valid is boolean
               and error_message is None if valid, or a string describing the duplicate
    """
    uuids = set()
    for mapping in mappings:
        # Check main UUID
        if mapping["uuid"] in uuids:
            return False, f'Duplicate UUID found: {mapping["uuid"]}'
        uuids.add(mapping["uuid"])

        # Check statement UUIDs
        for statement in mapping.get("statements", []):
            if statement["uuid"] in uuids:
                return False, f'Duplicate UUID found in statement: {statement["uuid"]}'
            uuids.add(statement["uuid"])

    return True, None


def validate_control_status(requirement: dict) -> tuple[bool, Optional[str]]:
    """
    Validate that the control-status field contains an allowable value.

    This is a focused validation function that specifically checks
    the control-status property against the allowed OSCAL values.

    Args:
        requirement: The implemented requirement dictionary

    Returns:
        tuple: (is_valid, error_message) where is_valid is boolean
               and error_message is None if valid, or a string describing the issue
    """
    ALLOWABLE_CONTROL_STATUSES = {
        "applicable and inherently satisfied",
        "applicable but only satisfied through configuration",
        "applicable but partially satisfied",
        "applicable and not satisfied",
        "not applicable",
    }

    # Find the control-status prop
    control_status = None
    props = requirement.get("props", [])
    if props is None:
        return False, "Missing 'props' or 'props' is None"
    for prop in props:
        if prop.get("name") == "control-status":
            control_status = prop.get("value")
            break

    if control_status is None:
        return False, "Missing 'control-status' property"

    # Handle both string and list values
    if isinstance(control_status, str):
        if control_status not in ALLOWABLE_CONTROL_STATUSES:
            return (
                False,
                f"Invalid control-status value: '{control_status}'. Must be one of: {', '.join(sorted(ALLOWABLE_CONTROL_STATUSES))}",
            )
    elif isinstance(control_status, list):
        if not control_status or not all(
            status in ALLOWABLE_CONTROL_STATUSES for status in control_status
        ):
            return (
                False,
                f"Invalid control-status values: {control_status}. All values must be one of: {', '.join(sorted(ALLOWABLE_CONTROL_STATUSES))}",
            )
    else:
        return (
            False,
            f"Invalid control-status format: {type(control_status)}. Must be string or list of strings",
        )

    return True, None


def validate_control_configuration(requirement: dict) -> tuple[bool, list]:
    """
    Validate the control-configuration field according to OSCAL requirements.

    This function performs comprehensive validation of the control-configuration
    property, including structure, file extensions, and consistency with control-status.

    Args:
        requirement: The implemented requirement dictionary

    Returns:
        tuple: (is_valid, list_of_violations) where is_valid is boolean
               and list_of_violations contains detailed violation information
    """
    violations = []
    
    # Use configurable extensions from settings, with fallback to defaults
    try:
        from maposcal import settings
        ALLOWED_EXTENSIONS = set(settings.config_file_extensions)
    except ImportError:
        # Fallback to default extensions if settings import fails
        ALLOWED_EXTENSIONS = {
            ".yaml", ".yml", ".json", ".toml", ".conf", ".ini", ".properties"
        }
    
    # Add common code file extensions
    ALLOWED_EXTENSIONS.update({
        ".py", ".js", ".ts", ".go", ".java", ".cpp", ".c", ".h", 
        ".cs", ".php", ".rb", ".pl", ".sh", ".bash", ".ps1"
    })

    # Find control-status and control-configuration props
    control_status = None
    control_config = None
    props = requirement.get("props", [])
    if props is None:
        return False, [{
            "field": "props",
            "issue": "Missing required props field or props is None",
            "suggestion": "Add props field with required properties",
        }]
    for prop in props:
        if prop.get("name") == "control-status":
            control_status = prop.get("value")
        elif prop.get("name") == "control-configuration":
            control_config = prop.get("value")

    # Check if status contains "configuration"
    status_contains_config = False
    if isinstance(control_status, str):
        status_contains_config = "configuration" in control_status.lower()
    elif isinstance(control_status, list):
        status_contains_config = any(
            "configuration" in str(status).lower() for status in control_status
        )

    if status_contains_config:
        # If status contains "configuration", control-configuration must be non-empty
        if not control_config:
            violations.append(
                {
                    "field": "control-configuration",
                    "issue": "control-configuration must be non-empty when status contains 'configuration'",
                    "suggestion": "Add configuration details or change status to 'applicable and not satisfied'",
                }
            )
        elif isinstance(control_config, list) and not control_config:
            violations.append(
                {
                    "field": "control-configuration",
                    "issue": "control-configuration array must be non-empty when status contains 'configuration'",
                    "suggestion": "Add configuration objects or change status to 'applicable and not satisfied'",
                }
            )
        elif isinstance(control_config, list) and control_config:
            # Validate each configuration object
            for i, config_obj in enumerate(control_config):
                if not isinstance(config_obj, dict):
                    violations.append(
                        {
                            "field": f"control-configuration[{i}]",
                            "issue": "Configuration object must be a dictionary",
                            "suggestion": "Use object with file_path, key_path, line_number keys",
                        }
                    )
                    continue

                # Check required keys
                required_keys = {"file_path", "key_path", "line_number"}
                missing_keys = required_keys - set(config_obj.keys())
                if missing_keys:
                    violations.append(
                        {
                            "field": f"control-configuration[{i}]",
                            "issue": f"Missing required keys: {', '.join(missing_keys)}",
                            "suggestion": f"Add missing keys: {', '.join(missing_keys)}",
                        }
                    )

                # Validate file_path extension
                file_path = config_obj.get("file_path", "")
                if file_path:
                    file_ext = (
                        "." + file_path.split(".")[-1].lower()
                        if "." in file_path
                        else ""
                    )
                    if file_ext not in ALLOWED_EXTENSIONS:
                        violations.append(
                            {
                                "field": f"control-configuration[{i}].file_path",
                                "issue": f"Invalid file extension: {file_path}. Must end with: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                                "suggestion": f"Use a file with extension: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                            }
                        )

                    # Check for disallowed file types
                    if file_path.endswith((".md", ".txt")):
                        violations.append(
                            {
                                "field": f"control-configuration[{i}].file_path",
                                "issue": f"Documentation files not allowed: {file_path}",
                                "suggestion": "Use configuration or source code files only",
                            }
                        )

    return len(violations) == 0, violations


def validate_oscal_structure(requirement: dict) -> tuple[bool, list]:
    """
    Validate the overall OSCAL structure and required fields.

    This function checks the basic structure of an OSCAL implemented requirement,
    including required fields, UUID formats, and statement validation.

    Args:
        requirement: The implemented requirement dictionary

    Returns:
        tuple: (is_valid, list_of_violations) where is_valid is boolean
               and list_of_violations contains detailed violation information
    """
    violations = []

    # Check required top-level fields
    required_fields = {"uuid", "control-id", "props"}
    missing_fields = required_fields - set(requirement.keys())
    if missing_fields:
        violations.append(
            {
                "field": "root",
                "issue": f"Missing required fields: {', '.join(missing_fields)}",
                "suggestion": f"Add missing fields: {', '.join(missing_fields)}",
            }
        )

    # Check required props
    if "props" in requirement and requirement["props"] is not None:
        required_props = {
            "control-status",
            "control-name",
            "control-description",
            "control-explanation",
            "control-configuration",
        }
        prop_names = {prop.get("name", "") for prop in requirement.get("props", [])}
        missing_props = required_props - prop_names
        if missing_props:
            violations.append(
                {
                    "field": "props",
                    "issue": f"Missing required properties: {', '.join(missing_props)}",
                    "suggestion": f"Add missing properties: {', '.join(missing_props)}",
                }
            )
    elif "props" not in requirement or requirement["props"] is None:
        violations.append(
            {
                "field": "props",
                "issue": "Missing required props field or props is None",
                "suggestion": "Add props field with required properties",
            }
        )

    # Validate UUID format
    if "uuid" in requirement and requirement["uuid"] is not None:
        try:
            uuid.UUID(requirement["uuid"])
        except ValueError:
            violations.append(
                {
                    "field": "uuid",
                    "issue": f"Invalid UUID format: {requirement['uuid']}",
                    "suggestion": "Use valid UUID format (e.g., 123e4567-e89b-12d3-a456-426614174000)",
                }
            )
    elif "uuid" not in requirement or requirement["uuid"] is None:
        violations.append(
            {
                "field": "uuid",
                "issue": "Missing required uuid field or uuid is None",
                "suggestion": "Add valid UUID format (e.g., 123e4567-e89b-12d3-a456-426614174000)",
            }
        )

    # Validate statements if present
    if "statements" in requirement:
        for i, statement in enumerate(requirement["statements"]):
            if not isinstance(statement, dict):
                violations.append(
                    {
                        "field": f"statements[{i}]",
                        "issue": "Statement must be a dictionary",
                        "suggestion": "Use object with statement-id, uuid, description keys",
                    }
                )
                continue

            # Check statement UUID
            if "uuid" in statement:
                try:
                    uuid.UUID(statement["uuid"])
                except ValueError:
                    violations.append(
                        {
                            "field": f"statements[{i}].uuid",
                            "issue": f"Invalid statement UUID format: {statement['uuid']}",
                            "suggestion": "Use valid UUID format",
                        }
                    )

    return len(violations) == 0, violations


def validate_implemented_requirement(requirement: dict) -> tuple[bool, list]:
    """
    Comprehensive validation of an implemented requirement.

    This is the main validation function that combines all validation checks:
    - OSCAL structure validation
    - Control status validation
    - Control configuration validation

    Args:
        requirement: The implemented requirement dictionary

    Returns:
        tuple: (is_valid, list_of_violations) where is_valid is boolean
               and list_of_violations contains detailed violation information
               with field names, issues, and suggestions
    """
    all_violations = []

    # Validate OSCAL structure
    structure_valid, structure_violations = validate_oscal_structure(requirement)
    all_violations.extend(structure_violations)

    # Validate control-status
    status_valid, status_error = validate_control_status(requirement)
    if not status_valid:
        all_violations.append(
            {
                "field": "control-status",
                "issue": status_error,
                "suggestion": "Use one of the allowable control-status values",
            }
        )

    # Validate control-configuration
    config_valid, config_violations = validate_control_configuration(requirement)
    all_violations.extend(config_violations)

    return len(all_violations) == 0, all_violations
