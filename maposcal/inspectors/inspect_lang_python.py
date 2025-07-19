"""
Python language inspector using the new control hints enumerator.

This is an example of how other language inspectors can use the new
control_hints_enumerator module for a more elegant solution.
"""

from traceback import format_exc
from textwrap import dedent
import re
from typing import List, Dict
from maposcal.utils.control_hints_enumerator import search_control_hints_in_content
import logging

logger = logging.getLogger(__name__)


def start_inspection(file_path: str, base_dir: str = None) -> Dict:
    """
    Takes a Python file and begins a non-generative inspection with the goal of returning
    a standardized inspection report covering many areas related to security and compliance.

    Args:
        file_path (str): Path to the Python file that will be inspected
        base_dir (str, optional): Base directory to truncate file_path relative to. If provided, file_path will be stored as relative to this directory.

    Returns:
        python_inspection_results (dict): Standardized inspection report
    """
    python_inspection_results = {}
    applicable_control_hints = []
    loaded_modules = {}
    file_system_interactions = []
    file_contents = ""
    cryptography = {}
    identified_vulnerabilities = {}
    access_controls = {}
    authn_authz = {}
    input_validation = {}
    logging_config = {}
    error_handling = {}
    configuration_settings = []

    # Truncate file_path if base_dir is provided
    display_file_path = file_path
    if base_dir:
        try:
            from pathlib import Path

            file_path_obj = Path(file_path)
            base_path_obj = Path(base_dir)
            if file_path_obj.is_relative_to(base_path_obj):
                display_file_path = str(file_path_obj.relative_to(base_path_obj))
        except (ValueError, AttributeError):
            # If file_path is not relative to base_dir, keep original path
            pass

    try:
        logger.debug(f"Opening Python file ({file_path}) for inspection.")
        with open(file_path, "r") as fh:
            file_contents = fh.read()
    except Exception:
        logger.error(f"Failed opening Python file ({file_path}) - {format_exc()}")

    if file_contents:
        try:
            ###
            # Parse for string-based control hints using the new enumerator
            # This searches all available controls, not just SC-8
            ###
            found_controls = search_control_hints_in_content(file_contents, "python")
            applicable_control_hints.extend(found_controls)
            logger.info(
                f"Found {len(found_controls)} applicable controls in Python file"
            )
        except Exception:
            logger.error(
                f"Failed to parse contents of {file_path} for control hints - {format_exc()}"
            )

        ###
        # Parse for loaded modules - shows what applicable functionality is likely used.
        ###
        try:
            (
                modules,
                network_modules,
                file_system_modules,
                logging_modules,
                cryptographic_modules,
            ) = identify_imported_modules(file_contents)
            loaded_modules["modules"] = modules
            loaded_modules["network_modules"] = network_modules
            loaded_modules["file_system_modules"] = file_system_modules
            loaded_modules["logging_modules"] = logging_modules
            loaded_modules["cryptographic_modules"] = cryptographic_modules
        except Exception:
            logger.error(
                f"Failed to parse loaded modules from {file_path} - {format_exc()}"
            )
            # Ensure loaded_modules has all required keys even if parsing fails
            loaded_modules.setdefault("modules", [])
            loaded_modules.setdefault("network_modules", [])
            loaded_modules.setdefault("file_system_modules", [])
            loaded_modules.setdefault("logging_modules", [])
            loaded_modules.setdefault("cryptographic_modules", [])

        ###
        # Parse for configuration ingestion (e.g., environmental variables, etc.)
        ###
        configuration_settings = identify_imported_configuration_variables(
            file_contents
        )

        ###
        # Parse for common file system interactions
        ###

        ###
        # Parse for known cryptographic operations
        ###
        try:
            cryptography = identify_cryptographic_operations(file_contents, cryptographic_modules)
            logger.info(f"Identified {len(cryptography)} cryptographic operations in {file_path}")
        except Exception:
            logger.error(f"Failed to parse cryptographic operations from {file_path} - {format_exc()}")
            cryptography = {}

        ###
        # Parse for identified vulnerabilities
        ###

        ###
        # Parse for known access controls
        ###

        ###
        # Parse for apparent authn/authz operations
        ###

        ###
        # Parse for known input validation
        ###

        ###
        # Parse for logging capabilities
        ###

        ###
        # Parse to determine error handling practices and failsafes.
        ###

        ###
        # Generate LLM context summary
        ###

    python_inspection_results["file_path"] = display_file_path
    python_inspection_results["language"] = "Python"
    python_inspection_results["control_hints"] = applicable_control_hints
    python_inspection_results["loaded_modules"] = loaded_modules
    python_inspection_results["configuration_settings"] = configuration_settings
    python_inspection_results["file_system_interactions"] = file_system_interactions
    python_inspection_results["cryptography"] = cryptography
    python_inspection_results["identified_vulnerabilities"] = identified_vulnerabilities
    python_inspection_results["access_controls"] = access_controls
    python_inspection_results["authn_authz"] = authn_authz
    python_inspection_results["input_validation"] = input_validation
    python_inspection_results["logging"] = logging_config
    python_inspection_results["error_handling"] = error_handling

    file_summary = summarize_discovery_content(python_inspection_results)
    python_inspection_results["file_summary"] = file_summary

    return python_inspection_results


