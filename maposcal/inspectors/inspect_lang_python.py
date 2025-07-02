from traceback import format_exc
from textwrap import dedent
import re
from typing import List, Dict
import maposcal.utils.sample_control_hints as control_hints
from maposcal.utils.utilities import (
    parse_file_into_strings,
    control_hints_strings_search,
)
import logging

logger = logging.getLogger()


def start_inspection(file_path):
    """
    Takes a Python file and begins a non-generative inspection with the goal of returning a standardized inspection report covering many
    areas related to security and compliance.  This data can be used to enrich any generative AI results.

    Args:
        file_path (str): Path to the Python file that will be inspected

    Returns
        python_inspection_results (dict): See README for full formatting details of the response.
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
    logging = {}
    error_handling = {}

    try:
        logger.debug(f"Opening Python file ({file_path}) for inspection.")
        with open(file_path, "r") as fh:
            file_contents = fh.read()
    except:
        logger.error(f"Failed opening Python file ({file_path}) - {format_exc()} ")

    if file_contents:
        ###
        # Parse for string-based control hints, first generic strings, then language-specific hits.  This is currently limited
        #   to SC-8 as global variables for the open source release.
        ###
        try:
            applicable_control_hints_strings = control_hints_strings_search(
                file_contents, control_hints.sc8, "SC-8"
            )
            applicable_control_hints_language_strings = control_hints_strings_search(
                file_contents, control_hints.sc8_python, "SC-8"
            )

            if (
                applicable_control_hints_strings
                or applicable_control_hints_language_strings
            ):
                applicable_control_hints.append("SC-8")
        except:
            logger.error(f"Failed to parse contents of {file_path} for strings - {format_exc()}")
        ###
        # Parse for loaded modules - shows what applicable functionality is likely used.
        ###
        modules, network_modules, file_system_modules, logging_modules, cryptographic_module = identify_imported_modules(file_contents)
        loaded_modules['modules'] = modules
        loaded_modules['network_modules'] = network_modules
        loaded_modules['file_system_modules'] = file_system_modules
        loaded_modules['logging_modules'] = logging_modules
        loaded_modules['cryptographic_module'] = cryptographic_module

        ###
        # Parse for configuration ingestion (e.g., environmental variables, etc.)
        ###
        configuration_settings = identify_imported_configuration_variables(file_contents)

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

    else:
        logger.error(f"Failed to retrieve contents of {file_path} for analysis.")


    python_inspection_results["file_path"] = file_path
    python_inspection_results["language"] = 'Python'
    python_inspection_results["control_hints"] = applicable_control_hints
    python_inspection_results["loaded_modules"] = loaded_modules
    python_inspection_results["configuration_settings"] = configuration_settings
    python_inspection_results["file_system_interactions"] = file_system_interactions
    python_inspection_results["cryptography"] = cryptography
    python_inspection_results["identified_vulnerabilities"] = identified_vulnerabilities
    python_inspection_results["access_controls"] = access_controls
    python_inspection_results["authn_authz"] = authn_authz
    python_inspection_results["input_validation"] = input_validation
    python_inspection_results["logging"] = logging
    python_inspection_results["error_handling"] = error_handling

    file_summary = summarize_discovery_content(python_inspection_results)

    python_inspection_results["file_summary"] = file_summary

    return python_inspection_results


def summarize_discovery_content(python_inspection_results):
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
    cryptograhic_results = ""

    if len(python_inspection_results["loaded_modules"]["network_modules"]) > 0:
        networking_results = f"Discovery of networking modules shows the following being used for connectivity: {python_inspection_results["loaded_modules"]["network_modules"]}."
    else:
        networking_results = "No networking capabilities have been detected in this file."

    if len(python_inspection_results["loaded_modules"]["file_system_modules"]) > 0:
        file_system_results = f"File system access is expected using the discovered modules: {python_inspection_results["loaded_modules"]["file_system_modules"]}."
    else:
        file_system_results = "No file system access has been detected in this file."

    if len(python_inspection_results["loaded_modules"]["logging_modules"]) > 0:
        logging_results = f"Logging capabilities are expected to be using these modules: {python_inspection_results["loaded_modules"]["logging_modules"]}."
    else:
        logging_results = "No logging capabilities have been detected in this file."

    if len(python_inspection_results["configuration_settings"]) > 0:
        configuration_results = f"Configuration settings, either from environmental variables, or other sources are established using {python_inspection_results["configuration_settings"]}."
    else:
        configuration_results = "No configuration settings (e.g., environmental variables, etc.) have been imported from this file."

    if len(python_inspection_results["loaded_modules"]['cryptographic_module']) > 0:
        cryptograhic_results = f"Potential cryptographic operations are happening using the following modules. {python_inspection_results["loaded_modules"]['cryptographic_module']}."


    file_summary = dedent(f"""\
        The file {python_inspection_results["file_path"]} is written in {python_inspection_results["language"]}. \
{networking_results} \
{file_system_results} \
{logging_results} \
{configuration_results} \
{cryptograhic_results}\
""")

    return file_summary


def identify_imported_configuration_variables(file_contents: str) -> List[Dict[str, str]]:
    """
    Parses a code file and identifies as many configuration variables as possible that are utilized by the code.
    Items such as use of dotenv, or loading environmental variables.  Identification of these items allows for
    other inspectors to cleanly identify configuration details that might otherwise be vague.

    Args:
        file_contents (str): Code contents of a module to be parsed for imported configuration variables.
    Returns:
        results (dict): Method of ingestion (e.g., environment variable), variable in code, as well as source name.
    """

    patterns = [
        {
            "method": "Environment Variables",
            "regex": r"(?P<var>\w+)\s*=\s*os\.getenv\(\s*['\"](?P<key>[^'\"]+)['\"]\s*\)"
        },
        {
            "method": "Environment Variables (dict style)",
            "regex": r"(?P<var>\w+)\s*=\s*os\.environ\[\s*['\"](?P<key>[^'\"]+)['\"]\s*\]"
        },
        {
            "method": ".env File (dotenv)",
            "regex": r"(load_dotenv\(\))"
        },
        {
            "method": "Command-line Arguments",
            "regex": r"(?P<var>\w+)\s*=\s*argparse\.ArgumentParser\("
        },
        {
            "method": "Command-line Flags (sys)",
            "regex": r"(?P<var>\w+)\s*=\s*sys\.argv(\[\d+\])?"
        },
        {
            "method": "Pickle File",
            "regex": r"(?P<var>\w+)\s*=\s*pickle\.load\(\s*open\(\s*['\"](?P<key>[^'\"]+)['\"]"
        },
        {
            "method": "Docker Secrets",
            "regex": r"(?P<var>\w+)\s*=\s*open\(\s*['\"]\/run\/secrets\/(?P<key>[^'\"]+)['\"]"
        }
    ]

    results = []

    for pattern in patterns:
        matches = re.finditer(pattern["regex"], file_contents)
        for match in matches:
            result = {
                "method": pattern["method"],
                "variable": match.group("var") if "var" in match.groupdict() else "",
                "source": match.group("key") if "key" in match.groupdict() else ""
            }
            results.append(result)

    return results


def identify_imported_modules(file_contents):
    """
    Parses a code file and identifies all modules that are imported and used by the code.  Uses a hard-coded reference
    to classify commonly-used modules applicable to security and compliance usecases (e.g., networking, cryptography, etc.).
    Because these references (prefixed with REF_) are statically assigned, they should be periodically updated.

    Args:
        file_contents (str): Contents of a code module to be parsed for imported modules.
    Returns:
        modules (list): All modules identified
        network_modules (list): All networking modules based on hard-coded reference.
        file_system_modules (list): All modules for interacting with the file system.
        logging_modules (list): All logging modules used.
        cryptographic_modules (list): Any modules used for cryptographic operations. 
    """
    line_number = 0
    modules = []
    network_modules = []
    file_system_modules = []
    logging_modules = []
    cryptographic_modules = []

    REF_PYTHON_NETWORK_MODULES = ['socket', 'requests', 'http.client', 'urllib', 'asyncio', 'paramiko', 'ftplib', 'telnetlib', 'scapy', 'twisted', 'dpky', 'pyshark', 'websockets', 'ssl', 'openssl']
    REF_PYTHON_FILE_SYSTEM_MODULES = ['os', 'shutil', 'pathlib', 'open', 'glob', 'stat', 'tempfile', 'subprocess', 'pickle', 'marshal', 'tarfile', 'zipfile', 'ctypes' ,'fcntl', 'watchdog']
    REF_PYTHON_LOGGING_MODULES = ['logging', 'print', 'loguru', 'sys', 'traceback', 'warnings', 'coloredlogs', 'structlog', 'sentry_sdk', 'fluent-logger']
    REF_PYTHON_CRYPTOGRAPHIC_MODULES = ['hashlib', 'hmac', 'secrets', 'random', 'cryptography', 'pycryptodome', 'ssl', 'base64', 'jwt', 'pyjwt', 'openssl', 'pyopenssl']

    # Split lines
    logger.info(f"Beginning identification of imported Python modules...")
    config_lines = file_contents.lower().strip().split('\n')
    
    for line in config_lines:
        line_number += 1
        line_details = line.split(' ')
        
        # Identify one of more modules using import
        if line_details[0] == 'import':
            # iterate through modules but stop at aliasing
            for m in line_details[1:]:
                if m == 'as':
                    break
                else:
                    modules.append(m)
                    logger.info(f"Identified module ({m}) at line {line_number}")

        # Since we're only tracking top-level modules, this inspection isn't granular.
        if line_details[0] == 'from':
            for m in line_details[1:]:
                if m == 'import':
                    break
                else:
                    modules.append(m)
                    logger.info(f"Identified module ({m}) at line {line_number}")

    # Assigned catagories from list of identified modules.
    for module in modules:
        if module in REF_PYTHON_NETWORK_MODULES:
            network_modules.append(module)
            logger.info(f"Identified likely networking module ({module})")
        if module in REF_PYTHON_FILE_SYSTEM_MODULES:
            file_system_modules.append(module)
            logger.info(f"Identified likely file system module ({module})")
        if module in REF_PYTHON_LOGGING_MODULES:
            logging_modules.append(module)
            logger.info(f"Identified likely logging module ({module})")
        if module in REF_PYTHON_CRYPTOGRAPHIC_MODULES:
            cryptographic_modules.append(module)
            logger.info(f"Identified likely cryptograhic module ({module})")

    return modules, network_modules, file_system_modules, logging_modules, cryptographic_modules


if __name__ == "__main__":
    r = start_inspection('inspect_lang_python.py')
    print(r)
