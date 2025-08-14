"""
Dockerfile Control Hints for MapOSCAL.

This module provides comprehensive mapping between Dockerfile patterns and NIST 800-53 Rev.5 controls
based on the compliance hints table. It enables automatic identification of security controls
implemented through Dockerfile configurations.
"""

from typing import Dict, List, Tuple, Optional

# Mapping of Dockerfile patterns to NIST 800-53 controls
DOCKERFILE_CONTROL_MAPPINGS = {
    # User and Access Control
    "USER": {
        "non_root_user": {
            "controls": ["AC-6", "CM-6"],
            "description": "Non-root user enforcement demonstrates least privilege at runtime",
            "evidence_template": "USER {username} (UID: {uid}, GID: {gid}) - non-root user enforcement",
            "oscal_props": [
                {"name": "uid", "value": "{uid}"},
                {"name": "gid", "value": "{gid}"},
                {"name": "username", "value": "{username}"}
            ]
        },
        "numeric_uid_gid": {
            "controls": ["AC-6", "CM-6"],
            "description": "Stable identity mapping in orchestration",
            "evidence_template": "Numeric UID/GID specified for stable identity mapping",
            "oscal_props": [
                {"name": "uid", "value": "{uid}"},
                {"name": "gid", "value": "{gid}"}
            ]
        }
    },
    
    "WORKDIR": {
        "dedicated_home_workdir": {
            "controls": ["AC-6", "CM-6"],
            "description": "Constrains write locations for process",
            "evidence_template": "WORKDIR {path} with non-root user - constrains write locations",
            "oscal_props": [
                {"name": "workdir", "value": "{path}"}
            ]
        }
    },
    
    # Network and Port Security
    "EXPOSE": {
        "exposed_ports": {
            "controls": ["CM-7", "SC-7"],
            "description": "Declares runtime network surface (least functionality)",
            "evidence_template": "EXPOSE {ports} - declared network surface",
            "oscal_props": [
                {"name": "ports", "value": "{ports}"}
            ]
        },
        "tls_ports": {
            "controls": ["SC-8", "SC-13", "CM-7"],
            "description": "Indicates HTTPS/TLS listener intent",
            "evidence_template": "EXPOSE {ports} - TLS/HTTPS ports exposed",
            "oscal_props": [
                {"name": "tls_ports", "value": "{tls_ports}"},
                {"name": "ports", "value": "{all_ports}"}
            ]
        }
    },
    
    # Process Control and Signal Handling
    "ENTRYPOINT": {
        "exec_form": {
            "controls": ["CP-10", "SI-2"],
            "description": "Proper signal handling & process control",
            "evidence_template": "ENTRYPOINT {command} - exec form for proper signal handling",
            "oscal_props": [
                {"name": "entrypoint", "value": "exec"},
                {"name": "command", "value": "{command}"}
            ]
        }
    },
    
    "CMD": {
        "exec_form": {
            "controls": ["CP-10", "SI-2"],
            "description": "Proper signal handling & process control",
            "evidence_template": "CMD {command} - exec form for proper signal handling",
            "oscal_props": [
                {"name": "cmd", "value": "exec"},
                {"name": "command", "value": "{command}"}
            ]
        }
    },
    
    "STOPSIGNAL": {
        "controlled_shutdown": {
            "controls": ["CP-10", "SI-13"],
            "description": "Controlled shutdown behavior",
            "evidence_template": "STOPSIGNAL {signal} - controlled shutdown behavior",
            "oscal_props": [
                {"name": "stopsignal", "value": "{signal}"}
            ]
        }
    },
    
    # Health Monitoring
    "HEALTHCHECK": {
        "health_monitoring": {
            "controls": ["SI-4(2)", "CP-2"],
            "description": "Health monitoring hook for ops/recovery",
            "evidence_template": "HEALTHCHECK {command} - health monitoring enabled",
            "oscal_props": [
                {"name": "healthcheck", "value": "{command}"},
                {"name": "interval", "value": "{interval}"},
                {"name": "timeout", "value": "{timeout}"}
            ]
        }
    },
    
    # Environment and Configuration
    "ENV": {
        "security_flags": {
            "controls": ["CM-6", "IA-5", "AU-12"],
            "description": "Records runtime posture (debug, auth toggles, logging)",
            "evidence_template": "ENV {var}={value} - security configuration set",
            "oscal_props": [
                {"name": "name", "value": "{var}"},
                {"name": "value", "value": "{value}"},
                {"name": "sensitivity", "value": "{sensitivity}"}
            ]
        },
        "tls_configuration": {
            "controls": ["SC-13", "SC-12"],
            "description": "Enforces approved crypto protocols",
            "evidence_template": "ENV {var}={value} - TLS configuration enforced",
            "oscal_props": [
                {"name": "min_tls", "value": "{min_version}"},
                {"name": "runtime_flags", "value": "{flags}"}
            ]
        },
        "tls_hardening": {
            "controls": ["SC-13", "SC-8"],
            "description": "Enforces cert verification / disables weaknesses",
            "evidence_template": "ENV {var}={value} - TLS hardening enabled",
            "oscal_props": [
                {"name": "tls_hardening_env", "value": "{vars}"}
            ]
        },
        "ca_bundle_config": {
            "controls": ["SC-8", "SC-13", "CM-6"],
            "description": "Ensures cert validation for outbound TLS",
            "evidence_template": "ENV {var}={value} - CA bundle configured for TLS validation",
            "oscal_props": [
                {"name": "trust_store_path", "value": "{path}"},
                {"name": "env_refs", "value": "{env_vars}"}
            ]
        }
    },
    
    # File Operations and Security
    "COPY": {
        "credentials_files": {
            "controls": ["IA-5(7)", "SC-28"],
            "description": "Identifies credential material in image",
            "evidence_template": "COPY {files} - credential files included",
            "oscal_props": [
                {"name": "secret_paths", "value": "{files}"}
            ]
        },
        "tls_certificates": {
            "controls": ["SC-12", "SC-13", "SC-28"],
            "description": "Provides server cert/key for TLS",
            "evidence_template": "COPY {cert_files} - TLS certificates included",
            "oscal_props": [
                {"name": "cert_path", "value": "{cert_path}"},
                {"name": "key_path", "value": "{key_path}"}
            ]
        },
        "ca_certificates": {
            "controls": ["SC-12", "SC-13"],
            "description": "Enables mTLS or enterprise PKI validation",
            "evidence_template": "COPY {ca_files} - CA certificates installed",
            "oscal_props": [
                {"name": "ca_install_paths", "value": "{paths}"}
            ]
        },
        "tls_config_files": {
            "controls": ["SC-13", "CM-6"],
            "description": "Declares presence of TLS server config",
            "evidence_template": "COPY {config_file} - TLS configuration file included",
            "oscal_props": [
                {"name": "tls_config_file", "value": "{config_file}"}
            ]
        }
    },
    
    # File Permissions and Ownership
    "RUN": {
        "ownership_permissions": {
            "controls": ["CM-6", "AC-6"],
            "description": "Enforces authorized access to code/data",
            "evidence_template": "RUN chown/chmod commands - file permissions hardened",
            "oscal_props": [
                {"name": "paths", "value": "{paths}"},
                {"name": "owner", "value": "{owner}"},
                {"name": "group", "value": "{group}"},
                {"name": "mode", "value": "{mode}"}
            ]
        },
        "key_permissions": {
            "controls": ["SC-12(3)", "SC-28"],
            "description": "Protects private key at rest in image",
            "evidence_template": "RUN chmod {mode} - key file permissions set",
            "oscal_props": [
                {"name": "key_owner", "value": "{owner}"},
                {"name": "key_group", "value": "{group}"},
                {"name": "key_mode", "value": "{mode}"}
            ]
        },
        "ca_certificate_install": {
            "controls": ["SC-12", "SC-13"],
            "description": "Installs and configures CA certificates",
            "evidence_template": "RUN update-ca-certificates - CA certificates installed",
            "oscal_props": [
                {"name": "ca_install_command", "value": "{command}"}
            ]
        },
        "keystore_setup": {
            "controls": ["SC-12", "SC-13", "SC-23"],
            "description": "Configures client certs/keystores for mutual auth",
            "evidence_template": "RUN {keystore_command} - keystore configured",
            "oscal_props": [
                {"name": "keystore_path", "value": "{path}"},
                {"name": "keystore_type", "value": "{type}"},
                {"name": "alias", "value": "{alias}"}
            ]
        }
    },
    
    # Data and Volume Management
    "VOLUME": {
        "persistent_data": {
            "controls": ["CP-9", "SC-28"],
            "description": "Marks persistent data needing backup/protection",
            "evidence_template": "VOLUME {paths} - persistent data paths declared",
            "oscal_props": [
                {"name": "data_paths", "value": "{paths}"}
            ]
        }
    },
    
    # Temporary Directory Control
    "TMPDIR": {
        "controlled_temp_path": {
            "controls": ["CM-6", "SI-7"],
            "description": "Directs writes to approved ephemeral path",
            "evidence_template": "ENV TMPDIR={path} - controlled temporary directory",
            "oscal_props": [
                {"name": "tmpdir", "value": "{path}"}
            ]
        }
    }
}

