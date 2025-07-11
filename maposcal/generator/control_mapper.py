"""
maposcal.generator.control_mapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OSCAL control mapping functionality for MapOSCAL.

This module provides functions for mapping security controls to OSCAL implemented requirements
using semantic search and LLM-based analysis. It includes security overview integration
for improved control mapping accuracy.

Key Features:
- Semantic evidence retrieval using FAISS indices
- Security overview integration for better context understanding
- LLM-based control status determination and explanation generation
- Comprehensive validation and retry logic
- Simplified file naming without service prefixes
- Template-based generation for structural integrity

Functions:
- get_relevant_chunks: Retrieve semantically relevant code chunks for control mapping
- create_control_template: Create OSCAL template with all required structural elements
- merge_llm_content: Merge LLM-generated content into OSCAL template
- map_control: Generate OSCAL implemented requirements for a specific control
- parse_llm_response: Parse and clean LLM responses as JSON
"""

from typing import List, Dict
from maposcal.llm import prompt_templates
from maposcal.llm.llm_handler import LLMHandler
import re
import json
from pathlib import Path
from maposcal.embeddings import faiss_index, meta_store, local_embedder
import logging
from .validation import validate_control_mapping
import uuid

logger = logging.getLogger()


def create_control_template(control_id: str, control_name: str, control_description: str, main_uuid: str, statement_uuid: str) -> dict:
    """
    Create a complete OSCAL template with all required structural elements.
    
    This function creates a template that ensures all required OSCAL fields are present
    with correct UUIDs and control-ids, reducing the burden on the LLM to generate
    complex JSON structures.
    
    Args:
        control_id: The OSCAL control ID (e.g., "AC-1")
        control_name: Human-readable name of the control
        control_description: The control description/statement
        main_uuid: UUID for the main control
        statement_uuid: UUID for the control statement
        
    Returns:
        dict: Complete OSCAL template with all required structural elements
    """
    return {
        "uuid": main_uuid,
        "control-id": control_id,
        "props": [
            {
                "name": "control-status",
                "value": "applicable and not satisfied",  # Default fallback
                "ns": "urn:maposcal:control-status-reference"
            },
            {
                "name": "control-name", 
                "value": control_name,
                "ns": "urn:maposcal:control-name-reference"
            },
            {
                "name": "control-description",
                "value": control_description,
                "ns": "urn:maposcal:control-description-reference"
            },
            {
                "name": "control-explanation",
                "value": "",  # LLM fills this
                "ns": "urn:maposcal:explanation-reference"
            },
            {
                "name": "control-configuration",
                "value": [],  # LLM fills this
                "ns": "urn:maposcal:configuration-reference"
            }
        ],
        "annotations": [
            {
                "name": "source-code-reference",
                "value": [],  # Will be populated based on evidence
                "ns": "urn:maposcal:source-code-reference"
            }
        ],
        "statements": [
            {
                "statement-id": f"{control_id}_smt.a",
                "uuid": statement_uuid,
                "description": ""  # LLM fills this
            }
        ]
    }


def merge_llm_content(template: dict, llm_content: dict, relevant_chunks: List[dict]) -> dict:
    """
    Merge LLM-generated content into the OSCAL template.
    
    This function takes the LLM-generated content and merges it into the structural
    template, ensuring all required fields are present and properly formatted.
    
    Args:
        template: The OSCAL template with structural elements
        llm_content: LLM-generated content dictionary
        relevant_chunks: List of evidence chunks for source code references
        
    Returns:
        dict: Complete OSCAL control mapping with merged content
    """
    result = template.copy()
    
    # Update control-status
    for prop in result["props"]:
        if prop["name"] == "control-status":
            prop["value"] = llm_content.get("control-status", "applicable and not satisfied")
        elif prop["name"] == "control-explanation":
            prop["value"] = llm_content.get("control-explanation", "")
        elif prop["name"] == "control-configuration":
            prop["value"] = llm_content.get("control-configuration", [])
    
    # Update statement description
    if result.get("statements"):
        result["statements"][0]["description"] = llm_content.get("statement-description", "")
    
    # Update source code references based on evidence chunks
    source_files = set()
    for chunk in relevant_chunks:
        if "source_file" in chunk:
            source_files.add(chunk["source_file"])
    
    for annotation in result["annotations"]:
        if annotation["name"] == "source-code-reference":
            annotation["value"] = list(source_files)
    
    return result