def summarize_discovery_content(python_inspection_results: Dict) -> str:
    """
    Takes the final report of all discovered items and creates a human-readable, LLM-friendly summary of the file.
    This allows for seeding future LLM activities with the necessary guardrails to ensure an accurate summary of
    the code.  This summary is focused on attributes key for security and compliance efforts.

    Args:
        python_inspection_results (dict): All attributes discovered by the start_inspection function
    Returns:
        file_summary (str): Human/LLM-readable summary of the file.
    """
    networking_results = ""
    file_system_results = ""
    logging_results = ""
    configuration_results = ""
    config_variables = ""
    cryptographic_results = ""

    # Safely access loaded_modules with default empty lists if keys don't exist
    loaded_modules = python_inspection_results.get("loaded_modules", {})
    network_modules = loaded_modules.get("network_modules", [])
    file_system_modules = loaded_modules.get("file_system_modules", [])
    logging_modules = loaded_modules.get("logging_modules", [])
    cryptographic_modules = loaded_modules.get("cryptographic_modules", [])

    if len(network_modules) > 0:
        networking_results = f"Discovery of networking modules shows the following being used for connectivity: {network_modules}."
    else:
        networking_results = (
            "No networking capabilities have been detected in this file."
        )

    if len(file_system_modules) > 0:
        file_system_results = f"File system access is expected using the discovered modules: {file_system_modules}."
    else:
        file_system_results = "No file system access has been detected in this file."

    if len(logging_modules) > 0:
        logging_results = f"Logging capabilities are expected to be using these modules: {logging_modules}."
    else:
        logging_results = "No logging capabilities have been detected in this file."

    configuration_settings = python_inspection_results.get("configuration_settings", [])
    if len(configuration_settings) > 0:
        for config_var in configuration_settings:
            config_variables = f"{config_variables}, {config_var['variable']}".lstrip(
                ","
            )

        configuration_results = f"Configuration settings, either from environmental variables, or other sources are stored in the following variables: {config_variables}."
    else:
        configuration_results = "No configuration settings (e.g., environmental variables, etc.) have been imported from this file."

    if len(cryptographic_modules) > 0:
        cryptographic_results = f"Potential cryptographic operations are happening using the following modules. {cryptographic_modules}."

    file_summary = dedent(
        f"""\
        The file {python_inspection_results["file_path"]} is written in {python_inspection_results["language"]}. \
{networking_results} \
{file_system_results} \
{logging_results} \
{configuration_results} \
{cryptographic_results}\
"""
    )

    return file_summary


def identify_imported_configuration_variables(
    file_contents: str,
) -> List[Dict[str, str]]:
    """
    Parses a Python code file and identifies configuration variables used in the code.
    Includes environment variables, config files, and other configuration sources.

    Args:
        file_contents (str): Code contents of a module to be parsed for imported configuration variables.

    Returns:
        results (List[Dict[str, str]]): Method of ingestion, variable name, and source key.
    """
    patterns = [
        {
            "method": "Environment Variables (os.getenv)",
            "regex": r'(?P<var>\w+)\s*=\s*os\.getenv\(["\'](?P<key>[^"\']+)["\']',
        },
        {
            "method": "Environment Variables (os.environ)",
            "regex": r'(?P<var>\w+)\s*=\s*os\.environ\[["\'](?P<key>[^"\']+)["\']\]',
        },
        {"method": "ConfigParser", "regex": r'config\.get\(["\'](?P<key>[^"\']+)["\']'},
        {
            "method": "YAML Configuration",
            "regex": r'yaml\.load\(.*?["\'](?P<key>[^"\']+)["\']',
        },
    ]

    results = []

    for pattern in patterns:
        matches = re.finditer(pattern["regex"], file_contents)
        for match in matches:
            result = {
                "method": pattern["method"],
                "variable": match.group("var") if "var" in match.groupdict() else "",
                "source": match.group("key") if "key" in match.groupdict() else "",
            }
            results.append(result)

    return results


