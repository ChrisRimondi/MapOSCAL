from maposcal.inspectors import inspect_lang_python, inspect_lang_golang
from traceback import format_exc
import logging

logger = logging.getLogger()


def begin_inspection(file_path, base_dir=None):
    """
    Takes a list of files (the same files that have been chunked for LLM inspection), but will now be used in a non-generative
    method using modular inspection techniques.  This function will:
      * Identify the appropriate inspector(s) for each file
      * Run a strings-based search to identify appropriate control hints.
      * Run the identified inspector(s)
      * Consolidate the returned results
      * Consolidate all control hints
      * Send discovered results for assignment as metadata

    Args:
      file_path (string): Path to a file that will be inspected for further clarifying details.
      base_dir (string, optional): Base directory to truncate file_path relative to. If provided, file_path will be stored as relative to this directory.

    Returns:
      inspection_results (dict): See README in inspectors directory for full formatting details of the response.
    """
    inspection_results = {
        "file_path": file_path,
        "language": "unknown",
        "control_hints": [],
        "loaded_modules": {
            "modules": [],
            "network_modules": [],
            "file_system_modules": [],
            "logging_modules": [],
            "cryptographic_module": [],
        },
        "configuration_settings": [],
        "file_system_interactions": [],
        "cryptography": {},
        "identified_vulnerabilities": {},
        "access_controls": {},
        "authn_authz": {},
        "input_validation": {},
        "logging": {},
        "error_handling": {},
        "file_summary": f"No specific inspection available for {file_path}. This file type is not currently supported by the automated inspectors.",
    }

    logger.info(f"Beginning inspection of {file_path}.")

    # Identify appropriate inspector(s) - Language specific
    if ".py" in file_path.lower():
        logger.info(
            f"Marking {file_path} as type (Python) and running local inspector."
        )
        try:
            inspection_results = inspect_lang_python.start_inspection(file_path, base_dir)
        except Exception:
            logger.error(f"Failed to launch Python inspector - {format_exc()}")

    if ".go" in file_path.lower():
        logger.info(
            f"Marking {file_path} as type (Golang) and running local inspector."
        )
        try:
            inspection_results = inspect_lang_golang.start_inspection(file_path, base_dir)
        except Exception:
            logger.error(f"Failed to launch Golang inspector - {format_exc()}")
    return inspection_results


""" OLD CODE
def apply_rules(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    Apply security rules to code chunks and identify relevant security controls.
    
    Args:
        chunks: List of dictionaries containing code chunks with their content
        
    Returns:
        Updated list of chunks with added security flags and control hints:
        - security_flags: Dictionary of boolean flags for security features
        - control_hints: List of relevant security control identifiers
  
    for chunk in chunks:
        content = chunk.get("content", "").lower()
        flags = {
            "uses_tls": "tls" in content or "https" in content,
            "hardcoded_secret": "secret" in content or "apikey" in content,
            "auth_check": "token" in content or "auth" in content
        }
        chunk["security_flags"] = flags
        chunk["control_hints"] = []
        if flags["uses_tls"]:
            chunk["control_hints"].append("SC-8")
        if flags["auth_check"]:
            chunk["control_hints"].append("AC-6")
    return chunks
    """