def validate_content_quality(llm_content: dict) -> tuple[bool, List[str]]:
    """
    Validate the quality of LLM-generated content.
    
    This function performs content-specific validation to ensure the LLM
    has provided meaningful content for required fields.
    
    Args:
        llm_content: LLM-generated content dictionary
        
    Returns:
        tuple: (is_valid, list_of_issues) where is_valid is boolean
               and list_of_issues contains specific content problems
    """
    issues = []
    
    # Check control-status
    control_status = llm_content.get("control-status", "")
    if not control_status:
        issues.append("Missing control-status")
    elif control_status not in [
        "applicable and inherently satisfied",
        "applicable but only satisfied through configuration", 
        "applicable but partially satisfied",
        "applicable and not satisfied",
        "not applicable"
    ]:
        issues.append(f"Invalid control-status: {control_status}")
    
    # Check control-explanation
    control_explanation = llm_content.get("control-explanation", "")
    if not control_explanation or len(control_explanation.strip()) < 10:
        issues.append("Control explanation is too short or missing")
    
    # Check statement description
    statement_description = llm_content.get("statement-description", "")
    if not statement_description or len(statement_description.strip()) < 10:
        issues.append("Statement description is too short or missing")
    
    # Check configuration consistency
    control_configuration = llm_content.get("control-configuration", [])
    if "configuration" in control_status.lower() and not control_configuration:
        issues.append("Control status indicates configuration but no configuration provided")
    
    return len(issues) == 0, issues


def get_relevant_chunks(
    control_description: str, output_dir: str, top_k: int = 5, control_id: str = None
) -> List[Dict]:
    """
    Query both index.faiss and summary_index.faiss using the control_description as the query.
    Combine and deduplicate the results to return relevant chunks.

    Additionally, if control_id is provided, include all chunks and summaries from files
    that have matching control hints for that specific control.

    This function performs semantic search across both code chunks and file summaries
    to find the most relevant evidence for control mapping. It uses FAISS indices
    for efficient similarity search and combines results from both chunk-level and
    summary-level analysis. When a control_id is provided, it also includes all
    evidence from files that have been tagged with matching control hints.

    Args:
        control_description (str): The control description to use as the query.
        output_dir (str): The directory containing the FAISS indices and metadata.
        top_k (int): Number of top chunks to retrieve from each index.
        control_id (str, optional): The NIST 800-53 control ID (e.g., "AC-4", "SC-5")
                                   to filter by control hints. If provided, includes
                                   all chunks from files with matching control hints.

    Returns:
        List[Dict]: A list of relevant chunks with source file information and content.

    Raises:
        FileNotFoundError: If required FAISS indices or metadata files are missing.
    """
    logger.info(
        f"Querying relevant chunks for control description: {control_description}"
    )
    if control_id:
        logger.info(f"Also filtering by control hints for control: {control_id}")

    # Embed the control description for querying
    query_embedding = local_embedder.embed_one(control_description)

    # Query index.faiss (chunk-level)
    index_path = Path(output_dir) / "index.faiss"
    meta_path = Path(output_dir) / "meta.json"
    if not index_path.exists() or not meta_path.exists():
        raise FileNotFoundError(
            f"Could not find {index_path} or {meta_path}. Please run analyze first."
        )
    index = faiss_index.load_index(index_path)
    meta_data = meta_store.load_metadata(meta_path)
    
    # Handle new metadata structure (with _metadata) or old structure (direct list)
    if isinstance(meta_data, dict) and "chunks" in meta_data:
        meta = meta_data["chunks"]
    else:
        meta = meta_data
    
    chunk_indices, _ = faiss_index.search_index(index, query_embedding, k=top_k)
    chunk_results = [
        meta_store.get_chunk_by_index(meta, idx)
        for idx in chunk_indices
        if idx < len(meta)
    ]

    # Query summary_index.faiss (file-level summaries)
    summary_index_path = Path(output_dir) / "summary_index.faiss"
    summary_meta_path = Path(output_dir) / "summary_meta.json"
    summary_results = []
    if summary_index_path.exists() and summary_meta_path.exists():
        summary_index = faiss_index.load_index(summary_index_path)
        summary_meta_data = meta_store.load_metadata(summary_meta_path)
        
        # Handle new metadata structure (with _metadata) or old structure (direct dict)
        if isinstance(summary_meta_data, dict) and "_metadata" in summary_meta_data:
            summary_meta = {k: v for k, v in summary_meta_data.items() if k != "_metadata"}
        else:
            summary_meta = summary_meta_data
            
        summary_indices, _ = faiss_index.search_index(
            summary_index, query_embedding, k=top_k
        )
        for idx in summary_indices:
            if str(idx) in summary_meta:
                summary_results.append(summary_meta[str(idx)])
            else:
                # Try to get by file path if available
                for k, v in summary_meta.items():
                    if v.get("vector_id") == idx:
                        summary_results.append(v)
                        break

    # Combine semantic search results
    relevant_chunks = chunk_results + summary_results

    # If control_id is provided, add chunks from files with matching control hints
    if control_id:
        # Convert control_id to control hints format (remove hyphens and convert to lowercase)
        control_hint = control_id.replace("-", "").lower()
        logger.info(f"Looking for control hint: {control_hint}")

        # Get all chunks from files with matching control hints
        control_hint_chunks = []

        # Check summary metadata for control hints
        if summary_meta_path.exists():
            summary_meta_data = meta_store.load_metadata(summary_meta_path)
            
            # Handle new metadata structure (with _metadata) or old structure (direct dict)
            if isinstance(summary_meta_data, dict) and "_metadata" in summary_meta_data:
                summary_meta = {k: v for k, v in summary_meta_data.items() if k != "_metadata"}
            else:
                summary_meta = summary_meta_data
                
            for file_path, summary_data in summary_meta.items():
                # Check if this is a file path entry (not a vector_id)
                # Since we now use relative paths, we check if it's not a numeric string
                if isinstance(file_path, str) and not file_path.isdigit():
                    # This is a file path entry
                    inspector_results = summary_data.get("inspector_results", {})
                    control_hints = inspector_results.get("control_hints", [])

                    if control_hint in control_hints:
                        logger.info(f"Found matching control hint in file: {file_path}")
                        # Add the summary
                        control_hint_chunks.append(summary_data)

                        # Add all chunks from this file
                        for chunk in meta:
                            if chunk.get("source_file") == file_path:
                                control_hint_chunks.append(chunk)

        # Add control hint chunks to results
        relevant_chunks.extend(control_hint_chunks)
        logger.info(
            f"Added {len(control_hint_chunks)} chunks from files with control hint {control_hint}"
        )

    # Deduplicate relevant chunks
    seen = set()
    unique_relevant_chunks = []
    for c in relevant_chunks:
        key = c.get("source_file") if "source_file" in c else c.get("summary")
        if key and key not in seen:
            unique_relevant_chunks.append(c)
            seen.add(key)

    # Debug log to print the chunks returned
    for chunk in unique_relevant_chunks:
        logger.debug(f"Relevant chunk: {chunk}")

    return unique_relevant_chunks


