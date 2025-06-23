"""
results = {
                file_path = "",
                control_hints = ['sc-8'],      -- This is additive, with this module also doing one based on sample_control_hints.
                loaded_modules = ['module_name'],
                file_system_interactions = ['file_path.test'],
                cryptography = {
                  transit_crypto_modules = {
                    library = 'boringssl',
                    cipher = 'cipher_123',
                    key_length = '256',
                    }
                  },
                  at_rest_crypto_modules = {
                    library = 'openssl',
                    cipher = 'aes256',
                    key_length = '256',
                    }
                  },
                identified_vulernabilities = {
                  cve_id = '',
                  ...
                  },
                access_controls = {
                  TODO
                  - Role checks
                  - ACLs / usage validation,
                  - Session timeouts, cookie usage, token expiration
                },
                authn_authz = {
                  suspected_authn = bool,
                  suspected_authz = bool,
                  suspected_password_storage = bool,
                  identified_passwords = bool,
                  mfa_usage = bool,
                },
                input_validation = {
                  validation_modules_identified = []
                },
                logging = {
                  logging_engine = '',
                  logging_location = '',
                  log_level = '',
                  log_file_contents = {
                    variable_log_content = bool,
                  }
                }
                error_handling = {
                  TODO
                  suspected_data_leakage_on_error = ""
                }
            }
"""

from maposcal.util.sample_control_hints as control_hints_def
from maposcal.util.utilities import parse_file_into_strings 

def start_inspection(file_path):
"""
"""

    # Open file

    # Parse for string-based control hints
    # Generic hints

    # Language-specific hints
    applicable_control_hints_language_strings = control_hints_strings_search_python(file_contents)


def control_hints_strings_search_python(file_contents):
    """
    Takes the contents of a Python file and parses it for known strings associated with control mappings.
    """

    # Parse into strings - utility
    identified_strings = parse_file_into_strings(file_contents)
    # Find hits - but we start with the smallest string set, which is the defined strings, not all the strings in the file's contents.
    for control_hit_strings_python in control_hints_def.sc8_python:
        for lang_string in identified_strings: 
            # Identify any hits




if __name__ == "__main__":
    start_inspection("test-python.py")