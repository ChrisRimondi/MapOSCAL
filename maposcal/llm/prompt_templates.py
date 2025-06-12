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
    Based on the source evidence chunks provided, draft an **OSCAL `implemented_requirement`** object
    for the control ID requested.  Ensure:

    * The `description` explains **how** the control is met (not just *that* it is met).
    * Include relevant parameters or references if available.
    * Output MUST be valid **YAML** inside a Markdown code-block so downstream tooling can parse it.

    Example output:

    ```yaml
    implemented_requirement:
      control_id: AC-6
      description: >
        Access to administrative endpoints is restricted to users in the "admin" role, enforced
        by middleware `AuthZMiddleware` (src/authz.py:14-87). ...
    ```
    """
)

CONTROL_IMPL_PROMPT_HEADER = (
    "{system}\n\n{instructions}\n\n"
    "Control ID requested: **{control_id}**\n\n"
    "Semantic evidence chunks (top-{k}):\n"
)

CHUNK_BULLET = "- {chunk_type} • {source} • lines {start}-{end}\n```\n{content}\n```\n"

CONTROL_IMPL_PROMPT_FOOTER = "\n---\nGenerate the YAML now:"

def build_control_prompt(control_id: str, evidence_chunks: List[dict], k: int) -> str:
    header = CONTROL_IMPL_PROMPT_HEADER.format(
        system=CONTROL_IMPL_SYSTEM,
        instructions=CONTROL_IMPL_INSTRUCTIONS,
        control_id=control_id,
        k=k,
    )
    body = ""
    for c in evidence_chunks:
        body += CHUNK_BULLET.format(
            chunk_type=c.get("chunk_type", "unknown"),
            source=c["source_file"],
            start=c.get("start_line", "?"),
            end=c.get("end_line", "?"),
            content=c["content"].strip()[:800],  # protect context length
        )
    return header + body + CONTROL_IMPL_PROMPT_FOOTER


# ---------------------------------------------------------------------------
# 3. AD-HOC QUESTION / ANSWER TEMPLATE  (optional utility)
# ---------------------------------------------------------------------------

QNA_SYSTEM = "You are a helpful assistant for compliance engineering tasks."
QNA_TEMPLATE = "{system}\n\nUser question:\n{question}\n\nAnswer briefly:"

def build_qna_prompt(question: str) -> str:
    return QNA_TEMPLATE.format(system=QNA_SYSTEM, question=question)
