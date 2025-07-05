from traceback import format_exc
from textwrap import dedent
import re
from typing import List, Dict
from maposcal.utils.control_hints_enumerator import search_control_hints_in_content
import logging

logger = logging.getLogger()


def start_inspection(file_path):
    """
    Takes a Golang file and begins a non-generative inspection with the goal of returning a standardized inspection report covering many
    areas related to security and compliance.

    Args:
        file_path (str): Path to the Golang file that will be inspected

    Returns
        golang_inspection_results (dict): See README for full formatting details of the response.
    """
    golang_inspection_results = {}
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
        logger.debug(f"Opening Golang file ({file_path}) for inspection.")
        with open(file_path, "r") as fh:
            file_contents = fh.read()
    except Exception:
        logger.error(f"Failed opening Python file ({file_path}) - {format_exc()} ")

    if file_contents:
        try:
            ###
            # Parse for string-based control hints using the new enumerator
            # This searches all available controls, not just SC-8
            ###
            found_controls = search_control_hints_in_content(file_contents, "golang")
            applicable_control_hints.extend(found_controls)
            logger.info(
                f"Found {len(found_controls)} applicable controls in Golang file"
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
            cryptographic_module,
        ) = identify_imported_modules(file_contents)
        loaded_modules["modules"] = modules
        loaded_modules["network_modules"] = network_modules
        loaded_modules["file_system_modules"] = file_system_modules
        loaded_modules["logging_modules"] = logging_modules
        loaded_modules["cryptographic_module"] = cryptographic_module

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

    golang_inspection_results["file_path"] = file_path
    golang_inspection_results["language"] = "Golang"
    golang_inspection_results["control_hints"] = applicable_control_hints
    golang_inspection_results["loaded_modules"] = loaded_modules
    golang_inspection_results["configuration_settings"] = configuration_settings
    golang_inspection_results["file_system_interactions"] = file_system_interactions
    golang_inspection_results["cryptography"] = cryptography
    golang_inspection_results["identified_vulnerabilities"] = identified_vulnerabilities
    golang_inspection_results["access_controls"] = access_controls
    golang_inspection_results["authn_authz"] = authn_authz
    golang_inspection_results["input_validation"] = input_validation
    golang_inspection_results["logging"] = logging
    golang_inspection_results["error_handling"] = error_handling

    file_summary = summarize_discovery_content(golang_inspection_results)

    golang_inspection_results["file_summary"] = file_summary

    return golang_inspection_results


def summarize_discovery_content(golang_inspection_results):
    """
    Takes the final report of all discovered items and creates a human-readable, LLM-friendly summary of the file.
    This allows for seeding future LLM activities with the necessary guardrails to ensure an accurate summary of
    the code.  This summary is focused on attributes key for security and compliance efforts.

    Args:
        golang_inspection_results (dict): All attributes discovered by the start_inspection function
    Returns:
        file_summary (str): Human/LLM-readable summary of the file.
    """

    networking_results = ""
    file_system_results = ""
    logging_results = ""
    configuration_results = ""
    config_variables = ""
    cryptograhic_results = ""

    if len(golang_inspection_results["loaded_modules"]["network_modules"]) > 0:
        networking_results = f"Discovery of networking modules shows the following being used for connectivity: {golang_inspection_results["loaded_modules"]["network_modules"]}."
    else:
        networking_results = (
            "No networking capabilities have been detected in this file."
        )

    if len(golang_inspection_results["loaded_modules"]["file_system_modules"]) > 0:
        file_system_results = f"File system access is expected using the discovered modules: {golang_inspection_results["loaded_modules"]["file_system_modules"]}."
    else:
        file_system_results = "No file system access has been detected in this file."

    if len(golang_inspection_results["loaded_modules"]["logging_modules"]) > 0:
        logging_results = f"Logging capabilities are expected to be using these modules: {golang_inspection_results["loaded_modules"]["logging_modules"]}."
    else:
        logging_results = "No logging capabilities have been detected in this file."

    if len(golang_inspection_results["configuration_settings"]) > 0:
        for config_var in golang_inspection_results["configuration_settings"]:
            config_variables = f"{config_variables}, {config_var['variable']}".lstrip(
                ","
            )

        configuration_results = f"Configuration settings, either from environmental variables, or other sources are stored in the following variables: {config_variables}."
    else:
        configuration_results = "No configuration settings (e.g., environmental variables, etc.) have been imported from this file."

    if len(golang_inspection_results["loaded_modules"]["cryptographic_module"]) > 0:
        cryptograhic_results = f"Potential cryptographic operations are happening using the following modules. {golang_inspection_results["loaded_modules"]['cryptographic_module']}."

    file_summary = dedent(
        f"""\
        The file {golang_inspection_results["file_path"]} is written in {golang_inspection_results["language"]}. \
{networking_results} \
{file_system_results} \
{logging_results} \
{configuration_results} \
{cryptograhic_results}\
"""
    )

    return file_summary




