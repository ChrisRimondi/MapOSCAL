"""
maposcal.llm.prompt_templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Central store for all LLM prompt templates used by MapOSCAL.

This module contains all the prompt templates used for different LLM interactions:
- Service security overview generation
- File-level security/compliance summaries
- OSCAL control implementation generation with security context
- Control validation and revision with security overview integration
- Quality evaluation of existing controls

Key Features:
- Security overview integration for improved control mapping accuracy
- Context-aware prompting with service-level security understanding
- Structured JSON output with deterministic formatting
- Comprehensive validation and revision capabilities

Tips
----
* Keep the **system** message short and stable.
* Keep a dedicated **instructions** section so you can tweak style centrally.
* Use f-strings or `.format()` for lightweight variable replacement.
* Templates are designed to be deterministic and produce consistent JSON output.
* Security overview context is integrated into control mapping for better accuracy.
"""

from textwrap import dedent
from typing import List
import json

# ---------------------------------------------------------------------------
# 0. Service Overview
# --------------------------------------------------------------------------
SERVICE_OVERVIEW_SYSTEM = """
You are a senior security engineer analyzing a service. 
"""

SERVICE_OVERVIEW_INSTRUCTIONS = dedent(
    """
    Based on the following context from the service's code and documentation, generate a comprehensive security summary that includes:
    
    1. Service Overview
   - Main purpose and functionality
   - Key architectural components
   - Technical stack and dependencies

  2. Authentication and Authorization
    - Authentication mechanisms
    - Authorization models and policies
    - Identity management
    - Session handling
    - Access control implementation

  3. Encryption and Data Protection
    - Data encryption at rest
    - Data encryption in transit
    - Key management
    - Secure configuration
    - Data handling and storage

  4. Audit Logging and Monitoring
    - Audit logging mechanisms
    - Log formats and structures
    - Log retention policies
    - Monitoring systems
    - Alert mechanisms
    - Compliance reporting

  Focus on security aspects and technical implementations. Do not make any recommendations. This is just a summary based on the code and documentation in the context you are provided. Do not make anything up. You are only to use the context provided to write this summary.
  
  IMPORTANT: Return ONLY the markdown content. Do NOT wrap your response in markdown code blocks (```markdown). Do NOT add any notes, disclaimers, or additional text at the end. Start directly with the first heading and end with the last section.

Context:
{context}
    """
)

SERVICE_OVERVIEW_PROMPT = "{system}\n\n{instructions}"


def build_service_overview_prompt(context: str) -> str:
    """
    Build a prompt for generating comprehensive service security overviews.

    Args:
        context: Context from the service's code and documentation

    Returns:
        str: Formatted prompt for LLM
    """
    return SERVICE_OVERVIEW_PROMPT.format(
        system=SERVICE_OVERVIEW_SYSTEM,
        instructions=SERVICE_OVERVIEW_INSTRUCTIONS.format(context=context),
    )

# ---------------------------------------------------------------------------
# 1. FILE-LEVEL SECURITY / COMPLIANCE SUMMARY
# ---------------------------------------------------------------------------

FILE_SUMMARY_SYSTEM = (
    "You are a seasoned security auditor specialising in source-code reviews."
)
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
    """
    Build a prompt for generating file-level security summaries.

    Args:
        filename: Name of the file being analyzed
        file_content: Content of the file to analyze

    Returns:
        str: Formatted prompt for LLM
    """
    return FILE_SUMMARY_PROMPT.format(
        system=FILE_SUMMARY_SYSTEM,
        instructions=FILE_SUMMARY_INSTRUCTIONS,
        filename=filename,
        file_content=file_content,
    )


# ---------------------------------------------------------------------------
# 2. OSCAL CONTROL IMPLEMENTATION GENERATION
# ---------------------------------------------------------------------------

