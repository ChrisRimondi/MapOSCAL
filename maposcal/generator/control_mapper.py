from typing import List, Dict
from maposcal.llm import prompt_templates
from maposcal.llm.llm_handler import LLMHandler
import re
import json
from pathlib import Path
from maposcal.embeddings import faiss_index, meta_store, local_embedder
import logging

logger = logging.getLogger(__name__)

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

def map_control(control_id: str, control_name: str, control_description: str, output_dir: str, top_k: int = 5, service_prefix: str = None) -> str:
    """
    Maps chunks to an OSCAL control using LLM summarization.

    Args:
        control_id (str): The OSCAL control ID (e.g. AC-6).
        control_name (str): The OSCAL control name.
        control_description (str): The OSCAL control description.
        output_dir (str): The directory containing the FAISS indices and metadata.
        top_k (int): Number of top chunks to use.
        service_prefix (str): Prefix for the FAISS and metadata files.

    Returns:
        str: The LLM response for the control mapping prompt.
    """
    logger.info(f"Mapping control: {control_id} - {control_name}")
    llm_handler = LLMHandler()
    
    # Get relevant chunks
    relevant_chunks = get_relevant_chunks(control_description, output_dir, top_k, service_prefix)

    prompt = prompt_templates.build_control_prompt(control_id, control_name, control_description, relevant_chunks, top_k)
    response = llm_handler.query(prompt=prompt)
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
        print(f"Failed to parse LLM response as JSON: {e}")
        return {"llm_raw_response": result}
