# Non-Generative Inspectors

This module provides custom, as well as tool-based inspection of a file/module to allow
a more accurate inspection of capabilities. Created to be modular and community-driven,
each file type (e.g., '.py') has a dedicated inspector (e.g., inspect-lang-python). In
addition, tooling-based inspectors (e.g., Semgrep, etc.) are also available as plugins.
This module should only be treated as a gateway or router, with the type-specific analysis
being performed by the appropriate modules, which in-turn return data here for formatting and
inclusion as part of the overall picture.

File inspection is accomplished at a file (NOT chunk) level, and the results are stored as
part of the `summary_meta.json` file, with details under each file path key. This is due
to the necessity to have these details at a file level, and not a chunked subset (such as those
found in the `meta.json`). Additionally, file-level is required as external scanners don't function
on subsets of data, but generally require a working/valid file to analyse.

Each inspector receives a file path to the file to be inspected. It then parses the file to
return a defined dictionary of key information. The syntax returned by each inspector is in
the below format for consistent data parsing and usage.

Once the results are returned they are stored in the `summary_meta.json` file, which is later parsed
by the `control_mapper.get_relevant_chunks()` and included in the overall assessment.

## Inspector Output Format

```python
results = {
    "file_path": "",
    "control_hints": ['sc-8'],  # This is additive, with this module also doing one based on sample_control_hints.
    "loaded_modules": {
        'modules': 'module_name', 
        'network_modules': 'requests', 
        'file_system_modules': 'os', 
        'cryptographic_modules': 'openssl'
    },
    "file_system_interactions": ['file_path.test'],
    "cryptography": {
        "transit_crypto_modules": {
            "library": 'boringssl',
            "cipher": 'cipher_123',
            "key_length": '256',
        },
        "at_rest_crypto_modules": {
            "library": 'openssl',
            "cipher": 'aes256',
            "key_length": '256',
        }
    },
    "identified_vulnerabilities": {
        "cve_id": '',
        # ... additional vulnerability information
    },
    "access_controls": {
        # TODO: Implement role checks, ACLs, session timeouts, cookie usage, token expiration
        "role_checks": [],
        "acls": [],
        "session_timeouts": [],
        "cookie_usage": [],
        "token_expiration": []
    },
    "authn_authz": {
        "suspected_authn": bool,
        "suspected_authz": bool,
        "suspected_password_storage": bool,
        "identified_passwords": bool,
        "mfa_usage": bool,
    },
    "input_validation": {
        "validation_modules_identified": []
    },
    "logging": {
        "logging_engine": '',
        "logging_location": '',
        "log_level": '',
        "log_file_contents": {
            "variable_log_content": bool,
        }
    },
    "error_handling": {
        # TODO: Implement data leakage detection on error
        "suspected_data_leakage_on_error": ""
    }
}
```

## Available Inspectors

- `inspect_lang_python.py` - Python code inspection
- `inspect_lang_golang.py` - Golang code inspection

## Integration

Inspectors are automatically called during the analysis phase and their results are integrated
into the overall security assessment. The control hints discovered by inspectors are used to
improve the accuracy of control mapping in the generation phase.