def identify_imported_modules(file_contents: str) -> tuple:
    """
    Parses a Python code file and identifies all modules that are imported and used by the code.

    Args:
        file_contents (str): Contents of a code module to be parsed for imported modules.
    Returns:
        tuple: (modules, network_modules, file_system_modules, logging_modules, cryptographic_modules)
    """
    modules = []
    network_modules = []
    file_system_modules = []
    logging_modules = []
    cryptographic_modules = []

    # Python-specific module patterns
    REF_PYTHON_NETWORK_MODULES = [
        "requests",
        "urllib",
        "urllib3",
        "httpx",
        "aiohttp",
        "socket",
        "ssl",
        "http",
        "https",
    ]
    REF_PYTHON_FILE_SYSTEM_MODULES = [
        "os",
        "pathlib",
        "shutil",
        "glob",
        "fnmatch",
        "tempfile",
        "zipfile",
        "tarfile",
    ]
    REF_PYTHON_LOGGING_MODULES = ["logging", "loguru", "structlog"]
    REF_PYTHON_CRYPTOGRAPHIC_MODULES = [
        "cryptography",
        "hashlib",
        "hmac",
        "base64",
        "secrets",
        "ssl",
        "crypto",
    ]

    # Find import statements
    import_patterns = [
        r"^import\s+(\w+)",
        r"^from\s+(\w+)\s+import",
        r"^import\s+(\w+)\s+as",
        r"^from\s+(\w+)\.(\w+)\s+import",
    ]

    for pattern in import_patterns:
        matches = re.finditer(pattern, file_contents, re.MULTILINE)
        for match in matches:
            module_name = match.group(1)
            if module_name not in modules:
                modules.append(module_name)

    # Categorize modules
    for module in modules:
        if module in REF_PYTHON_NETWORK_MODULES:
            network_modules.append(module)
        if module in REF_PYTHON_FILE_SYSTEM_MODULES:
            file_system_modules.append(module)
        if module in REF_PYTHON_LOGGING_MODULES:
            logging_modules.append(module)
        if module in REF_PYTHON_CRYPTOGRAPHIC_MODULES:
            cryptographic_modules.append(module)

    return (
        modules,
        network_modules,
        file_system_modules,
        logging_modules,
        cryptographic_modules,
    )