def identify_imported_configuration_variables(
    file_contents: str,
) -> List[Dict[str, str]]:
    """
    Parses a Go code file and identifies configuration variables used in the code.
    Includes environment variables, flags, Viper, and struct decoding from file-based sources.

    Args:
        file_contents (str): Code contents of a module to be parsed for imported configuration variables.

    Returns:
        results (List[Dict[str, str]]): Method of ingestion, variable name, and source key.
    """

    patterns = [
        {
            "method": "Environment Variables (os.Getenv)",
            "regex": r'(?P<var>\w+)\s*[:=]{1,2}\s*os\.Getenv\(["\'](?P<key>[^"\']+)["\']\)',
        },
        {
            "method": "Environment Lookup (os.LookupEnv)",
            "regex": r'(?P<var>\w+)\s*,\s*\w+\s*[:=]{1,2}\s*os\.LookupEnv\(["\'](?P<key>[^"\']+)["\']\)',
        },
        {
            "method": "Command-line Flags (flag.X or flag.Var)",
            "regex": r'(?P<var>\w+)\s*[:=]{1,2}\s*flag\.(?:String|Int|Bool|Duration|.*Var)\(["\'](?P<key>[^"\']+)["\']',
        },
        {
            "method": "Viper Get (viper.Get*)",
            "regex": r'(?P<var>\w+)\s*[:=]{1,2}\s*viper\.Get\w*\(["\'](?P<key>[^"\']+)["\']\)',
        },
        {
            "method": "Viper BindEnv",
            "regex": r'viper\.BindEnv\(["\'](?P<key>[^"\']+)["\']\)',
        },
        {
            "method": "Viper SetDefault",
            "regex": r'viper\.SetDefault\(["\'](?P<key>[^"\']+)["\']\s*,',
        },
        {
            "method": "Struct Decoding (Unmarshal into config struct)",
            "regex": r"(?P<decoder>(json|yaml|viper))\.(Unmarshal|UnmarshalExact)\s*\(\s*&(?P<var>\w+)\s*\)",
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
    modules = []
    network_modules = []
    file_system_modules = []
    logging_modules = []
    cryptographic_modules = []

    REF_GOLANG_NETWORK_MODULES = [
        "net",
        "net/http",
        "net/url",
        "crypto/tls",
        "net/smtp",
        "golang.org/x/net/websocket",
        "golang.org/x/net/proxy",
        "net/rpc",
        "net/rpc/jsonrpc",
        "golang.org/x/net/icmp",
        "golang.org/x/net/http2",
    ]
    REF_GOLANG_FILE_SYSTEM_MODULES = [
        "io",
        "fmt",
        "os",
        "io/ioutil",
        "os/exec",
        "path/filepath",
        "embed",
        "bufio",
        "archive/zip",
        "tar",
        "syscall",
        "golang.org/x/sys/unix",
    ]
    REF_GOLANG_LOGGING_MODULES = [
        "log",
        "log/syslog",
        "logrus",
        "zap",
        "go.uber.org/zap",
        "zerolog",
        "klog",
        "k8s.io/klog",
        "github.com/sirupsen/logrus/hooks",
        "github.com/rs/zerolog/log",
        "lumberjack",
        "logfmt",
        "golang.org/x/exp/slog",
        "go.uber.org/multierr",
    ]
    REF_GOLANG_CRYPTOGRAPHIC_MODULES = [
        "crypto/sha256",
        "sha512",
        "crypto/md5",
        "crypto/aes",
        "crypto/rsa",
        "crypto/tls",
        "crypto/x509",
        "crypto/rand",
        "crypto/des",
        "crypto/dsa",
        "encoding/base64",
        "encoding/hex",
        "golang.org/x/crypto",
        "golang.org/x/crypto/openpgp",
        "golang.org/x/crypto/ssh",
        "golang.org/x/crypto/ocsp",
        "math/rand",
    ]

    logger.info("Beginning identification of imported Golang modules...")
    config_lines = file_contents.strip().split("\n")
    in_import_block = False

    for line in config_lines:
        stripped = line.strip()
        # Single-line import: import "os"
        if stripped.startswith("import ") and not stripped.endswith("("):
            # e.g., import "os"
            mod = stripped[len("import ") :].strip().strip('"')
            if mod:
                modules.append(mod)
                logger.info(f"Identified single-line import module ({mod})")
        # Start of multi-line import block
        elif stripped.startswith("import ("):
            in_import_block = True
            continue
        elif in_import_block:
            if stripped == ")":
                in_import_block = False
                continue
            # Each line in the block should be a module name in quotes
            mod = stripped.strip('"')
            if mod:
                modules.append(mod)
                logger.info(f"Identified multi-line import module ({mod})")

    # Assigned categories from list of identified modules.
    for module in modules:
        if module in REF_GOLANG_NETWORK_MODULES:
            network_modules.append(module)
            logger.info(f"Identified likely networking module ({module})")
        if module in REF_GOLANG_FILE_SYSTEM_MODULES:
            file_system_modules.append(module)
            logger.info(f"Identified likely file system module ({module})")
        if module in REF_GOLANG_LOGGING_MODULES:
            logging_modules.append(module)
            logger.info(f"Identified likely logging module ({module})")
        if module in REF_GOLANG_CRYPTOGRAPHIC_MODULES:
            cryptographic_modules.append(module)
            logger.info(f"Identified likely cryptographic module ({module})")

    return (
        modules,
        network_modules,
        file_system_modules,
        logging_modules,
        cryptographic_modules,
    )


if __name__ == "__main__":
    r = start_inspection(
        "/home/caleb/code/minio/docs/site-replication/gen-oidc-sts-cred.go"
    )
    print(r)
