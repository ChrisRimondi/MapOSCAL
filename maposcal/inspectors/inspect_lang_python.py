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


def start_inspection(file_path: str) -> Dict:
    """
    Takes a Python file and begins a non-generative inspection with the goal of returning
    a standardized inspection report covering many areas related to security and compliance.

    Args:
        file_path (str): Path to the Python file that will be inspected

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

    python_inspection_results["file_path"] = file_path
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

    if len(python_inspection_results["loaded_modules"]["network_modules"]) > 0:
        networking_results = f"Discovery of networking modules shows the following being used for connectivity: {python_inspection_results['loaded_modules']['network_modules']}."
    else:
        networking_results = (
            "No networking capabilities have been detected in this file."
        )

    if len(python_inspection_results["loaded_modules"]["file_system_modules"]) > 0:
        file_system_results = f"File system access is expected using the discovered modules: {python_inspection_results['loaded_modules']['file_system_modules']}."
    else:
        file_system_results = "No file system access has been detected in this file."

    if len(python_inspection_results["loaded_modules"]["logging_modules"]) > 0:
        logging_results = f"Logging capabilities are expected to be using these modules: {python_inspection_results['loaded_modules']['logging_modules']}."
    else:
        logging_results = "No logging capabilities have been detected in this file."

    if len(python_inspection_results["configuration_settings"]) > 0:
        for config_var in python_inspection_results["configuration_settings"]:
            config_variables = f"{config_variables}, {config_var['variable']}".lstrip(
                ","
            )

        configuration_results = f"Configuration settings, either from environmental variables, or other sources are stored in the following variables: {config_variables}."
    else:
        configuration_results = "No configuration settings (e.g., environmental variables, etc.) have been imported from this file."

    if len(python_inspection_results["loaded_modules"]["cryptographic_modules"]) > 0:
        cryptographic_results = f"Potential cryptographic operations are happening using the following modules. {python_inspection_results['loaded_modules']['cryptographic_modules']}."

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


if __name__ == "__main__":
    # Example usage
    r = start_inspection("/path/to/example.py")
    print(r)
