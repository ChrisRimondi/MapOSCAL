"""
maposcal.generator.security_section_mapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Security section mapping functionality for selective context injection.

This module provides functionality to map NIST 800-53 controls to relevant
security overview sections, enabling more focused and efficient control mapping
by only including relevant security context.

Key Features:
- Control family to security section mapping
- Security overview markdown parsing into sections
- Selective security context building for control mapping
- Graceful degradation to full overview if parsing fails

Functions:
- get_control_family: Extract control family from control ID
- get_relevant_security_sections: Get relevant sections for a control
- parse_security_overview_sections: Parse markdown into structured sections
- build_selective_security_overview_section: Build focused security context
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Mapping of NIST 800-53 control families to relevant security overview sections
CONTROL_SECURITY_SECTION_MAP = {
    # Access Control family - Authentication, Authorization, Identity Management
    "AC": ["service_overview", "authentication_authorization"],
    
    # Audit and Accountability - Logging, Monitoring, Audit trails
    "AU": ["service_overview", "audit_logging_monitoring"],
    
    # System and Communications Protection - Encryption, Data Protection
    "SC": ["service_overview", "encryption_data_protection"],
    
    # System and Information Integrity - may need encryption for integrity checks
    "SI": ["service_overview", "encryption_data_protection"],
    
    # Configuration Management - may need auth for change control
    "CM": ["service_overview", "authentication_authorization"],
    
    # Identification and Authentication - Authentication mechanisms
    "IA": ["service_overview", "authentication_authorization"],
    
    # System and Services Acquisition - may need multiple sections
    "SA": ["service_overview", "authentication_authorization", "encryption_data_protection"],
    
    # Planning - usually organizational, minimal tech context needed
    "PL": ["service_overview"],
    
    # Risk Assessment - may need multiple sections for comprehensive view
    "RA": ["service_overview", "authentication_authorization", "encryption_data_protection"],
    
    # Contingency Planning - may need logging for incident response
    "CP": ["service_overview", "audit_logging_monitoring"],
    
    # Incident Response - needs logging and monitoring capabilities
    "IR": ["service_overview", "audit_logging_monitoring"],
    
    # Media Protection - encryption for data protection
    "MP": ["service_overview", "encryption_data_protection"],
    
    # Physical and Environmental Protection - minimal tech context
    "PE": ["service_overview"],
    
    # Personnel Security - minimal tech context
    "PS": ["service_overview"],
    
    # System and Communications Protection - comprehensive sections
    "SC": ["service_overview", "encryption_data_protection"],
    
    # Default fallback for unknown control families
    "DEFAULT": ["service_overview"]
}

# Standard section headers that should be recognized in security overview markdown
SECTION_HEADERS = {
    "service_overview": ["# Service Overview", "## Service Overview", "# 1. Service Overview", "## 1. Service Overview"],
    "authentication_authorization": ["# Authentication and Authorization", "## Authentication and Authorization", 
                                   "# 2. Authentication and Authorization", "## 2. Authentication and Authorization"],
    "encryption_data_protection": ["# Encryption and Data Protection", "## Encryption and Data Protection",
                                 "# 3. Encryption and Data Protection", "## 3. Encryption and Data Protection"],
    "audit_logging_monitoring": ["# Audit Logging and Monitoring", "## Audit Logging and Monitoring",
                               "# 4. Audit Logging and Monitoring", "## 4. Audit Logging and Monitoring"]
}


def get_control_family(control_id: str) -> str:
    """
    Extract the control family from a NIST 800-53 control ID.
    
    Args:
        control_id: The NIST control ID (e.g., "AC-1", "AU-2", "SC-8")
        
    Returns:
        str: The control family (e.g., "AC", "AU", "SC")
    """
    if not control_id:
        return "DEFAULT"
    
    # Extract family from control ID (everything before the first hyphen)
    family = control_id.split("-")[0].upper()
    return family


def get_relevant_security_sections(control_id: str) -> List[str]:
    """
    Get the list of relevant security overview sections for a control.
    
    Args:
        control_id: The NIST control ID (e.g., "AC-1", "AU-2", "SC-8")
        
    Returns:
        List[str]: List of relevant section names for the control
    """
    family = get_control_family(control_id)
    sections = CONTROL_SECURITY_SECTION_MAP.get(family, CONTROL_SECURITY_SECTION_MAP["DEFAULT"])
    
    logger.info(f"Control {control_id} (family: {family}) mapped to sections: {sections}")
    return sections


def parse_security_overview_sections(security_overview_content: str) -> Dict[str, str]:
    """
    Parse the security overview markdown content into individual sections.
    
    This function splits the markdown content by headers and extracts each
    section's content for selective inclusion in control mapping prompts.
    
    Args:
        security_overview_content: The full security overview markdown content
        
    Returns:
        Dict[str, str]: Dictionary mapping section names to their content
    """
    if not security_overview_content:
        return {}
    
    sections = {}
    lines = security_overview_content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        # Check if this line is a section header
        section_found = None
        for section_name, headers in SECTION_HEADERS.items():
            for header in headers:
                if line.strip().startswith(header.strip()):
                    section_found = section_name
                    break
            if section_found:
                break
        
        if section_found:
            # Save previous section if we have one
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = section_found
            current_content = [line]  # Include the header
            logger.debug(f"Found section: {current_section}")
        else:
            # Add line to current section
            if current_section:
                current_content.append(line)
    
    # Save the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    logger.info(f"Parsed {len(sections)} sections from security overview")
    return sections


def build_selective_security_overview_section(
    control_id: str, 
    security_overview_sections: Dict[str, str]
) -> str:
    """
    Build a security overview section containing only relevant parts for the control.
    
    This function takes the parsed security overview sections and builds a focused
    security context that includes only the sections relevant to the specific control
    being mapped.
    
    Args:
        control_id: The NIST control ID (e.g., "AC-1", "AU-2", "SC-8")
        security_overview_sections: Dictionary of parsed security sections
        
    Returns:
        str: Formatted security overview section with only relevant content
    """
    if not security_overview_sections:
        return ""
    
    relevant_sections = get_relevant_security_sections(control_id)
    
    # Build the focused security overview
    section_parts = []
    for section_name in relevant_sections:
        if section_name in security_overview_sections:
            section_content = security_overview_sections[section_name]
            section_parts.append(section_content)
            logger.debug(f"Included section '{section_name}' for control {control_id}")
        else:
            logger.warning(f"Section '{section_name}' not found in parsed overview for control {control_id}")
    
    if not section_parts:
        logger.warning(f"No relevant sections found for control {control_id}, using service_overview if available")
        # Fallback to service overview if no relevant sections found
        if "service_overview" in security_overview_sections:
            section_parts.append(security_overview_sections["service_overview"])
    
    focused_overview = '\n\n'.join(section_parts)
    
    if focused_overview:
        return (
            "## SERVICE SECURITY OVERVIEW (Reference)\n"
            "The following provides relevant security context for this control. "
            "Use this as context when analyzing the specific control implementation:\n\n"
            f"{focused_overview}\n\n"
            "---\n\n"
        )
    
    return ""


def validate_security_overview_structure(security_overview_content: str) -> tuple[bool, List[str]]:
    """
    Validate that the security overview has the expected structure.
    
    Args:
        security_overview_content: The security overview markdown content
        
    Returns:
        tuple: (is_valid, list_of_issues)
    """
    if not security_overview_content:
        return False, ["Security overview content is empty"]
    
    issues = []
    sections_found = []
    
    # Check for each expected section
    for section_name, headers in SECTION_HEADERS.items():
        found = False
        for header in headers:
            if header.strip() in security_overview_content:
                found = True
                sections_found.append(section_name)
                break
        
        if not found:
            issues.append(f"Missing section: {section_name}")
    
    if len(sections_found) < 2:
        issues.append(f"Only found {len(sections_found)} sections, expected at least 2")
    
    is_valid = len(issues) == 0
    return is_valid, issues
