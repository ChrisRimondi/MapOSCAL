"""
maposcal.llm.prompt_templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Central store for all LLM prompt templates used by MapOSCAL.

Tips
----
* Keep the **system** message short and stable.
* Keep a dedicated **instructions** section so you can tweak style centrally.
* Use f-strings or `.format()` for lightweight variable replacement.
"""

from textwrap import dedent
from typing import List
import json

# ---------------------------------------------------------------------------
# 1. FILE-LEVEL SECURITY / COMPLIANCE SUMMARY
# ---------------------------------------------------------------------------

FILE_SUMMARY_SYSTEM = "You are a seasoned security auditor specialising in source-code reviews."
FILE_SUMMARY_INSTRUCTIONS = dedent(
    """
    Summarise the file below with a focus on:

    * security controls (e.g., authentication, authorisation, encryption, input validation)
    * compliance-relevant features (e.g., logging, auditing, IAM roles)
    * any obvious risks or TODOs

    **Return exactly one concise paragraph (<=120 words).**
    DO NOT include any text verbatim from the file.
    """
)

FILE_SUMMARY_PROMPT = (
    "{system}\n\n{instructions}\n\n"
    "------------ FILE START (name={filename}) ------------\n"
    "{file_content}\n"
    "------------- FILE END -------------\n\n"
    "Summary:"
)


def build_file_summary_prompt(filename: str, file_content: str) -> str:
    return FILE_SUMMARY_PROMPT.format(
        system=FILE_SUMMARY_SYSTEM,
        instructions=FILE_SUMMARY_INSTRUCTIONS,
        filename=filename,
        file_content=file_content,
    )


# ---------------------------------------------------------------------------
# 2. OSCAL CONTROL IMPLEMENTATION GENERATION
# ---------------------------------------------------------------------------

CONTROL_IMPL_SYSTEM = "You are a compliance automation assistant that writes OSCAL component definitions."
CONTROL_IMPL_INSTRUCTIONS = dedent(
    """
You are a security compliance expert analyzing a service's implementation of a specific security control.

For the control {control_id}: Name: {control_name}, Description: {control_description}, based on the provided context (documentation, configuration, or code), determine:

- `control-status` must be one of:  
    • "applicable and inherently satisfied"  
    • "applicable but only satisfied through configuration"  
    • "applicable but partially satisfied"  
    • "applicable and not satisfied"  
    • "not applicable"
    
    - ✅ If the control is applicable and inherently satisfied — explain how within the JSON control-explanation field.
    - ✅ If the control is applicable but only satisfied through configuration — explain your reasoning within the JSON control-explanation field and provide the configuration details within the JSON control-configuration field. Make sure to include the file path, key value, and line number of the configuration as applicable. Configuration files should be json or yaml files. Do not reference .md files or other type of documentation type files. 
    - ⚠️ If the control is applicable but represents a gap — clearly describe the gap within the JSON control-explanation field.
    - 🚫 If the control is not applicable to the system — provide a brief explanation in the control-explanation field (e.g., "This system does not transmit sensitive data over public networks.").

Do NOT wrap JSON in markdown fences.
Do NOT include comments inside JSON.

Use this structure and format for the JSON output:
{{
  "uuid": "{main_uuid}",
  "control-id": "{control_id}",
  "props": [
    {{
      "name": "control-status",
      "value": "applicable and inherently satisfied|applicable but only satisfied through configuration|applicable but partially satisfied|applicable and not satisfied|not applicable",
      "ns": "urn:maposcal:control-status-reference"
    }},
    {{
      "name": "control-name",
      "value": "{control_name}",
      "ns": "urn:maposcal:control-name-reference"
    }},
    {{
      "name": "control-description",
      "value": "{control_description}",
      "ns": "urn:maposcal:control-description-reference"
    }},
    {{
      "name": "control-explanation",
      "value": "Detailed explanation of how the control is implemented or why it is not applicable",
      "ns": "urn:maposcal:explanation-reference"
    }},
    {{
      "name": "control-configuration",
      "value": [
        {{
          "file_path": "path/to/config.yaml",
          "key_path": "security.authentication.enabled",
          "line_number": 42
        }}
      ],
      "ns": "urn:maposcal:configuration-reference"
    }}
  ],
  "annotations": [
    {{
      "name": "source-code-reference",
      "value": ["file1.py", "file2.yaml", "file3.json"],
      "ns": "urn:maposcal:source-code-reference"
    }}
  ],
  "statements": [
    {{
      "statement-id": "{control_id}_smt.a",
      "uuid": "{statement_uuid}",
      "description": "Detailed description of how the control statement is implemented"
    }}
  ]
}}

IMPORTANT NOTES:
- control-status must be exactly one of the 5 values shown above
- control-configuration.value must be an array of objects, each with file_path, key_path, and line_number
- file_path must end with .yaml, .yml, .json, .toml, .conf, .ini, .env, or source code extensions (.py, .js, .ts, .go, .java, .cpp, .c, .h, .cs, .php, .rb, .pl, .sh, .bash, .ps1)
- Do NOT use .md, .txt, or documentation files for file_path
- If control-status contains "configuration", control-configuration must have at least one object
- If control-status does NOT contain "configuration", control-configuration can be empty array []
- source-code-reference.value must be an array of strings (file names)
- All UUIDs must be valid UUID format

Return only valid, minified JSON.
"""
)

