from traceback import format_exc
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
        #   to SC-8 as global variables.
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
        # Parse for loaded modules
        ###
        modules, network_modules, file_system_modules, logging_modules, cryptographic_module = identify_imported_modules(file_contents)
        loaded_modules['modules'] = modules
        loaded_modules['network_modules'] = network_modules
        loaded_modules['file_system_modules'] = file_system_modules
        loaded_modules['logging_modules'] = logging_modules
        loaded_modules['cryptographic_module'] = cryptographic_module

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
    else:
        logger.error(f"Failed to retrieve contents of {file_path} for analysis.")


    python_inspection_results["file_path"] = file_path
    python_inspection_results["control_hints"] = applicable_control_hints
    python_inspection_results["loaded_modules"] = loaded_modules
    python_inspection_results["file_system_interactions"] = file_system_interactions
    python_inspection_results["cryptography"] = cryptography
    python_inspection_results["identified_vulnerabilities"] = identified_vulnerabilities
    python_inspection_results["access_controls"] = access_controls
    python_inspection_results["authn_authz"] = authn_authz
    python_inspection_results["input_validation"] = input_validation
    python_inspection_results["logging"] = logging
    python_inspection_results["error_handling"] = error_handling

    return python_inspection_results


def identify_imported_modules(file_contents):
    """
    Parses a Python file and identifies all modules that are imported and used by the code.  Uses a hard-coded reference
    to classify commonly-used modules applicable to security and compliance usecases (e.g., networking, cryptography, etc.).
    Because these references (prefixed with REF_) are statically assigned, they should be periodically updated.

    Args:
        file_contents (str): Contents of a Python module to be parsed for imported modules.
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
