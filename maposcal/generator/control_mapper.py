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

Functions:
- get_relevant_chunks: Retrieve semantically relevant code chunks for control mapping
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
    meta = meta_store.load_metadata(meta_path)
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
        summary_meta = meta_store.load_metadata(summary_meta_path)
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
            summary_meta = meta_store.load_metadata(summary_meta_path)
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


def map_control(control_dict: dict, output_dir: str, top_k: int = 5) -> str:
    """
    Maps chunks to an OSCAL control using LLM summarization with security context.

    This function generates OSCAL implemented requirements for a specific security control
    by combining semantic evidence retrieval with LLM-based analysis. It includes
    security overview integration for improved control mapping accuracy and context
    understanding.

    Args:
        control_dict (dict): Dictionary containing control information with keys:
            - id: The OSCAL control ID (e.g. AC-6)
            - title: The OSCAL control name
            - statement: The OSCAL control statement/description
            - params: Optional parameters for the control
        output_dir (str): The directory containing the FAISS indices and metadata.
        top_k (int): Number of top chunks to use.

    Returns:
        str: The LLM response for the control mapping prompt.

    Features:
        - Security overview integration for better context understanding
        - Semantic evidence retrieval from both code chunks and file summaries
        - LLM-based control status determination and explanation generation
        - Comprehensive validation and retry logic for improved accuracy
    """
    logger.info(f"Mapping control: {control_dict['id']} - {control_dict['title']}")
    llm_handler = LLMHandler()

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
                    resolved_value = param["resolved-values"][
                        0
                    ]  # Take the first resolved value
                    control_description = control_description.replace(
                        placeholder, resolved_value
                    )
                # If no resolved values, use the prose
                elif param.get("prose"):
                    prose_value = param["prose"][0]  # Take the first prose value
                    control_description = control_description.replace(
                        placeholder, prose_value
                    )

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

    # Try up to 3 times to get a valid response
    max_retries = 3
    for attempt in range(max_retries):
        # Generate new UUIDs for each attempt
        main_uuid = str(uuid.uuid4())
        statement_uuid = str(uuid.uuid4())

        prompt = prompt_templates.build_control_prompt(
            control_dict["id"],
            control_dict["title"],
            control_description,
            relevant_chunks,
            main_uuid,
            statement_uuid,
            security_overview,
        )
        response = llm_handler.query(prompt=prompt)

        # Parse and validate the response
        parsed = parse_llm_response(response)
        if isinstance(parsed, dict):
            is_valid, error_msg = validate_control_mapping(parsed)
            if is_valid:
                return response

            # If validation failed and we have retries left, try again with error feedback
            if attempt < max_retries - 1:
                error_prompt = f"Here is the validation error—fix it: {error_msg}\n\nPlease regenerate the control mapping with the following requirements:\n"
                error_prompt += "- Ensure all required properties are present\n"
                error_prompt += "- Use only .json, .yaml, or .yml file extensions in control-configuration\n"
                error_prompt += "- Use valid UUID format for all UUIDs\n"
                error_prompt += "- Ensure no duplicate UUIDs are used\n\n"
                error_prompt += "Original prompt:\n" + prompt

                response = llm_handler.query(prompt=error_prompt)
                continue

            # If we're out of retries, log the error and return the last response
            logger.error(
                f"Failed to generate valid control mapping after {max_retries} attempts. Last error: {error_msg}"
            )
            return response

    return response


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