def identify_cryptographic_operations(file_contents: str, cryptographic_modules: List[str]) -> Dict[str, str]:
    """
    Parses a Python code file and identifies specific cryptographic operations based on loaded modules.
    Generates concise descriptions of what each cryptographic module is doing in the code.

    Args:
        file_contents (str): Contents of the code file to analyze
        cryptographic_modules (List[str]): List of detected cryptographic modules

    Returns:
        Dict[str, str]: Dictionary with module names as keys and operation descriptions as values
    """
    cryptography_operations = {}
    
    # Define operation patterns for each cryptographic module
    operation_patterns = {
        "cryptography": [
            {
                "pattern": r'Cipher\(',
                "description": "Symmetric encryption cipher creation using cryptography library primitives. Provides high-security encryption algorithms with proper key management and initialization vectors. Supports FIPS-compliant cryptographic implementations for compliance requirements."
            },
            {
                "pattern": r'rsa\.generate_private_key\(',
                "description": "RSA private key generation for asymmetric cryptography operations. Creates secure key pairs for digital signatures and encryption with configurable key sizes. Enables secure key exchange and digital signature capabilities."
            },
            {
                "pattern": r'load_pem_private_key\(',
                "description": "PEM format private key loading for cryptographic operations. Imports existing keys for digital signature generation and data decryption. Requires secure key storage and access control practices."
            },
            {
                "pattern": r'load_pem_x509_certificate\(',
                "description": "X.509 certificate loading for identity verification and trust establishment. Validates certificate authenticity and extracts identity information. Essential for PKI-based authentication and authorization systems."
            }
        ],
        "hashlib": [
            {
                "pattern": r'hashlib\.sha256\(',
                "description": "SHA256 hash generation for data integrity verification and digital signatures. Ensures message authenticity and prevents tampering during transmission. Critical for compliance controls requiring data integrity protection (SI-7)."
            },
            {
                "pattern": r'hashlib\.md5\(',
                "description": "MD5 hash generation for legacy compatibility and checksum operations. Provides fast hash computation but should not be used for security-critical applications. Suitable for non-security data validation and integrity checks."
            },
            {
                "pattern": r'hashlib\.sha512\(',
                "description": "SHA512 hash generation for high-security data integrity verification. Provides stronger cryptographic properties than SHA256 for enhanced security requirements. Suitable for applications requiring maximum cryptographic strength."
            }
        ],
        "hmac": [
            {
                "pattern": r'hmac\.new\(',
                "description": "HMAC (Hash-based Message Authentication Code) creation for message integrity verification. Combines cryptographic hashing with secret key authentication for secure message validation. Provides both integrity and authenticity protection for data transmission."
            },
            {
                "pattern": r'hmac\.compare_digest\(',
                "description": "Constant-time HMAC comparison for secure authentication verification. Prevents timing attacks during cryptographic validation operations. Essential for secure authentication and session management."
            }
        ],
        "base64": [
            {
                "pattern": r'base64\.b64encode\(',
                "description": "Base64 encoding of binary data for text-based transmission and storage. Converts cryptographic outputs to ASCII format for safe data handling. Supports audit and compliance requirements for data handling transparency."
            },
            {
                "pattern": r'base64\.b64decode\(',
                "description": "Base64 decoding of encoded data back to binary format for processing. Restores cryptographic data from text representation for further operations. Enables secure data serialization and deserialization workflows."
            }
        ],
        "secrets": [
            {
                "pattern": r'secrets\.token_bytes\(',
                "description": "Cryptographically secure random byte generation for key and nonce creation. Provides high-entropy random data for cryptographic operations and prevents predictable patterns. Essential for secure key generation and initialization vector creation."
            },
            {
                "pattern": r'secrets\.token_hex\(',
                "description": "Cryptographically secure random hex string generation for secure identifiers. Creates unpredictable tokens for session management and cryptographic parameters. Critical for preventing cryptographic attacks based on predictable values."
            },
            {
                "pattern": r'secrets\.choice\(',
                "description": "Cryptographically secure random selection from sequences for secure randomization. Ensures unpredictable choices for cryptographic algorithms and security protocols. Provides secure random selection for cryptographic applications."
            }
        ],
        "ssl": [
            {
                "pattern": r'ssl\.create_default_context\(',
                "description": "SSL/TLS context creation with secure default settings for encrypted communications. Establishes secure communication channels with certificate validation and encryption. Supports compliance requirements for data in transit protection (SC-8)."
            },
            {
                "pattern": r'ssl\.wrap_socket\(',
                "description": "SSL/TLS socket wrapping for secure network communication. Provides encrypted data transmission and server certificate validation. Critical for protecting sensitive data during network transmission."
            },
            {
                "pattern": r'ssl\.create_connection\(',
                "description": "SSL/TLS client connection establishment for secure outbound communications. Ensures encrypted data transmission with proper certificate validation. Essential for secure client-server communication protocols."
            }
        ],
        "crypto": [
            {
                "pattern": r'Crypto\.Cipher\.AES\.new\(',
                "description": "AES cipher creation using PyCrypto library for symmetric encryption operations. Provides high-performance block cipher encryption for data confidentiality. Supports various key sizes and encryption modes for different security requirements."
            },
            {
                "pattern": r'Crypto\.PublicKey\.RSA\.generate\(',
                "description": "RSA key pair generation using PyCrypto library for asymmetric cryptography. Creates public/private key pairs for digital signatures and encryption operations. Enables secure key exchange and digital signature capabilities."
            },
            {
                "pattern": r'Crypto\.Signature\.pkcs1_15\.new\(',
                "description": "RSA digital signature creation using PKCS1 v1.5 padding scheme. Generates cryptographically verifiable signatures for message authentication. Essential for secure communication and document integrity verification."
            }
        ]
    }
    
    # Check each detected cryptographic module for specific operations
    for module in cryptographic_modules:
        if module in operation_patterns:
            module_operations = []
            
            for operation in operation_patterns[module]:
                matches = list(re.finditer(operation["pattern"], file_contents))
                if matches:
                    module_operations.append(operation["description"])
            
            # If operations were found for this module, add to results
            if module_operations:
                # Use the first operation description found (most representative)
                cryptography_operations[module] = module_operations[0]
                logger.info(f"Identified cryptographic operations for module {module}")
    
    return cryptography_operations


if __name__ == "__main__":
    # Example usage
    r = start_inspection("/path/to/example.py")
    print(r)