CONTROL_IMPL_PROMPT_HEADER = (
    "{system}\n\n{instructions}\n\n"
    "Control ID requested: **{control_id}**\n\n"
    "Semantic evidence chunks (top-{k}):\n"
)

CHUNK_BULLET = "- {chunk_type} • {source} • lines {start}-{end}\n```\n{content}\n```\n"

CONTROL_IMPL_PROMPT_FOOTER = "\n---\nGenerate the JSON now:"

CRITIQUE_REVISE_SYSTEM = """You are an expert in OSCAL and software-security evidence mapping.
Follow every JSON rule exactly; invalid JSON is never acceptable.
When asked to CRITIQUE, list flaws without rewriting the object.
When asked to REVISE, fix *only* the flagged flaws; keep everything else identical.
Never invent content you don't have evidence for.
Return raw, minified JSON—no markdown, no comments."""

CRITIQUE_PROMPT = """
{system}

You will receive a dictionary of an OSCAL `implemented_requirements` object.

Goal: identify every violation of the Draft-Prompt Guidelines below.

Draft-Prompt Guidelines
- If status contains "configuration", the `control-configuration` prop must have a **non-empty** array value containing objects with keys:
    file_path, key_path, line_number.
- `control-configuration` prop value array objects must have `file_path` ending with .yaml, .yml, .json, .toml, .conf, .ini, .env, or a source-code extension; **never** .md / .txt / directory.
- No fields outside the OSCAL spec or the above list.
- All string values must be plain strings (no JSON or markdown inside).

OUTPUT FORMAT  
Return a JSON object:
{{
  "valid": <boolean>,
  "violations": [
    {{
      "path": "<JSONPath to the problematic field>",
      "issue": "<short description>",
      "suggestion": "<if obvious, one-line fix or 'remove'>"
    }},
    ...
  ]
}}

Begin when ready.  Here is the input array:

<<<{implemented_requirements_json}>>>
"""

REVISE_PROMPT = """
{system}

You are given:
1. The original `implemented_requirements` array.
2. A `violations` list produced by the Critique step (same schema as above).

Task: produce a **repaired** version of the array that resolves *every* violation,
without altering any other content.

Rules
- Preserve all original field order unless you must add / remove / reorder for validity.
- If a `control-configuration` must be emptied (per suggestion: "remove"), also
  change `control-status` to "applicable and not satisfied".
- After fixes, the object set **must** pass the Guidelines from the Critique prompt.

Return the full, minified JSON array—nothing else.

INPUT
"original": <<<{implemented_requirements_json}>>>
"violations": <<<{critique_violations_json}>>>

"""


def build_control_prompt(control_id: str, control_name: str, control_description: str, evidence_chunks: List[dict], k: int, main_uuid: str, statement_uuid: str) -> str:
    instructions = CONTROL_IMPL_INSTRUCTIONS.format(
        control_id=control_id,
        control_name=control_name,
        control_description=control_description,
        main_uuid=main_uuid,
        statement_uuid=statement_uuid
    )
    header = CONTROL_IMPL_PROMPT_HEADER.format(
        system=CONTROL_IMPL_SYSTEM,
        instructions=instructions,
        control_id=control_id,
        k=k,
    )
    body = ""
    for c in evidence_chunks:
        body += CHUNK_BULLET.format(
            chunk_type=c.get("chunk_type", "unknown"),
            source=c.get("source_file", "N/A"),
            start=c.get("start_line", "?"),
            end=c.get("end_line", "?"),
            content=(c.get("content") or c.get("summary", "")).strip()[:800],  # protect context length
        )
    return header + body + CONTROL_IMPL_PROMPT_FOOTER

def build_critique_prompt(implemented_requirements: List[dict]) -> str:
    """Build a prompt for critiquing implemented requirements."""
    return CRITIQUE_PROMPT.format(
        system=CRITIQUE_REVISE_SYSTEM,
        implemented_requirements_json=json.dumps(implemented_requirements)
    )

def build_revise_prompt(implemented_requirements: List[dict], violations: List[dict]) -> str:
    """Build a prompt for revising implemented requirements based on violations."""
    return REVISE_PROMPT.format(
        system=CRITIQUE_REVISE_SYSTEM,
        implemented_requirements_json=json.dumps(implemented_requirements),
        critique_violations_json=json.dumps(violations)
    )