def map_control(control_dict: dict, output_dir: str, top_k: int = 5, llm_config: dict = None) -> dict:
    """
    Maps chunks to an OSCAL control using template-based generation with LLM content injection.

    This function generates OSCAL implemented requirements for a specific security control
    using a hybrid approach: structural elements are handled in code while the LLM focuses
    on content generation. This ensures structural integrity while leveraging LLM capabilities
    for meaningful content analysis.

    Args:
        control_dict (dict): Dictionary containing control information with keys:
            - id: The OSCAL control ID (e.g. AC-6)
            - title: The OSCAL control name
            - statement: The OSCAL control statement/description
            - params: Optional parameters for the control
        output_dir (str): The directory containing the FAISS indices and metadata.
        top_k (int): Number of top chunks to use.
        llm_config (dict, optional): LLM configuration parameters.

    Returns:
        dict: The complete OSCAL control mapping with all required structural elements.

    Features:
        - Template-based generation for structural integrity
        - Security overview integration for better context understanding
        - Semantic evidence retrieval from both code chunks and file summaries
        - LLM-based content generation with content quality validation
        - Comprehensive retry logic for content-specific issues
    """
    logger.info(f"Mapping control: {control_dict['id']} - {control_dict['title']}")
    
    # Use provided LLM config or fall back to defaults
    if llm_config:
        llm_handler = LLMHandler(provider=llm_config["provider"], model=llm_config["model"])
    else:
        llm_handler = LLMHandler(command="generate")

    # Load security overview if available
    security_overview = None
    security_overview_path = Path(output_dir) / "security_overview.md"
    if security_overview_path.exists():
        try:
            with open(security_overview_path, "r") as f:
                security_overview = f.read().strip()
            logger.info(f"Loaded security overview from {security_overview_path}")
        except Exception as e:
            logger.warning(f"Failed to load security overview: {e}")

    # Get the control statement and handle ODP substitution
    control_description = (
        control_dict["statement"][0]
        if isinstance(control_dict["statement"], list)
        else control_dict["statement"]
    )

    # Handle ODP parameter substitution and collect prose
    additional_prose = []
    if "params" in control_dict:
        for param in control_dict["params"]:
            param_id = param["id"]
            # Look for the parameter placeholder in the statement
            placeholder = f"{{{{ insert: param, {param_id} }}}}"
            if placeholder in control_description:
                # Replace with resolved values if available
                if param.get("resolved-values"):
                    resolved_value = param["resolved-values"][0]  # Take the first resolved value
                    control_description = control_description.replace(placeholder, resolved_value)
                # If no resolved values, use the prose
                elif param.get("prose"):
                    prose_value = param["prose"][0]  # Take the first prose value
                    control_description = control_description.replace(placeholder, prose_value)

            # Collect prose for additional context
            if param.get("prose"):
                additional_prose.extend(param["prose"])

    # Append additional prose if available
    if additional_prose:
        control_description += "\n\nAdditional requirements:\n" + "\n".join(
            f"- {prose}" for prose in additional_prose
        )

    relevant_chunks = get_relevant_chunks(
        control_description, output_dir, top_k, control_dict["id"]
    )

    # Create template with all required structural elements
    main_uuid = str(uuid.uuid4())
    statement_uuid = str(uuid.uuid4())
    template = create_control_template(
        control_dict["id"],
        control_dict["title"], 
        control_description,
        main_uuid,
        statement_uuid
    )

    # Try up to 3 times to get valid content
    max_retries = 3
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1} for control {control_dict['id']}")
        
        # Generate content with simplified prompt
        content_prompt = prompt_templates.build_content_generation_prompt(
            control_dict["id"],
            control_dict["title"],
            control_description,
            relevant_chunks,
            security_overview
        )
        
        response = llm_handler.query(prompt=content_prompt)
        llm_content = parse_llm_response(response)
        
        # Validate content quality
        if isinstance(llm_content, dict):
            content_valid, content_issues = validate_content_quality(llm_content)
            
            if content_valid:
                # Merge content into template
                result = merge_llm_content(template, llm_content, relevant_chunks)
                
                # Final validation of the complete structure
                is_valid, error_msg = validate_control_mapping(result)
                if is_valid:
                    logger.info(f"Successfully generated control mapping for {control_dict['id']}")
                    return result
                else:
                    logger.warning(f"Structural validation failed for {control_dict['id']}: {error_msg}")
                    # This shouldn't happen with template-based approach, but log it
                    content_issues.append(f"Structural validation error: {error_msg}")
            
            # If content validation failed and we have retries left, try again with error feedback
            if attempt < max_retries - 1 and not content_valid:
                error_prompt = f"Content validation failed. Please fix the following issues:\n"
                error_prompt += "\n".join(f"- {issue}" for issue in content_issues)
                error_prompt += "\n\nPlease regenerate the content with the following requirements:\n"
                error_prompt += "- Provide a valid control-status from the allowed values\n"
                error_prompt += "- Write detailed explanations (at least 10 characters)\n"
                error_prompt += "- Include configuration details if status contains 'configuration'\n"
                error_prompt += "- Provide meaningful statement descriptions\n\n"
                error_prompt += "Original prompt:\n" + content_prompt
                
                response = llm_handler.query(prompt=error_prompt)
                continue
        
        # If we're out of retries, log the error and return the template with default content
        logger.error(
            f"Failed to generate valid content for control {control_dict['id']} after {max_retries} attempts. "
            f"Last content issues: {content_issues if 'content_issues' in locals() else 'Unknown'}"
        )
        
        # Return template with default content as fallback
        return template

    # This should never be reached, but return template as final fallback
    return template


def parse_llm_response(result: str) -> dict:
    """
    Clean and parse the LLM response as JSON.

    Args:
        result (str): The raw LLM response string.

    Returns:
        dict: The parsed JSON object. If parsing fails, returns a dict with the raw response.
    """
    logger.info("Parsing LLM response")
    try:
        cleaned = result.strip()

        # Try to extract JSON from markdown code blocks first
        json_block_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", cleaned, re.DOTALL)
        if json_block_match:
            json_content = json_block_match.group(1).strip()
            return json.loads(json_content)

        # Try to find JSON object in the text (look for { ... })
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", cleaned, re.DOTALL)
        if json_match:
            json_content = json_match.group(0)
            return json.loads(json_content)

        # If no JSON found, try to parse the entire cleaned string
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return {"llm_raw_response": result}
