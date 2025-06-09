# maposcal/embeddings/faiss_index.py
"""
FAISS (Facebook AI Similarity Search) index management utilities.
This module provides functions for creating, saving, loading, and searching FAISS indices
for efficient similarity search of vector embeddings.
"""

import faiss
import numpy as np
from pathlib import Path

def build_faiss_index(vectors: np.ndarray) -> faiss.IndexFlatL2:
    """
    Build a FAISS index from a set of vectors.
    
    Args:
        vectors: numpy array of shape (n_vectors, vector_dim) containing the vectors to index
        
    Returns:
        A FAISS index containing the input vectors
    """
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)  # Exact search
    index.add(vectors)
    return index

def save_index(index: faiss.IndexFlatL2, path: Path):
    """
    Save a FAISS index to disk.
    
    Args:
        index: The FAISS index to save
        path: Path where the index should be saved
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(path))

def load_index(path: Path) -> faiss.IndexFlatL2:
    """
    Load a FAISS index from disk.
    
    Args:
        path: Path to the saved index file
        
    Returns:
        The loaded FAISS index
    """
    return faiss.read_index(str(path))

def search_index(index: faiss.IndexFlatL2, query: np.ndarray, k: int = 5):
    """
    Search the index for the k nearest neighbors of the query vector.
    
    Args:
        index: The FAISS index to search
        query: Query vector of shape (1, vector_dim)
        k: Number of nearest neighbors to return (default: 5)
        
    Returns:
        Tuple of (indices, distances) for the k nearest neighbors
    """
    D, I = index.search(query, k)
    return I[0], D[0]  # Return top-k indices and distances