CONTROL_IMPL_SYSTEM = (
    "You are a compliance automation assistant that writes OSCAL component definitions."
)
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
    - ✅ If the control is applicable but only satisfied through configuration — explain your reasoning within the JSON control-explanation field and provide the configuration details within the JSON control-configuration field.  Do not reference .md files or other type of documentation type files. Do not make up any configuration details. If you are sure of the configuration details, provide the file path, key value, and line number of the configuration as applicable. If you are not sure of the configuration details, do not provide any configuration details and leave the control-configuration field empty.
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

Return only valid, minified JSON.
"""
)

CONTROL_IMPL_PROMPT_HEADER = (
    "{system}\n\n{instructions}\n\n"
    "Control ID requested: **{control_id}**\n\n"
    "{security_overview_section}"
    "Semantic evidence chunks (top-{k}):\n"
)

CHUNK_BULLET = "- {chunk_type} • {source} • lines {start}-{end}\n```\n{content}\n```\n"

CONTROL_IMPL_PROMPT_FOOTER = "\n---\nGenerate the JSON now:"

# ---------------------------------------------------------------------------
# 3. OSCAL CONTROL VALIDATION AND REVISION
# ---------------------------------------------------------------------------

CRITIQUE_REVISE_SYSTEM = """You are an expert in OSCAL and software-security evidence mapping.
Follow every JSON rule exactly; invalid JSON is never acceptable.
When asked to CRITIQUE, list flaws without rewriting the object.
When asked to REVISE, fix *only* the flagged flaws; keep everything else identical.
Never invent content you don't have evidence for.
Return raw, minified JSON—no markdown, no comments."""

CRITIQUE_PROMPT = """
{system}

You will receive a dictionary of an OSCAL `implemented_requirements` object.

Goal: identify any remaining structural or content issues that need fixing.

{security_overview_section}
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
2. A `violations` list produced by the Critique step.

Task: produce a **repaired** version of the array that resolves *every* violation,
without altering any other content.

{security_overview_section}
Return the full, minified JSON array—nothing else.

INPUT
"original": <<<{implemented_requirements_json}>>>
"violations": <<<{critique_violations_json}>>>

"""

# ---------------------------------------------------------------------------
# 4. OSCAL CONTROL EVALUATION
# ---------------------------------------------------------------------------

EVALUATE_SYSTEM = """
You are a senior compliance auditor reviewing automated control mappings in OSCAL format.
You evaluate based on the quality of rationale (explanation), evidence (configuration), and status alignment.
Your goal is to provide a structured assessment and recommendations to improve the mapping output.
Do not assume any content beyond what is shown.

"""

EVALUATE_PROMPT = """
{system}

Here is a single control from an OSCAL component-definition's `implemented_requirements` section.

Evaluate the following:
1. Is the `control-status` correct given the explanation and configuration?
2. Is the `control-explanation` clearly written, accurate, and grounded in the observed implementation?
3. Is the `control-configuration` (if required) specific, correct, and valid?
4. Do all parts of the control (status, explanation, configuration, and statement) reinforce each other without contradiction?

Score each of the 4 categories from 0–2 as follows:
- 0 = inaccurate or missing
- 1 = partially correct or vague
- 2 = complete, specific, and accurate

Also provide:
- A 1–2 sentence justification for each score
- A recommendation (if any) for how to improve this control mapping

Return the result in this format:


{{
  "control-id": "<from input>",
  "scores": {{
    "status_alignment": <0-2>,
    "explanation_quality": <0-2>,
    "configuration_support": <0-2>,
    "overall_consistency": <0-2>
  }},
  "total_score": <sum>,
  "justifications": {{
    "status_alignment": "...",
    "explanation_quality": "...",
    "configuration_support": "...",
    "overall_consistency": "..."
  }},
  "recommendation": "..."
}}

CONTROL TO EVALUATE:
{control_json}