# Transport Security Indicators
TRANSPORT_SECURITY_INDICATORS = {
    "tls_ports": [443, 8443, 9443, 1443, 2443],
    "tls_environment_vars": [
        "TLS_MIN_VERSION", "TLS_MAX_VERSION", "TLS_CIPHER_SUITE",
        "SSL_CERT_FILE", "SSL_KEY_FILE", "SSL_CA_FILE",
        "REQUESTS_CA_BUNDLE", "NODE_EXTRA_CA_CERTS",
        "JAVA_TOOL_OPTIONS", "GODEBUG"
    ],
    "tls_config_files": [
        "nginx.conf", "apache2.conf", "httpd.conf", "ssl.conf",
        "tls.conf", "https.conf", "ssl-params.conf"
    ],
    "tls_certificate_extensions": [".crt", ".pem", ".cer", ".der", ".p12", ".pfx"],
    "tls_key_extensions": [".key", ".pem", ".p8", ".p12", ".pfx"]
}

# Control Status Mapping
CONTROL_STATUS_MAPPING = {
    "implemented": "applicable and inherently satisfied",
    "configured": "applicable but only satisfied through configuration",
    "partial": "applicable but partially satisfied",
    "not_implemented": "applicable and not satisfied",
    "not_applicable": "not applicable"
}

