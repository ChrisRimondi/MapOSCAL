import pytest
from maposcal.embeddings import meta_store


@pytest.fixture
def sample_metadata():
    return [
        {"id": 1, "content": "foo", "extra": "bar"},
        {"id": 2, "content": "baz", "extra": "qux"},
    ]


def test_save_and_load_metadata(tmp_path, sample_metadata):
    meta_path = tmp_path / "meta.json"
    meta_store.save_metadata(sample_metadata, meta_path)
    assert meta_path.exists()
    loaded = meta_store.load_metadata(meta_path)
    assert isinstance(loaded, list)
    assert loaded == sample_metadata


def test_get_chunk_by_index(sample_metadata):
    chunk = meta_store.get_chunk_by_index(sample_metadata, 1)
    assert chunk["id"] == 2
    assert chunk["content"] == "baz"
    assert chunk["extra"] == "qux"


def test_get_chunk_by_index_out_of_range(sample_metadata):
    with pytest.raises(IndexError):
        meta_store.get_chunk_by_index(sample_metadata, 10)


def test_load_metadata_file_not_found(tmp_path):
    missing_path = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        meta_store.load_metadata(missing_path)


def test_save_metadata_creates_parent(tmp_path, sample_metadata):
    nested_path = tmp_path / "nested/dir/meta.json"
    meta_store.save_metadata(sample_metadata, nested_path)
    assert nested_path.exists()
    loaded = meta_store.load_metadata(nested_path)
    assert loaded == sample_metadata
