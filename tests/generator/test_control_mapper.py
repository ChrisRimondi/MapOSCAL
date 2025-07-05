"""
Tests for the control_mapper module.

This module tests the control mapping functionality including semantic search,
LLM-based analysis, and response parsing.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
from maposcal.generator.control_mapper import (
    get_relevant_chunks,
    map_control,
    parse_llm_response,
)


class TestGetRelevantChunks:
    """Test get_relevant_chunks function."""

    @patch("maposcal.generator.control_mapper.faiss_index")
    @patch("maposcal.generator.control_mapper.meta_store")
    @patch("maposcal.generator.control_mapper.local_embedder")
    def test_get_relevant_chunks_basic(
        self, mock_embedder, mock_meta_store, mock_faiss_index
    ):
        """Test basic functionality of get_relevant_chunks."""
        # Setup mocks
        mock_embedder.embed_one.return_value = [0.1, 0.2, 0.3]
        mock_index = Mock()
        mock_faiss_index.load_index.return_value = mock_index
        mock_faiss_index.search_index.return_value = ([0], [0.1])

        mock_meta = [
            {"source_file": "auth.py", "content": "def authenticate_user(): pass"}
        ]
        mock_meta_store.load_metadata.return_value = mock_meta
        mock_meta_store.get_chunk_by_index.side_effect = lambda meta, idx: meta[idx]

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()

            result = get_relevant_chunks("test query", temp_dir)
            assert len(result) == 1
            assert result[0]["source_file"] == "auth.py"

    @patch("maposcal.generator.control_mapper.faiss_index")
    @patch("maposcal.generator.control_mapper.meta_store")
    @patch("maposcal.generator.control_mapper.local_embedder")
    def test_get_relevant_chunks_with_summary_index(
        self, mock_embedder, mock_meta_store, mock_faiss_index
    ):
        """Test get_relevant_chunks with summary index."""
        # Setup mocks
        mock_embedder.embed_one.return_value = [0.1, 0.2, 0.3]
        mock_index = Mock()
        mock_faiss_index.load_index.return_value = mock_index
        mock_faiss_index.search_index.return_value = ([0], [0.1])

        mock_meta = [
            {"source_file": "auth.py", "content": "def authenticate_user(): pass"}
        ]
        mock_meta_store.load_metadata.return_value = mock_meta
        mock_meta_store.get_chunk_by_index.side_effect = lambda meta, idx: meta[idx]

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files including summary index
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            summary_index_path = Path(temp_dir) / "summary_index.faiss"
            summary_meta_path = Path(temp_dir) / "summary_meta.json"

            index_path.touch()
            meta_path.touch()
            summary_index_path.touch()
            summary_meta_path.touch()

            # Mock summary metadata
            mock_summary_meta = {
                "0": {"source_file": "config.py", "summary": "Configuration file"}
            }
            mock_meta_store.load_metadata.side_effect = [mock_meta, mock_summary_meta]

            result = get_relevant_chunks("test query", temp_dir)
            assert len(result) >= 1

    @patch("maposcal.generator.control_mapper.faiss_index")
    @patch("maposcal.generator.control_mapper.meta_store")
    @patch("maposcal.generator.control_mapper.local_embedder")
    def test_get_relevant_chunks_missing_files(
        self, mock_embedder, mock_meta_store, mock_faiss_index
    ):
        """Test get_relevant_chunks with missing index files."""
        mock_embedder.embed_one.return_value = [0.1, 0.2, 0.3]

        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError):
                get_relevant_chunks("test query", temp_dir)

    @patch("maposcal.generator.control_mapper.faiss_index")
    @patch("maposcal.generator.control_mapper.meta_store")
    @patch("maposcal.generator.control_mapper.local_embedder")
    def test_get_relevant_chunks_with_control_hints(
        self, mock_embedder, mock_meta_store, mock_faiss_index
    ):
        """Test get_relevant_chunks with control hints filtering."""
        # Setup mocks
        mock_embedder.embed_one.return_value = [0.1, 0.2, 0.3]
        mock_index = Mock()
        mock_faiss_index.load_index.return_value = mock_index
        mock_faiss_index.search_index.return_value = ([0], [0.1])

        # Mock regular metadata
        mock_meta = [
            {
                "source_file": "/path/to/auth.py",
                "content": "def authenticate_user(): pass",
            },
            {
                "source_file": "/path/to/other.py",
                "content": "def other_function(): pass",
            },
        ]

        # Mock summary metadata with control hints
        mock_summary_meta = {
            "/path/to/auth.py": {
                "source_file": "/path/to/auth.py",
                "summary": "Authentication module",
                "inspector_results": {"control_hints": ["ac4", "sc5"]},
            },
            "/path/to/other.py": {
                "source_file": "/path/to/other.py",
                "summary": "Other module",
                "inspector_results": {"control_hints": ["ac6"]},
            },
        }

        # The function calls load_metadata multiple times:
        # 1. For regular metadata (meta.json)
        # 2. For summary metadata (summary_meta.json) - first time for semantic search
        # 3. For summary metadata (summary_meta.json) - second time for control hints
        mock_meta_store.load_metadata.side_effect = [
            mock_meta,
            mock_summary_meta,
            mock_summary_meta,
        ]
        mock_meta_store.get_chunk_by_index.side_effect = lambda meta, idx: meta[idx]

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            summary_index_path = Path(temp_dir) / "summary_index.faiss"
            summary_meta_path = Path(temp_dir) / "summary_meta.json"

            index_path.touch()
            meta_path.touch()
            summary_index_path.touch()
            summary_meta_path.touch()

            # Test with control_id that matches control hints
            result = get_relevant_chunks("test query", temp_dir, control_id="AC-4")

            # Should include both semantic search results and control hint matches
            assert len(result) >= 1

            # Check that auth.py is included (has ac4 control hint)
            auth_chunks = [
                chunk
                for chunk in result
                if chunk.get("source_file") == "/path/to/auth.py"
            ]
            assert len(auth_chunks) > 0

            # Check that other.py is not included (doesn't have ac4 control hint)
            # other_chunks = [
            #     chunk
            #     for chunk in result
            #     if "other.py" in chunk["source_file"]
            # ]
            # assert len(other_chunks) == 0


class TestMapControl:
    """Test map_control function."""

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_map_control_basic(self, mock_get_chunks, mock_llm_handler_class):
        """Test basic map_control functionality."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        mock_llm_handler.query.return_value = "Mock LLM response"

        mock_get_chunks.return_value = [
            {"source_file": "auth.py", "content": "def authenticate_user(): pass"}
        ]

        control_dict = {
            "id": "AC-1",
            "title": "Access Control Policy",
            "statement": "The organization develops access control policies.",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()

            result = map_control(control_dict, temp_dir)
            assert result == "Mock LLM response"

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_map_control_with_security_overview(
        self, mock_get_chunks, mock_llm_handler_class
    ):
        """Test map_control with security overview file."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        mock_llm_handler.query.return_value = "Mock LLM response"

        mock_get_chunks.return_value = [
            {"source_file": "auth.py", "content": "def authenticate_user(): pass"}
        ]

        control_dict = {
            "id": "AC-1",
            "title": "Access Control Policy",
            "statement": "The organization develops access control policies.",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            security_overview_path = Path(temp_dir) / "security_overview.md"

            index_path.touch()
            meta_path.touch()
            security_overview_path.write_text("Security overview content")

            result = map_control(control_dict, temp_dir)
            assert result == "Mock LLM response"

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_map_control_with_parameters(self, mock_get_chunks, mock_llm_handler_class):
        """Test map_control with control parameters."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        mock_llm_handler.query.return_value = "Mock LLM response"

        mock_get_chunks.return_value = [
            {"source_file": "auth.py", "content": "def authenticate_user(): pass"}
        ]

        control_dict = {
            "id": "AC-1",
            "title": "Access Control Policy",
            "statement": "The organization develops access control policies with {{ insert: param, ac-1_prm_1 }}.",
            "params": [
                {
                    "id": "ac-1_prm_1",
                    "prose": ["specific requirements"],
                    "resolved-values": ["detailed requirements"],
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()

            result = map_control(control_dict, temp_dir)
            assert result == "Mock LLM response"

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_map_control_with_list_statement(
        self, mock_get_chunks, mock_llm_handler_class
    ):
        """Test map_control with list statement format."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        mock_llm_handler.query.return_value = "Mock LLM response"

        mock_get_chunks.return_value = [
            {"source_file": "auth.py", "content": "def authenticate_user(): pass"}
        ]

        control_dict = {
            "id": "AC-1",
            "title": "Access Control Policy",
            "statement": ["The organization develops access control policies."],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()

            result = map_control(control_dict, temp_dir)
            assert result == "Mock LLM response"


class TestParseLLMResponse:
    """Test parse_llm_response function."""

    def test_parse_llm_response_valid_json(self):
        """Test parsing valid JSON response."""
        json_content = {"control-status": "implemented", "control-name": "Test Control"}

        response = json.dumps(json_content)
        result = parse_llm_response(response)

        assert result == json_content

    def test_parse_llm_response_with_code_block(self):
        """Test parsing response with markdown code block."""
        json_content = {"control-status": "implemented", "control-name": "Test Control"}

        response = f"Here is the JSON:\n```json\n{json.dumps(json_content)}\n```"
        result = parse_llm_response(response)

        assert result == json_content

    def test_parse_llm_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        invalid_json = "{ invalid json }"

        result = parse_llm_response(invalid_json)
        assert "llm_raw_response" in result
        assert result["llm_raw_response"] == invalid_json

    def test_parse_llm_response_empty(self):
        """Test parsing empty response."""
        result = parse_llm_response("")
        assert "llm_raw_response" in result
        assert result["llm_raw_response"] == ""

    def test_parse_llm_response_none(self):
        """Test parsing None response."""
        result = parse_llm_response(None)
        assert "llm_raw_response" in result
        assert result["llm_raw_response"] is None

    def test_parse_llm_response_with_extra_text(self):
        """Test parsing response with extra text before/after JSON."""
        json_content = {"control-status": "implemented", "control-name": "Test Control"}

        response = f"Some text before\n{json.dumps(json_content)}\nSome text after"
        result = parse_llm_response(response)

        assert result == json_content

    def test_parse_llm_response_multiple_json_blocks(self):
        """Test parsing response with multiple JSON blocks (should use first)."""
        json_content1 = {
            "control-status": "implemented",
            "control-name": "Test Control 1",
        }
        json_content2 = {
            "control-status": "not-implemented",
            "control-name": "Test Control 2",
        }

        response = f"```json\n{json.dumps(json_content1)}\n```\n```json\n{json.dumps(json_content2)}\n```"
        result = parse_llm_response(response)

        assert result == json_content1


class TestControlMapperIntegration:
    """Integration tests for control mapper."""

    @patch("maposcal.generator.control_mapper.local_embedder")
    @patch("maposcal.generator.control_mapper.faiss_index")
    @patch("maposcal.generator.control_mapper.meta_store")
    @patch("maposcal.generator.control_mapper.LLMHandler")
    def test_full_control_mapping_workflow(
        self, mock_llm_handler_class, mock_meta_store, mock_faiss_index, mock_embedder
    ):
        """Test the full control mapping workflow."""
        # Setup all mocks
        mock_embedder.embed_one.return_value = [0.1, 0.2, 0.3]
        mock_index = Mock()
        mock_faiss_index.load_index.return_value = mock_index
        mock_faiss_index.search_index.return_value = ([0], [0.1])

        mock_meta = [
            {"source_file": "auth.py", "content": "def authenticate_user(): pass"}
        ]
        mock_meta_store.load_metadata.return_value = mock_meta
        mock_meta_store.get_chunk_by_index.side_effect = lambda meta, idx: meta[idx]

        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        mock_llm_response = {
            "control-status": "implemented",
            "control-name": "Access Control Policy",
            "control-description": "The organization develops access control policies",
            "control-explanation": "Authentication function found in auth.py",
        }
        mock_llm_handler.query.return_value = json.dumps(mock_llm_response)

        control_dict = {
            "id": "AC-1",
            "title": "Access Control Policy",
            "statement": "The organization develops, disseminates, and reviews/updates access control policies.",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()

            # Test full workflow
            result = map_control(control_dict, temp_dir)
            parsed_result = parse_llm_response(result)

            assert parsed_result["control-status"] == "implemented"
            assert parsed_result["control-name"] == "Access Control Policy"
            assert "auth.py" in parsed_result["control-explanation"]