def get_control_mappings_for_instruction(instruction: str, value: str) -> List[Dict]:
    """
    Get control mappings for a specific Dockerfile instruction and value.
    
    Args:
        instruction: The Dockerfile instruction (e.g., "USER", "EXPOSE", "ENV")
        value: The value of the instruction
        
    Returns:
        List of control mappings with evidence and OSCAL properties
    """
    mappings = []
    
    if instruction in DOCKERFILE_CONTROL_MAPPINGS:
        for pattern, mapping in DOCKERFILE_CONTROL_MAPPINGS[instruction].items():
            # Check if the pattern matches the value
            if _pattern_matches(pattern, instruction, value):
                mappings.append(mapping)
    
    return mappings

def _pattern_matches(pattern: str, instruction: str, value: str) -> bool:
    """
    Check if a pattern matches the instruction value.
    
    Args:
        pattern: The pattern to check
        instruction: The Dockerfile instruction
        value: The value to check
        
    Returns:
        True if the pattern matches, False otherwise
    """
    if instruction == "USER":
        if pattern == "non_root_user":
            # Check if it's not root (UID != 0)
            return not value.strip().isdigit() or int(value.strip()) != 0
        elif pattern == "numeric_uid_gid":
            # Check if numeric UID:GID format
            return ":" in value and all(part.strip().isdigit() for part in value.split(":"))
    
    elif instruction == "EXPOSE":
        if pattern == "exposed_ports":
            return True  # Any EXPOSE instruction
        elif pattern == "tls_ports":
            # Check if any of the ports are TLS ports
            ports = [int(p.strip()) for p in value.split() if p.strip().isdigit()]
            return any(port in TRANSPORT_SECURITY_INDICATORS["tls_ports"] for port in ports)
    
    elif instruction == "ENV":
        if pattern == "security_flags":
            # Check for security-related environment variables
            return any(flag in value.upper() for flag in ["DEBUG", "AUTH", "LOG", "SECURE"])
        elif pattern == "tls_configuration":
            # Check for TLS-related environment variables
            return any(tls_var in value.upper() for tls_var in ["TLS", "SSL", "HTTPS"])
    
    elif instruction == "COPY":
        if pattern == "tls_certificates":
            # Check for certificate or key files
            return any(ext in value.lower() for ext in TRANSPORT_SECURITY_INDICATORS["tls_certificate_extensions"] + TRANSPORT_SECURITY_INDICATORS["tls_key_extensions"])
    
    elif instruction == "RUN":
        if pattern == "ownership_permissions":
            # Check for chown/chmod commands
            return "chown" in value.lower() or "chmod" in value.lower()
    
    return False

