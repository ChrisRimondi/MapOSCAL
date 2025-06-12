from typing import List, Dict
from maposcal.llm import prompt_templates
from maposcal.llm.llm_handler import LLMHandler

def map_control(control_id: str, control_name: str, control_description: str, chunks: List[Dict], top_k: int = 20) -> str:
    """
    Maps chunks to an OSCAL control using LLM summarization.

    Args:
        control_id (str): The OSCAL control ID (e.g. AC-6).
        control_name (str): The OSCAL control name.
        control_description (str): The OSCAL control description.
        chunks (List[Dict]): All indexed and annotated chunks from analysis.
        top_k (int): Number of top chunks to use.

    Returns:
        str: The LLM response for the control mapping prompt.
    """
    # TODO: Replace this with vector ranking logic
    relevant_chunks = chunks[:top_k]

    llm_handler = LLMHandler()

    prompt = prompt_templates.build_control_prompt(control_id, control_name, control_description, relevant_chunks, top_k)
    response, _ = llm_handler.query(prompt=prompt)

    return response
