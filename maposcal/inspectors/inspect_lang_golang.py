from traceback import format_exc
import maposcal.utils.sample_control_hints as control_hints
from maposcal.utils.utilities import parse_file_into_strings, control_hints_strings_search

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
    loaded_modules = []
    file_system_interactions = []
    file_contents = ''
    cryptography = {}
    identified_vulnerabilities = {}
    access_controls = {}
    authn_authz = {}
    input_validation = {}
    logging = {}
    error_handling = {}

    try: 
        logger.debug(f"Opening Golang file ({file_path}) for inspection.")
        with open(file_path, 'r') as python_fh:
            file_contents = python_fh.read()
    except:
        logger.error(f"Failed opening Python file ({file_path}) - {format_exc()} ")

    if file_contents:
        # Parse for string-based control hints, first generic strings, then language-specific hits.
        applicable_control_hints_strings = control_hints_strings_search(file_contents, control_hints.sc8 , 'SC-8' )
        applicable_control_hints.append(applicable_control_hints_strings)
        # Language-specific hits.
        applicable_control_hints_language_strings = control_hints_strings_search(file_contents, control_hints.sc8_golang, 'SC-8' )
        applicable_control_hints.append(applicable_control_hints_language_strings)

    golang_inspection_results['file_path'] = file_path
    golang_inspection_results['control_hints'] = applicable_control_hints
    golang_inspection_results['loaded_modules'] = loaded_modules
    golang_inspection_results['file_system_interactions'] = file_system_interactions
    golang_inspection_results['cryptography'] = cryptography
    golang_inspection_results['identified_vulnerabilities'] = identified_vulnerabilities
    golang_inspection_results['access_controls'] = access_controls
    golang_inspection_results['authn_authz'] = authn_authz
    golang_inspection_results['input_validation'] = input_validation
    golang_inspection_results['logging'] = logging
    golang_inspection_results['error_handling'] = error_handling

    return golang_inspection_results


def control_hints_strings_search_golang(file_contents):
    """
    Takes the contents of a Golang file and parses it for known strings associated with control mappings. If a
    match is found, the applicable flag is returned.
    """
    applicable_control_hints = []

    # Parse into strings - utility
    identified_strings = parse_file_into_strings(file_contents)

    #   This is where future magic has to happen to identify all the applicable control families, not just SC-8.
    # The current configuration is for example purposes only, scale requires a different model of storing these.

    #   Find hits - but we start with the smallest string set, which is the defined strings, not all the strings in 
    # the file's contents.  This is really a job for Redis, etc., but sufficient as an example.
    for control_hit_string in control_hints_def.sc8_golang:
        logger.debug(f"Searching for string ({control_hit_string})...")
        for lang_string in identified_strings: 
            # Identify any hits
            if control_hit_string == lang_string:
                #   We don't care about additional hits, the control hint is now active.  However, future work
                # might add weight to the findings based on the number of occurances...
                logger.info(f"Identified SC-8 control applicability based on string ({control_hit_string}).")
                applicable_control_hints.append('sc-8')
                break

    return applicable_control_hints


if __name__ == "__main__":
    start_inspection("inspect_lang_python.py")