# maposcal/embeddings/local_embedder.py
"""
Local embedding utilities using sentence-transformers.
This module provides functions for loading and using local embedding models
to convert text into vector representations.
"""
from maposcal import settings
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger()

# Global model instance and name
_model = None
_model_name = settings.local_embeddings_model  # or "thenlper/gte-small", etc.


def load_model(model_name: str = None):
    """
    Load or initialize the sentence transformer model.
    If the model is not cached, it will be downloaded and cached.

    Args:
        model_name: Optional name of the model to load. If None, uses the default model.

    Returns:
        The loaded SentenceTransformer model
    """
    global _model, _model_name
    if model_name:
        _model_name = model_name
    if _model is None:
        logger.info(f"Loading local embedding model: {_model_name}")
        _model = SentenceTransformer(
            _model_name,
            cache_folder=os.path.expanduser("~/.cache/torch/sentence_transformers/"),
        )
    return _model


def embed_chunks(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text chunks.

    Args:
        texts: List of text chunks to embed

    Returns:
        numpy array of embeddings
    """
    if not texts:
        logger.error("No texts provided for embedding")
        raise ValueError("Cannot embed empty list of texts")

    logger.debug(f"Embedding {len(texts)} chunks")
    model = load_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    logger.debug(f"Generated embeddings of shape: {embeddings.shape}")
    return embeddings


def embed_one(text: str) -> np.ndarray:
    """
    Generate embedding for a single text.

    Args:
        text: Text to embed

    Returns:
        numpy array containing the embedding
    """
    if not text:
        logger.error("Empty text provided for embedding")
        raise ValueError("Cannot embed empty text")

    logger.debug("Embedding single text")
    model = load_model()
    embedding = model.encode([text])[0]
    logger.debug(f"Generated embedding of shape: {embedding.shape}")
    return embedding


def get_model_name() -> str:
    """
    Get the name of the currently loaded model.

    Returns:
        Name of the current embedding model
    """
    return _model_name
