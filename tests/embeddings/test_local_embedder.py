import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from maposcal.embeddings import local_embedder


@pytest.fixture(autouse=True)
def reset_model():
    # Reset the global model before each test
    local_embedder._model = None
    local_embedder._model_name = "all-MiniLM-L6-v2"


@patch("maposcal.embeddings.local_embedder.SentenceTransformer")
def test_load_model_default(mock_st):
    mock_model = MagicMock()
    mock_st.return_value = mock_model
    model = local_embedder.load_model()
    assert model is mock_model
    assert local_embedder._model is mock_model
    assert local_embedder.get_model_name() == "all-MiniLM-L6-v2"


@patch("maposcal.embeddings.local_embedder.SentenceTransformer")
def test_load_model_custom_name(mock_st):
    mock_model = MagicMock()
    mock_st.return_value = mock_model
    model = local_embedder.load_model("custom-model")
    assert model is mock_model
    assert local_embedder.get_model_name() == "custom-model"


@patch("maposcal.embeddings.local_embedder.load_model")
def test_embed_chunks_success(mock_load_model):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.ones((2, 3))
    mock_load_model.return_value = mock_model
    texts = ["foo", "bar"]
    embeddings = local_embedder.embed_chunks(texts)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 3)
    mock_model.encode.assert_called_once_with(texts, show_progress_bar=True)


@patch("maposcal.embeddings.local_embedder.load_model")
def test_embed_one_success(mock_load_model):
    mock_model = MagicMock()
    mock_model.encode.return_value = [np.ones(3)]
    mock_load_model.return_value = mock_model
    text = "foo"
    embedding = local_embedder.embed_one(text)
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (3,)
    mock_model.encode.assert_called_once_with([text])


@patch("maposcal.embeddings.local_embedder.load_model")
def test_embed_chunks_empty_raises(mock_load_model):
    with pytest.raises(ValueError, match="Cannot embed empty list of texts"):
        local_embedder.embed_chunks([])


@patch("maposcal.embeddings.local_embedder.load_model")
def test_embed_one_empty_raises(mock_load_model):
    with pytest.raises(ValueError, match="Cannot embed empty text"):
        local_embedder.embed_one("")


def test_get_model_name():
    # Should return the default model name
    assert local_embedder.get_model_name() == "all-MiniLM-L6-v2"
    # After loading a custom model
    local_embedder._model_name = "foo-bar"
    assert local_embedder.get_model_name() == "foo-bar"
