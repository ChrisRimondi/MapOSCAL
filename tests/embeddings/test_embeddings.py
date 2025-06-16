"""Tests for the FAISS index functionality."""
import pytest
import numpy as np
import faiss
from pathlib import Path
from maposcal.embeddings import faiss_index

@pytest.fixture
def sample_vectors():
    """Create a sample set of vectors for testing."""
    # Create 10 random vectors of dimension 4
    np.random.seed(42)  # For reproducibility
    return np.random.rand(10, 4).astype('float32')

@pytest.fixture
def sample_index(sample_vectors):
    """Create a sample FAISS index."""
    return faiss_index.build_faiss_index(sample_vectors)

def test_build_faiss_index(sample_vectors):
    """Test building a FAISS index from vectors."""
    index = faiss_index.build_faiss_index(sample_vectors)
    assert isinstance(index, faiss.IndexFlatL2)
    assert index.ntotal == len(sample_vectors)

def test_build_faiss_index_empty():
    """Test that building an index with empty vectors raises an error."""
    empty_vectors = np.array([])
    with pytest.raises(ValueError, match="Cannot build FAISS index with empty vectors array"):
        faiss_index.build_faiss_index(empty_vectors)

def test_save_and_load_index(sample_index, tmp_path):
    """Test saving and loading a FAISS index."""
    # Save the index
    index_path = tmp_path / "test_index.faiss"
    faiss_index.save_index(sample_index, index_path)
    assert index_path.exists()
    
    # Load the index
    loaded_index = faiss_index.load_index(index_path)
    assert isinstance(loaded_index, faiss.IndexFlatL2)
    assert loaded_index.ntotal == sample_index.ntotal

def test_search_index(sample_index, sample_vectors):
    """Test searching the index for nearest neighbors."""
    # Use the first vector as the query
    query = sample_vectors[0]
    
    # Search for 3 nearest neighbors
    indices, distances = faiss_index.search_index(sample_index, query, k=3)
    
    # Check the results
    assert len(indices) == 3
    assert len(distances) == 3
    assert indices[0] == 0  # The query vector should be its own nearest neighbor
    assert all(isinstance(i, np.int64) for i in indices)
    assert all(isinstance(d, np.float32) for d in distances)
    assert all(d >= 0 for d in distances)  # Distances should be non-negative

def test_search_index_with_large_k(sample_index, sample_vectors):
    """Test searching with k larger than number of vectors."""
    query = sample_vectors[0]
    
    # k larger than number of vectors
    indices, distances = faiss_index.search_index(sample_index, query, k=20)
    
    # FAISS will return all vectors and pad with -1 indices and very large distances
    assert len(indices) == 20
    assert len(distances) == 20
    assert all(i == -1 for i in indices[10:])  # Padding indices
    # Accept either inf or very large values for padding
    assert all((np.isinf(d) or d >= 1e10) for d in distances[10:])  # Padding distances

def test_search_index_with_invalid_query(sample_index):
    """Test searching with invalid query vector."""
    # Query with wrong dimension
    invalid_query = np.random.rand(5).astype('float32')  # Should be 4 dimensions
    with pytest.raises(AssertionError):  # FAISS raises AssertionError for dimension mismatch
        faiss_index.search_index(sample_index, invalid_query)

def test_index_persistence(sample_vectors, tmp_path):
    """Test that saved and loaded index produces same results as original."""
    # Create and save index
    original_index = faiss_index.build_faiss_index(sample_vectors)
    index_path = tmp_path / "test_index.faiss"
    faiss_index.save_index(original_index, index_path)
    
    # Load index
    loaded_index = faiss_index.load_index(index_path)
    
    # Compare search results
    query = sample_vectors[0]
    original_indices, original_distances = faiss_index.search_index(original_index, query)
    loaded_indices, loaded_distances = faiss_index.search_index(loaded_index, query)
    
    np.testing.assert_array_equal(original_indices, loaded_indices)
    np.testing.assert_array_almost_equal(original_distances, loaded_distances)
