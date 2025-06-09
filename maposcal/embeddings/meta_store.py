# maposcal/embeddings/meta_store.py
"""
Metadata storage utilities for managing chunk metadata.
This module provides functions for saving, loading, and retrieving metadata
associated with text chunks in the embedding system.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

def save_metadata(metadata: List[Dict[str, Any]], path: Path):
    """
    Save chunk metadata to a JSON file.
    
    Args:
        metadata: List of dictionaries containing metadata for each chunk
        path: Path where the metadata should be saved
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

def load_metadata(path: Path) -> List[Dict[str, Any]]:
    """
    Load chunk metadata from a JSON file.
    
    Args:
        path: Path to the metadata file
        
    Returns:
        List of dictionaries containing the loaded metadata
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_chunk_by_index(meta: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
    """
    Retrieve metadata for a specific chunk by its index.
    
    Args:
        meta: List of metadata dictionaries
        index: Index of the chunk to retrieve
        
    Returns:
        Dictionary containing the metadata for the specified chunk
    """
    return meta[index]
