"""
Dockerfile Inspector for MapOSCAL.

This module provides comprehensive analysis of Dockerfiles to identify security controls
and compliance features. It parses Dockerfile instructions and maps them to NIST 800-53
Rev.5 controls using the control hints system.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from maposcal.utils.dockerfile_control_hints import (
    DOCKERFILE_CONTROL_MAPPINGS,
    get_control_mappings_for_instruction,
    is_transport_security_configured,
    generate_oscal_props,
    CONTROL_STATUS_MAPPING
)

logger = logging.getLogger(__name__)


def start_inspection(file_path: str, base_dir: str = None) -> Dict:
    """
    Analyze a Dockerfile and return a standardized inspection report.
    
    Args:
        file_path: Path to the Dockerfile to analyze
        base_dir: Base directory to truncate file_path relative to
        
    Returns:
        Dictionary containing Dockerfile analysis results
    """
    dockerfile_inspection_results = {}
    
    try:
        # Truncate file_path if base_dir is provided
        display_file_path = file_path
        if base_dir:
            try:
                file_path_obj = Path(file_path)
                base_path_obj = Path(base_dir)
                if file_path_obj.is_relative_to(base_path_obj):
                    display_file_path = str(file_path_obj.relative_to(base_path_obj))
            except (ValueError, AttributeError):
                # If file_path is not relative to base_dir, keep original path
                pass
        
        logger.info(f"Starting Dockerfile inspection: {display_file_path}")
        
        # Read Dockerfile content
        with open(file_path, "r", encoding="utf-8") as f:
            dockerfile_content = f.read()
        
        # Parse Dockerfile instructions
        parsed_instructions = parse_dockerfile_instructions(dockerfile_content)
        
        # Analyze for security controls
        control_implementations = analyze_security_controls(parsed_instructions, dockerfile_content)
        
        # Check for transport security
        transport_security = is_transport_security_configured(dockerfile_content)
        
        # Generate summary
        file_summary = generate_dockerfile_summary(parsed_instructions, control_implementations, transport_security)
        
        # Build results
        dockerfile_inspection_results = {
            "file_path": display_file_path,
            "file_summary": file_summary,
            "control_hints": list(set([control for impl in control_implementations.values() for control in impl.get("controls", [])])),
            "parsed_instructions": parsed_instructions,
            "control_implementations": control_implementations,
            "transport_security": transport_security,
            "entrypoint_scripts": find_entrypoint_scripts(parsed_instructions),
            "dockerfile_analysis": {
                "total_instructions": len(parsed_instructions),
                "security_controls_found": len(control_implementations),
                "transport_security_configured": transport_security,
                "entrypoint_scripts": find_entrypoint_scripts(parsed_instructions),
                "exposed_ports": extract_exposed_ports(parsed_instructions),
                "user_configuration": extract_user_configuration(parsed_instructions),
                "volume_declarations": extract_volume_declarations(parsed_instructions),
                "health_check": extract_health_check(parsed_instructions)
            }
        }
        
        logger.info(f"Dockerfile inspection completed: {len(control_implementations)} security controls found")
        
    except Exception as e:
        logger.error(f"Failed to inspect Dockerfile {file_path}: {e}")
        dockerfile_inspection_results = {
            "file_path": display_file_path,
            "file_summary": f"Error analyzing Dockerfile: {e}",
            "control_hints": [],
            "error": str(e)
        }
    
    return dockerfile_inspection_results


def parse_dockerfile_instructions(content: str) -> Dict[str, List[Dict]]:
    """
    Parse Dockerfile content and extract all instructions.
    
    Args:
        content: Raw Dockerfile content
        
    Returns:
        Dictionary mapping instruction types to lists of instruction details
    """
    instructions = {
        "FROM": [],
        "USER": [],
        "WORKDIR": [],
        "EXPOSE": [],
        "ENV": [],
        "COPY": [],
        "ADD": [],
        "RUN": [],
        "ENTRYPOINT": [],
        "CMD": [],
        "STOPSIGNAL": [],
        "HEALTHCHECK": [],
        "VOLUME": [],
        "ARG": [],
        "LABEL": [],
        "SHELL": []
    }
    
    lines = content.split('\n')
    line_number = 0
    
    while line_number < len(lines):
        line = lines[line_number].strip()
        line_number += 1
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Parse instruction
        instruction_match = re.match(r'^(\w+)\s+(.+)$', line, re.IGNORECASE)
        if instruction_match:
            instruction_type = instruction_match.group(1).upper()
            instruction_value = instruction_match.group(2).strip()
            
            # Handle multi-line instructions (lines ending with \)
            if instruction_value.endswith('\\'):
                # Collect continuation lines
                while line_number < len(lines):
                    next_line = lines[line_number].strip()
                    if next_line.endswith('\\'):
                        # Remove the backslash and add the content
                        instruction_value = instruction_value[:-1] + " " + next_line[:-1]
                        line_number += 1
                    elif next_line and not next_line.startswith('#'):
                        # This is the final line of the multi-line instruction
                        instruction_value = instruction_value[:-1] + " " + next_line
                        line_number += 1
                        break
                    else:
                        # Empty line or comment, skip
                        line_number += 1
            
            if instruction_type in instructions:
                instruction_detail = {
                    "line_number": line_number,
                    "value": instruction_value,
                    "raw_line": line
                }
                
                # Parse specific instruction types
                if instruction_type == "ENV":
                    parsed_env = parse_env_instruction(instruction_value)
                    instruction_detail.update(parsed_env)
                elif instruction_type == "EXPOSE":
                    parsed_ports = parse_expose_instruction(instruction_value)
                    instruction_detail.update(parsed_ports)
                elif instruction_type == "USER":
                    parsed_user = parse_user_instruction(instruction_value)
                    instruction_detail.update(parsed_user)
                elif instruction_type == "COPY":
                    parsed_copy = parse_copy_instruction(instruction_value)
                    instruction_detail.update(parsed_copy)
                elif instruction_type == "RUN":
                    parsed_run = parse_run_instruction(instruction_value)
                    instruction_detail.update(parsed_run)
                elif instruction_type == "VOLUME":
                    parsed_volume = parse_volume_instruction(instruction_value)
                    instruction_detail.update(parsed_volume)
                elif instruction_type == "HEALTHCHECK":
                    parsed_health = parse_healthcheck_instruction(instruction_value)
                    instruction_detail.update(parsed_health)
                
                instructions[instruction_type].append(instruction_detail)
    
    return instructions


def parse_env_instruction(value: str) -> Dict[str, Any]:
    """Parse ENV instruction value."""
    env_vars = {}
    
    # Handle both forms: ENV key=value and ENV key value
    if '=' in value:
        # ENV key=value form
        parts = value.split('=', 1)
        if len(parts) == 2:
            env_vars[parts[0].strip()] = parts[1].strip()
    else:
        # ENV key value form
        parts = value.split(None, 1)
        if len(parts) == 2:
            env_vars[parts[0].strip()] = parts[1].strip()
    
    return {"env_variables": env_vars}


def parse_expose_instruction(value: str) -> Dict[str, Any]:
    """Parse EXPOSE instruction value."""
    ports = []
    protocols = []
    
    # Extract ports and protocols
    for part in value.split():
        if ':' in part:
            # Format: port:protocol
            port_protocol = part.split(':')
            if len(port_protocol) == 2:
                try:
                    ports.append(int(port_protocol[0]))
                    protocols.append(port_protocol[1].lower())
                except ValueError:
                    continue
        else:
            # Just port number
            try:
                ports.append(int(part))
                protocols.append('tcp')  # Default protocol
            except ValueError:
                continue
    
    return {"ports": ports, "protocols": protocols}


def parse_user_instruction(value: str) -> Dict[str, Any]:
    """Parse USER instruction value."""
    user_info = {"username": value, "uid": None, "gid": None}
    
    if ':' in value:
        # Format: user:group or uid:gid
        parts = value.split(':')
        if len(parts) == 2:
            if parts[0].isdigit() and parts[1].isdigit():
                # Numeric UID:GID
                user_info["uid"] = int(parts[0])
                user_info["gid"] = int(parts[1])
                user_info["username"] = None
            else:
                # Username:group
                user_info["username"] = parts[0]
                user_info["group"] = parts[1]
    elif value.isdigit():
        # Numeric UID
        user_info["uid"] = int(value)
        user_info["username"] = None
    
    return user_info


def parse_copy_instruction(value: str) -> Dict[str, Any]:
    """Parse COPY instruction value."""
    copy_info = {"source": [], "destination": None}
    
    # Handle both forms: COPY src dst and COPY ["src", "dst"]
    if value.startswith('[') and value.endswith(']'):
        # JSON array format
        try:
            import json
            parts = json.loads(value)
            if len(parts) >= 2:
                copy_info["source"] = parts[:-1]
                copy_info["destination"] = parts[-1]
        except json.JSONDecodeError:
            pass
    else:
        # Space-separated format
        parts = value.split()
        if len(parts) >= 2:
            copy_info["source"] = parts[:-1]
            copy_info["destination"] = parts[-1]
    
    return copy_info


def parse_run_instruction(value: str) -> Dict[str, Any]:
    """Parse RUN instruction value."""
    run_info = {"commands": [], "shell_form": True}
    
    # Check if it's exec form (starts with [)
    if value.startswith('[') and value.endswith(']'):
        run_info["shell_form"] = False
        try:
            import json
            commands = json.loads(value)
            run_info["commands"] = commands
        except json.JSONDecodeError:
            run_info["commands"] = [value]
    else:
        # Shell form
        run_info["commands"] = [value]
    
    return run_info


def parse_volume_instruction(value: str) -> Dict[str, Any]:
    """Parse VOLUME instruction value."""
    volume_info = {"paths": []}
    
    # Handle both forms: VOLUME path and VOLUME ["path1", "path2"]
    if value.startswith('[') and value.endswith(']'):
        try:
            import json
            paths = json.loads(value)
            volume_info["paths"] = paths
        except json.JSONDecodeError:
            volume_info["paths"] = [value]
    else:
        volume_info["paths"] = [value]
    
    return volume_info


def parse_healthcheck_instruction(value: str) -> Dict[str, Any]:
    """Parse HEALTHCHECK instruction value."""
    health_info = {"command": value, "interval": None, "timeout": None, "retries": None}
    
    # Extract health check parameters if present
    # This is a simplified parser - could be enhanced for more complex health checks
    return health_info


def analyze_security_controls(parsed_instructions: Dict, dockerfile_content: str) -> Dict[str, Dict]:
    """
    Analyze parsed instructions for security control implementations.
    
    Args:
        parsed_instructions: Parsed Dockerfile instructions
        dockerfile_content: Raw Dockerfile content
        
    Returns:
        Dictionary mapping control IDs to implementation details
    """
    control_implementations = {}
    
    # Analyze each instruction type
    for instruction_type, instructions in parsed_instructions.items():
        for instruction in instructions:
            value = instruction.get("value", "")
            
            # Get control mappings for this instruction
            mappings = get_control_mappings_for_instruction(instruction_type, value)
            
            for mapping in mappings:
                for control_id in mapping.get("controls", []):
                    if control_id not in control_implementations:
                        control_implementations[control_id] = {
                            "controls": [control_id],
                            "status": "implemented",
                            "evidence": [],
                            "oscal_props": [],
                            "instruction_count": 0
                        }
                    
                    # Add evidence
                    evidence = {
                        "instruction": instruction_type,
                        "line_number": instruction.get("line_number"),
                        "value": value,
                        "description": mapping.get("description"),
                        "evidence_template": mapping.get("evidence_template")
                    }
                    
                    control_implementations[control_id]["evidence"].append(evidence)
                    control_implementations[control_id]["instruction_count"] += 1
                    
                                    # Add OSCAL properties
                    context = {
                        "uid": instruction.get("uid"),
                        "gid": instruction.get("gid"),
                        "username": instruction.get("username"),
                        "ports": instruction.get("ports"),
                        "path": instruction.get("destination"),
                        "command": value,
                        "files": ", ".join(instruction.get("source", [])),
                        "paths": ", ".join(instruction.get("paths", [])),
                        "env_vars": ", ".join(instruction.get("env_variables", {}).keys()),
                        "all_ports": ", ".join(map(str, instruction.get("ports", []))),
                        "tls_ports": ", ".join(map(str, [p for p in instruction.get("ports", []) if p in [443, 8443, 9443, 1443, 2443]])),
                        "min_version": "1.2",  # Default TLS version
                        "flags": value,  # Default to instruction value
                        "vars": value,  # Default to instruction value
                        "cert_path": instruction.get("destination"),
                        "key_path": instruction.get("destination"),
                        "ca_files": ", ".join(instruction.get("source", [])),
                        "config_file": instruction.get("destination"),
                        "keystore_command": value,
                        "keystore_path": instruction.get("destination"),
                        "keystore_type": "unknown",
                        "alias": "default"
                    }
                    
                    oscal_props = generate_oscal_props(mapping, context)
                    control_implementations[control_id]["oscal_props"].extend(oscal_props)
    
    return control_implementations


def generate_dockerfile_summary(parsed_instructions: Dict, control_implementations: Dict, transport_security: bool) -> str:
    """
    Generate a human-readable summary of the Dockerfile analysis.
    
    Args:
        parsed_instructions: Parsed Dockerfile instructions
        control_implementations: Security control implementations
        transport_security: Whether transport security is configured
        
    Returns:
        Summary string
    """
    summary_parts = []
    
    # Basic statistics
    total_instructions = sum(len(instructions) for instructions in parsed_instructions.values())
    summary_parts.append(f"Dockerfile contains {total_instructions} instructions")
    
    # Security controls found
    if control_implementations:
        summary_parts.append(f"Implements {len(control_implementations)} security controls:")
        for control_id, impl in control_implementations.items():
            evidence_count = len(impl.get("evidence", []))
            summary_parts.append(f"  - {control_id}: {evidence_count} implementation(s)")
    else:
        summary_parts.append("No specific security controls identified")
    
    # Transport security
    if transport_security:
        summary_parts.append("Transport security (TLS/HTTPS) is configured")
    else:
        summary_parts.append("Transport security (TLS/HTTPS) is not configured")
    
    # Key security features
    if parsed_instructions.get("USER"):
        summary_parts.append("User management configured")
    
    if parsed_instructions.get("EXPOSE"):
        ports = extract_exposed_ports(parsed_instructions)
        if ports:
            summary_parts.append(f"Network ports exposed: {', '.join(map(str, ports))}")
    
    if parsed_instructions.get("VOLUME"):
        summary_parts.append("Persistent data volumes declared")
    
    if parsed_instructions.get("HEALTHCHECK"):
        summary_parts.append("Health monitoring configured")
    
    return "\n".join(summary_parts)


def find_entrypoint_scripts(parsed_instructions: Dict) -> List[str]:
    """Extract ENTRYPOINT script paths from parsed instructions."""
    entrypoint_scripts = []
    
    for entrypoint in parsed_instructions.get("ENTRYPOINT", []):
        value = entrypoint.get("value", "")
        
        # Check if it's a script file (not a direct command)
        if not value.startswith('[') and not value.startswith('"'):
            # Shell form - might be a script
            if '/' in value or value.endswith('.sh') or value.endswith('.py'):
                entrypoint_scripts.append(value)
        elif value.startswith('['):
            # Exec form - check if it's a script
            try:
                import json
                parts = json.loads(value)
                if parts and isinstance(parts[0], str):
                    script_path = parts[0]
                    if '/' in script_path or script_path.endswith('.sh') or script_path.endswith('.py'):
                        entrypoint_scripts.append(script_path)
            except json.JSONDecodeError:
                pass
    
    return entrypoint_scripts


def extract_exposed_ports(parsed_instructions: Dict) -> List[int]:
    """Extract all exposed ports from parsed instructions."""
    ports = []
    
    for expose in parsed_instructions.get("EXPOSE", []):
        if "ports" in expose:
            ports.extend(expose["ports"])
    
    return list(set(ports))  # Remove duplicates


def extract_user_configuration(parsed_instructions: Dict) -> Dict[str, Any]:
    """Extract user configuration from parsed instructions."""
    user_config = {}
    
    for user in parsed_instructions.get("USER", []):
        user_config.update({
            "username": user.get("username"),
            "uid": user.get("uid"),
            "gid": user.get("gid"),
            "group": user.get("group")
        })
    
    return user_config


def extract_volume_declarations(parsed_instructions: Dict) -> List[str]:
    """Extract volume declarations from parsed instructions."""
    volumes = []
    
    for volume in parsed_instructions.get("VOLUME", []):
        if "paths" in volume:
            volumes.extend(volume["paths"])
    
    return volumes


def extract_health_check(parsed_instructions: Dict) -> Optional[Dict[str, Any]]:
    """Extract health check configuration from parsed instructions."""
    health_checks = parsed_instructions.get("HEALTHCHECK", [])
    
    if health_checks:
        return health_checks[0]  # Return the first health check
    
    return None