def is_transport_security_configured(dockerfile_content: str) -> bool:
    """
    Determine if the Dockerfile configures transport security (TLS/HTTPS).
    
    Args:
        dockerfile_content: The content of the Dockerfile
        
    Returns:
        True if transport security is configured, False otherwise
    """
    content_lower = dockerfile_content.lower()
    
    # Check for TLS ports
    if any(f"expose {port}" in content_lower for port in TRANSPORT_SECURITY_INDICATORS["tls_ports"]):
        return True
    
    # Check for TLS environment variables
    if any(f"env {var.lower()}" in content_lower for var in TRANSPORT_SECURITY_INDICATORS["tls_environment_vars"]):
        return True
    
    # Check for TLS configuration files
    if any(f"copy {file}" in content_lower for file in TRANSPORT_SECURITY_INDICATORS["tls_config_files"]):
        return True
    
    # Check for certificate/key files
    if any(ext in content_lower for ext in TRANSPORT_SECURITY_INDICATORS["tls_certificate_extensions"] + TRANSPORT_SECURITY_INDICATORS["tls_key_extensions"]):
        return True
    
    return False

def generate_oscal_props(mapping: Dict, context: Dict) -> List[Dict]:
    """
    Generate OSCAL properties from a control mapping.
    
    Args:
        mapping: The control mapping dictionary
        context: Context variables for property value substitution
        
    Returns:
        List of OSCAL properties
    """
    props = []
    
    for prop_template in mapping.get("oscal_props", []):
        prop = prop_template.copy()
        
        # Substitute context variables in property values
        if "value" in prop:
            try:
                prop["value"] = prop["value"].format(**context)
            except KeyError as e:
                # If a context variable is missing, use a default value
                missing_var = str(e).strip("'")
                if missing_var in ["uid", "gid", "username", "ports", "path", "command", "files", "paths", "env_vars"]:
                    prop["value"] = "not specified"
                elif missing_var in ["all_ports", "tls_ports", "min_version", "flags", "vars"]:
                    prop["value"] = "not specified"
                elif missing_var in ["cert_path", "key_path", "ca_files", "config_file"]:
                    prop["value"] = "not specified"
                elif missing_var in ["keystore_command", "keystore_path", "keystore_type", "alias"]:
                    prop["value"] = "not specified"
                else:
                    prop["value"] = "not specified"
        
        props.append(prop)
    
    return props