"""


def build_control_prompt(
    control_id: str,
    control_name: str,
    control_description: str,
    evidence_chunks: List[dict],
    main_uuid: str,
    statement_uuid: str,
    security_overview: str = None,
) -> str:

    """
    Build a prompt for generating OSCAL control implementations.

    Args:
        control_id: The control identifier (e.g., "AC-1")
        control_name: Human-readable name of the control
        control_description: Detailed description of the control
        evidence_chunks: List of evidence chunks from code analysis
        main_uuid: UUID for the main control
        statement_uuid: UUID for the control statement
        security_overview: Optional security overview content to include as reference

    Returns:
        str: Formatted prompt for LLM
    """
    instructions = CONTROL_IMPL_INSTRUCTIONS.format(
        control_id=control_id,
        control_name=control_name,
        control_description=control_description,
        main_uuid=main_uuid,
        statement_uuid=statement_uuid,
    )

    # Format security overview section if provided
    security_overview_section = ""
    if security_overview:
        security_overview_section = (
            "## SERVICE SECURITY OVERVIEW (Reference)\n"
            "The following provides a high-level security overview of the service. "
            "Use this as context when analyzing the specific control implementation:\n\n"
            f"{security_overview}\n\n"
            "---\n\n"
        )

    header = CONTROL_IMPL_PROMPT_HEADER.format(
        system=CONTROL_IMPL_SYSTEM,
        instructions=instructions,
        control_id=control_id,
        k=len(evidence_chunks),
        security_overview_section=security_overview_section,
    )
    body = ""
    for c in evidence_chunks:
        body += CHUNK_BULLET.format(
            chunk_type=c.get("chunk_type", "unknown"),
            source=c.get("source_file", "N/A"),
            start=c.get("start_line", "?"),
            end=c.get("end_line", "?"),
            content=(c.get("content") or c.get("summary", "")).strip()[
                :800
            ],  # protect context length
        )
    return header + body + CONTROL_IMPL_PROMPT_FOOTER


def build_critique_prompt(
    implemented_requirements: List[dict], security_overview: str = None
) -> str:

    """
    Build a prompt for critiquing implemented requirements.

    Args:
        implemented_requirements: List of implemented requirement dictionaries
        security_overview: Optional security overview content to include as reference

    Returns:
        str: Formatted prompt for LLM critique
    """
    # Format security overview section if provided
    security_overview_section = ""
    if security_overview:
        security_overview_section = (
            "## SERVICE SECURITY OVERVIEW (Reference)\n"
            "The following provides a high-level security overview of the service. "
            "Use this as context when validating the control implementations:\n\n"
            f"{security_overview}\n\n"
            "---\n\n"
        )

    return CRITIQUE_PROMPT.format(
        system=CRITIQUE_REVISE_SYSTEM,
        implemented_requirements_json=json.dumps(implemented_requirements),
        security_overview_section=security_overview_section,
    )


def build_revise_prompt(
    implemented_requirements: List[dict],
    violations: List[dict],
    security_overview: str = None,
) -> str:
    """
    Build a prompt for revising implemented requirements based on violations.

    Args:
        implemented_requirements: List of implemented requirement dictionaries
        violations: List of validation violations to fix
        security_overview: Optional security overview content to include as reference

    Returns:
        str: Formatted prompt for LLM revision
    """
    # Format security overview section if provided
    security_overview_section = ""
    if security_overview:
        security_overview_section = (
            "## SERVICE SECURITY OVERVIEW (Reference)\n"
            "The following provides a high-level security overview of the service. "
            "Use this as context when fixing the control implementations:\n\n"
            f"{security_overview}\n\n"
            "---\n\n"
        )
    return REVISE_PROMPT.format(
        system=CRITIQUE_REVISE_SYSTEM,
        implemented_requirements_json=json.dumps(implemented_requirements),
        critique_violations_json=json.dumps(violations),
        security_overview_section=security_overview_section,
    )


def build_evaluate_prompt(requirement: dict) -> str:
    """
    Build a prompt for evaluating a single implemented requirement.

    Args:
        requirement: Single implemented requirement dictionary

    Returns:
        str: Formatted prompt for LLM evaluation
    """
    return EVALUATE_PROMPT.format(
        system=EVALUATE_SYSTEM, control_json=json.dumps(requirement, indent=2)
    )
