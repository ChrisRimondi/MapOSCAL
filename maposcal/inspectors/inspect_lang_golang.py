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
    except:
        logger.error(f"Failed opening Python file ({file_path}) - {format_exc()} ")

    if file_contents:
        try:
            # Parse for string-based control hints, first generic strings, then language-specific hits.
            applicable_control_hints_strings = control_hints_strings_search(
                file_contents, control_hints.sc8, "SC-8"
            )
            applicable_control_hints_language_strings = control_hints_strings_search(
                file_contents, control_hints.sc8_golang, "SC-8"
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

    golang_inspection_results["file_path"] = file_path
    golang_inspection_results["control_hints"] = applicable_control_hints
    golang_inspection_results["loaded_modules"] = loaded_modules
    golang_inspection_results["file_system_interactions"] = file_system_interactions
    golang_inspection_results["cryptography"] = cryptography
    golang_inspection_results["identified_vulnerabilities"] = identified_vulnerabilities
    golang_inspection_results["access_controls"] = access_controls
    golang_inspection_results["authn_authz"] = authn_authz
    golang_inspection_results["input_validation"] = input_validation
    golang_inspection_results["logging"] = logging
    golang_inspection_results["error_handling"] = error_handling

    return golang_inspection_results


def identify_imported_modules(file_contents):
    """
    Parses a Golang file and identifies all modules that are imported and used by the code.  Uses a hard-coded reference
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
    modules_section = False

    modules = []
    network_modules = []
    file_system_modules = []
    logging_modules = []
    cryptographic_modules = []

    REF_GOLANG_NETWORK_MODULES = ['net', 'net/http', 'net/url', 'crypto/tls', 'net/smtp', 'golang.org/x/net/websocket', 'golang.org/x/net/proxy', 'net/rpc', 'net/rpc/jsonrpc', 'golang.org/x/net/icmp', 'golang.org/x/net/http2']
    REF_GOLANG_FILE_SYSTEM_MODULES = ['io', 'fmt', 'os', 'io/ioutil', 'os/exec', 'path/filepath', 'embed', 'bufio', 'archive/zip', 'tar', 'syscall', 'golang.org/x/sys/unix']
    REF_GOLANG_LOGGING_MODULES = ['log', 'log/syslog', 'logrus', 'zap', 'go.uber.org/zap', 'zerolog', 'klog', 'k8s.io/klog', 'github.com/sirupsen/logrus/hooks', 'github.com/rs/zerolog/log', 'lumberjack', 'logfmt', 'golang.org/x/exp/slog', 'go.uber.org/multierr']
    REF_GOLANG_CRYPTOGRAPHIC_MODULES = ['crypto/sha256', 'sha512', 'crypto/md5', 'crypto/aes', 'crypto/rsa', 'crypto/tls', 'crypto/x509', 'crypto/rand', 'crypto/des', 'crypto/dsa' 'encoding/base64', 'encoding/hex' 'golang.org/x/crypto', 'golang.org/x/crypto/openpgp', 'golang.org/x/crypto/ssh', 'golang.org/x/crypto/ocsp', 'math/rand']

    # Split lines
    logger.info(f"Beginning identification of imported Golang modules...")
    config_lines = file_contents.lower().strip().split('\n')
    
    for line in config_lines:
        # This can be multi-line...
        line_number += 1
        line_details = line.split(' ')
        
        """
        import (
        "encoding/base64"
        "net/http"
        "sort"
        "testing"

        xhttp "github.com/minio/minio/internal/http"
        )
        """
        if not modules_section:
            if line_details[0] == 'import':
                modules_section = True

                # Check for multiple import
                if line_details[1] == '(':
                    if len(line_details) > 2:
                        logger.debug(f"Identified multiple packages on the same line ({line_number}).")
                        for m in line_details[3:]:
                            modules.append(m)
                            logger.info(f"Identified multi-package line with module ({m}) at line {line_number}")
                    else:
                        # Move to the next line.
                        continue
    
        if modules_section:
            # We know that we're inside an import statement
            # Figure out if we are at the end and need to exit
            if line_details[0] == ')':
                modules_section = False
                continue
            else:
                # Still inside, so discovery continues... and we remove the quotes used in Go
                m = line_details[0].strip().lstrip('"').rstrip('"')
                # Ignore blank lines
                if len(m) > 1:
                    modules.append(m)
                    logger.info(f"Identified module ({m}) at line {line_number}")


    # Assigned catagories from list of identified modules.
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
            logger.info(f"Identified likely cryptograhic module ({module})")

    return modules, network_modules, file_system_modules, logging_modules, cryptographic_modules


if __name__ == "__main__":
    r = start_inspection('/home/caleb/code/minio/internal/crypto/crypto.go')
    print(r)
