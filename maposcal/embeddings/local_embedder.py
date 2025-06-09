# maposcal/embeddings/local_embedder.py
"""
Local embedding utilities using sentence-transformers.
This module provides functions for loading and using local embedding models
to convert text into vector representations.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

# Global model instance and name
_model = None
_model_name = "all-MiniLM-L6-v2"  # or "thenlper/gte-small", etc.

def load_model(model_name: str = None):
    """
    Load or initialize the sentence transformer model.
    
    Args:
        model_name: Optional name of the model to load. If None, uses the default model.
        
    Returns:
        The loaded SentenceTransformer model
    """
    global _model, _model_name
    if model_name:
        _model_name = model_name
    if _model is None:
        print(f"Loading local embedding model: {_model_name}")
        _model = SentenceTransformer(_model_name)
    return _model

def embed_chunks(chunks: List[str]) -> np.ndarray:
    """
    Convert a list of text chunks into embeddings.
    
    Args:
        chunks: List of text strings to embed
        
    Returns:
        numpy array of shape (n_chunks, embedding_dim) containing the embeddings
    """
    model = load_model()
    embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
    return embeddings.astype("float32")

def embed_one(text: str) -> np.ndarray:
    """
    Convert a single text string into an embedding.
    
    Args:
        text: Text string to embed
        
    Returns:
        numpy array of shape (1, embedding_dim) containing the embedding
    """
    model = load_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.astype("float32").reshape(1, -1)

def get_model_name() -> str:
    """
    Get the name of the currently loaded model.
    
    Returns:
        Name of the current embedding model
    """
    return _model_name
