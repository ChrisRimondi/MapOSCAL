"""
Metadata utilities for MapOSCAL.

This module provides functions to generate and inject metadata into output files,
tracking model information, timing, and generation context.
"""

import json
import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def generate_metadata(
    model: str,
    provider: str,
    base_url: str,
    command: str,
    config_file: str = None,
    version: str = "1.0.0"
) -> Dict[str, Any]:
    """
    Generate metadata for file outputs.
    
    Args:
        model: The LLM model used
        provider: The LLM provider (openai, gemini, etc.)
        base_url: The base URL for the provider
        command: The CLI command being executed
        config_file: Path to the configuration file used
        version: MapOSCAL version
        
    Returns:
        dict: Metadata dictionary
    """
    return {
        "generation_info": {
            "model": model,
            "provider": provider,
            "base_url": base_url,
            "start_time": datetime.datetime.now().isoformat(),
            "command": command,
            "config_file": config_file,
            "version": version
        }
    }


def inject_metadata_into_json(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject metadata into a JSON data structure.
    
    Args:
        data: The original JSON data
        metadata: The metadata to inject
        
    Returns:
        dict: JSON data with metadata injected
    """
    # Create a copy to avoid modifying the original
    result = data.copy()
    
    # Inject metadata at the top level
    result["_metadata"] = metadata
    
    return result


def inject_metadata_into_markdown(content: str, metadata: Dict[str, Any]) -> str:
    """
    Inject metadata into markdown content as HTML comment.
    
    Args:
        content: The original markdown content
        metadata: The metadata to inject
        
    Returns:
        str: Markdown content with metadata comment
    """
    # Convert metadata to YAML-like format for readability
    metadata_yaml = "\n".join([
        f"  {key}: {value}" 
        for key, value in metadata["generation_info"].items()
    ])
    
    metadata_comment = f"""<!--
metadata:
{metadata_yaml}
-->

"""
    
    return metadata_comment + content


def extract_metadata_from_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a JSON data structure.
    
    Args:
        data: JSON data that may contain metadata
        
    Returns:
        dict: Extracted metadata or empty dict if not found
    """
    return data.get("_metadata", {})


def extract_metadata_from_markdown(content: str) -> Dict[str, Any]:
    """
    Extract metadata from markdown content.
    
    Args:
        content: Markdown content that may contain metadata comment
        
    Returns:
        dict: Extracted metadata or empty dict if not found
    """
    try:
        # Look for metadata comment at the beginning
        if content.startswith("<!--\nmetadata:"):
            # Find the end of the comment
            end_comment = content.find("-->\n")
            if end_comment != -1:
                metadata_section = content[4:end_comment].strip()
                
                # Parse the YAML-like metadata
                metadata = {}
                for line in metadata_section.split("\n"):
                    if line.strip() and ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                
                return {"generation_info": metadata}
    except Exception as e:
        logger.warning(f"Failed to extract metadata from markdown: {e}")
    
    return {} 