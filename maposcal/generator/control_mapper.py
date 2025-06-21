from typing import List, Dict
from maposcal.llm import prompt_templates
from maposcal.llm.llm_handler import LLMHandler
import re
import json
from pathlib import Path
from maposcal.embeddings import faiss_index, meta_store, local_embedder
import logging
from .validation import validate_control_mapping, validate_unique_uuids
import uuid

logger = logging.getLogger()

def get_relevant_chunks(control_description: str, output_dir: str, top_k: int = 5, service_prefix: str = None) -> List[Dict]:
    """
    Query both index.faiss and summary_index.faiss using the control_description as the query.
    Combine and deduplicate the results to return relevant chunks.
    
    Args:
        control_description (str): The control description to use as the query.
        output_dir (str): The directory containing the FAISS indices and metadata.
        top_k (int): Number of top chunks to retrieve from each index.
        service_prefix (str): Prefix for the FAISS and metadata files.
        
    Returns:
        List[Dict]: A list of relevant chunks.
    """
    logger.info(f"Querying relevant chunks for control description: {control_description}")
    # Embed the control description for querying
    query_embedding = local_embedder.embed_one(control_description)

    # Query index.faiss (chunk-level)
    index_path = Path(output_dir) / f"{service_prefix}_index.faiss"
    meta_path = Path(output_dir) / f"{service_prefix}_meta.json"
    if not index_path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"Could not find {index_path} or {meta_path}. Please run analyze first.")
    index = faiss_index.load_index(index_path)
    meta = meta_store.load_metadata(meta_path)
    chunk_indices, _ = faiss_index.search_index(index, query_embedding, k=top_k)
    chunk_results = [meta_store.get_chunk_by_index(meta, idx) for idx in chunk_indices if idx < len(meta)]

    # Query summary_index.faiss (file-level summaries)
    summary_index_path = Path(output_dir) / f"{service_prefix}_summary_index.faiss"
    summary_meta_path = Path(output_dir) / f"{service_prefix}_summary_meta.json"
    summary_results = []
    if summary_index_path.exists() and summary_meta_path.exists():
        summary_index = faiss_index.load_index(summary_index_path)
        summary_meta = meta_store.load_metadata(summary_meta_path)
        summary_indices, _ = faiss_index.search_index(summary_index, query_embedding, k=top_k)
        for idx in summary_indices:
            if str(idx) in summary_meta:
                summary_results.append(summary_meta[str(idx)])
            else:
                # Try to get by file path if available
                for k, v in summary_meta.items():
                    if v.get("vector_id") == idx:
                        summary_results.append(v)
                        break

    # Combine and deduplicate relevant chunks
    relevant_chunks = chunk_results + summary_results
    # Optionally deduplicate by file path or content
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

def map_control(control_dict: dict, output_dir: str, top_k: int = 5, service_prefix: str = None) -> str:
    """
    Maps chunks to an OSCAL control using LLM summarization.

    Args:
        control_dict (dict): Dictionary containing control information with keys:
            - id: The OSCAL control ID (e.g. AC-6)
            - title: The OSCAL control name
            - statement: The OSCAL control statement/description
            - params: Optional parameters for the control
        output_dir (str): The directory containing the FAISS indices and metadata.
        top_k (int): Number of top chunks to use.
        service_prefix (str): Prefix for the FAISS and metadata files.

    Returns:
        str: The LLM response for the control mapping prompt.
    """
    logger.info(f"Mapping control: {control_dict['id']} - {control_dict['title']}")
    llm_handler = LLMHandler()
    
    # Load security overview if available
    security_overview = None
    if service_prefix:
        security_overview_path = Path(output_dir) / f"{service_prefix}_security_overview.md"
        if security_overview_path.exists():
            try:
                with open(security_overview_path, 'r') as f:
                    security_overview = f.read().strip()
                logger.info(f"Loaded security overview from {security_overview_path}")
            except Exception as e:
                logger.warning(f"Failed to load security overview: {e}")
    
    # Get the control statement and handle ODP substitution
    control_description = control_dict['statement'][0] if isinstance(control_dict['statement'], list) else control_dict['statement']
    
    # Handle ODP parameter substitution and collect prose
    additional_prose = []
    if 'params' in control_dict:
        for param in control_dict['params']:
            param_id = param['id']
            # Look for the parameter placeholder in the statement
            placeholder = f"{{{{ insert: param, {param_id} }}}}"
            if placeholder in control_description:
                # Replace with resolved values if available
                if param.get('resolved-values'):
                    resolved_value = param['resolved-values'][0]  # Take the first resolved value
                    control_description = control_description.replace(placeholder, resolved_value)
                # If no resolved values, use the prose
                elif param.get('prose'):
                    prose_value = param['prose'][0]  # Take the first prose value
                    control_description = control_description.replace(placeholder, prose_value)
            
            # Collect prose for additional context
            if param.get('prose'):
                additional_prose.extend(param['prose'])
    
    # Append additional prose if available
    if additional_prose:
        control_description += "\n\nAdditional requirements:\n" + "\n".join(f"- {prose}" for prose in additional_prose)
    
    relevant_chunks = get_relevant_chunks(control_description, output_dir, top_k, service_prefix)

    # Try up to 3 times to get a valid response
    max_retries = 3
    for attempt in range(max_retries):
        # Generate new UUIDs for each attempt
        main_uuid = str(uuid.uuid4())
        statement_uuid = str(uuid.uuid4())
        
        prompt = prompt_templates.build_control_prompt(
            control_dict['id'],
            control_dict['title'],
            control_description,
            relevant_chunks,
            top_k,
            main_uuid,
            statement_uuid,
            security_overview
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
            logger.error(f"Failed to generate valid control mapping after {max_retries} attempts. Last error: {error_msg}")
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
        cleaned = re.sub(r"^```json|```$", "", cleaned, flags=re.MULTILINE).strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return {"llm_raw_response": result}
