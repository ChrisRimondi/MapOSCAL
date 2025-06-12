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

- Status of the control: (applicable and inherently satisfied, applicable but only satisfied through configuration, gap, or not applicable)
    - ✅ If the control is applicable and inherently satisfied — explain how within the JSON explanation field.
    - ✅ If the control is applicable but only satisfied through configuration — explain your reasoning within the JSON explanation field and provide the configuration details within the JSON configuration field. Make sure to include the file path, key value, and line number of the configuration as applicable. Configuration files should be json or yaml files. Do not reference .md files or other type of documentation type files. 
    - ⚠️ If the control is applicable but represents a gap — clearly describe the gap within the JSON explanation field.
    - 🚫 If the control is not applicable to the system — provide a brief explanation in the `explanation` field (e.g., "This system does not transmit sensitive data over public networks.").

Use this structure and format for the JSON output:
{{
  "control-id": "{control_id}",
  "control-name": "{control_name}",
  "description": "{control_description}",
  "status": "applicable and inherently satisfied | applicable but only satisfied through configuration | gap | not applicable",
  "explanation": "string explaining the status of the control",
  "configuration": "string explaining the configuration of the control",
  "files_used": "list of files used to determine the status of the control"
}}
"""
)

CONTROL_IMPL_PROMPT_HEADER = (
    "{system}\n\n{instructions}\n\n"
    "Control ID requested: **{control_id}**\n\n"
    "Semantic evidence chunks (top-{k}):\n"
)

CHUNK_BULLET = "- {chunk_type} • {source} • lines {start}-{end}\n```\n{content}\n```\n"

CONTROL_IMPL_PROMPT_FOOTER = "\n---\nGenerate the JSON now:"

def build_control_prompt(control_id: str, control_name: str, control_description: str, evidence_chunks: List[dict], k: int) -> str:
    instructions = CONTROL_IMPL_INSTRUCTIONS.format(
        control_id=control_id,
        control_name=control_name,
        control_description=control_description,
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