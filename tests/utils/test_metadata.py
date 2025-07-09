"""
Tests for metadata utilities.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch
from maposcal.utils.metadata import (
    generate_metadata,
    inject_metadata_into_json,
    inject_metadata_into_markdown,
    extract_metadata_from_json,
    extract_metadata_from_markdown,
)


class TestGenerateMetadata:
    def test_generate_metadata_basic(self):
        """Test basic metadata generation."""
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="generate"
        )
        
        assert "generation_info" in metadata
        info = metadata["generation_info"]
        assert info["model"] == "gpt-4"
        assert info["provider"] == "openai"
        assert info["base_url"] == "https://api.openai.com/v1"
        assert info["command"] == "generate"
        assert "start_time" in info
        assert info["config_file"] is None
        assert info["version"] == "1.0.0"

    def test_generate_metadata_with_config_file(self):
        """Test metadata generation with config file."""
        metadata = generate_metadata(
            model="gemini-2.5-flash",
            provider="gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            command="analyze",
            config_file="config.yaml"
        )
        
        info = metadata["generation_info"]
        assert info["model"] == "gemini-2.5-flash"
        assert info["provider"] == "gemini"
        assert info["config_file"] == "config.yaml"

    def test_generate_metadata_custom_version(self):
        """Test metadata generation with custom version."""
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="evaluate",
            version="2.0.0"
        )
        
        assert metadata["generation_info"]["version"] == "2.0.0"


class TestInjectMetadataIntoJson:
    def test_inject_metadata_into_json_basic(self):
        """Test basic JSON metadata injection."""
        data = {"implemented_requirements": [{"control-id": "AC-1"}]}
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="generate"
        )
        
        result = inject_metadata_into_json(data, metadata)
        
        assert "_metadata" in result
        assert result["_metadata"] == metadata
        assert "implemented_requirements" in result
        assert result["implemented_requirements"] == data["implemented_requirements"]

    def test_inject_metadata_into_json_preserves_original(self):
        """Test that original data is not modified."""
        data = {"key": "value"}
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="generate"
        )
        
        result = inject_metadata_into_json(data, metadata)
        
        # Original data should not be modified
        assert data == {"key": "value"}
        # Result should have both original data and metadata
        assert result["key"] == "value"
        assert result["_metadata"] == metadata

    def test_inject_metadata_into_json_complex_data(self):
        """Test metadata injection with complex nested data."""
        data = {
            "validation_failures": [
                {"control_id": "AC-1", "reason": "Missing field"},
                {"control_id": "AC-2", "reason": "Invalid format"}
            ],
            "summary": {"total": 2, "passed": 0}
        }
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="generate"
        )
        
        result = inject_metadata_into_json(data, metadata)
        
        assert result["_metadata"] == metadata
        assert result["validation_failures"] == data["validation_failures"]
        assert result["summary"] == data["summary"]


class TestInjectMetadataIntoMarkdown:
    def test_inject_metadata_into_markdown_basic(self):
        """Test basic markdown metadata injection."""
        content = "# Security Overview\n\nThis is the content."
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="summarize"
        )
        
        result = inject_metadata_into_markdown(content, metadata)
        
        assert result.startswith("<!--\nmetadata:")
        assert result.endswith("\n\n# Security Overview\n\nThis is the content.")
        assert "model: gpt-4" in result
        assert "provider: openai" in result
        assert "command: summarize" in result

    def test_inject_metadata_into_markdown_preserves_content(self):
        """Test that original content is preserved."""
        content = "Original content here"
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="summarize"
        )
        
        result = inject_metadata_into_markdown(content, metadata)
        
        assert content in result
        assert result.endswith(content)

    def test_inject_metadata_into_markdown_all_fields(self):
        """Test that all metadata fields are included."""
        metadata = generate_metadata(
            model="gemini-2.5-flash",
            provider="gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            command="analyze",
            config_file="config.yaml",
            version="1.5.0"
        )
        
        result = inject_metadata_into_markdown("content", metadata)
        
        expected_fields = [
            "model: gemini-2.5-flash",
            "provider: gemini",
            "base_url: https://generativelanguage.googleapis.com/v1beta/openai/",
            "command: analyze",
            "config_file: config.yaml",
            "version: 1.5.0"
        ]
        
        for field in expected_fields:
            assert field in result


class TestExtractMetadataFromJson:
    def test_extract_metadata_from_json_with_metadata(self):
        """Test extracting metadata from JSON with metadata."""
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="generate"
        )
        data = {
            "_metadata": metadata,
            "implemented_requirements": [{"control-id": "AC-1"}]
        }
        
        extracted = extract_metadata_from_json(data)
        
        assert extracted == metadata

    def test_extract_metadata_from_json_without_metadata(self):
        """Test extracting metadata from JSON without metadata."""
        data = {"implemented_requirements": [{"control-id": "AC-1"}]}
        
        extracted = extract_metadata_from_json(data)
        
        assert extracted == {}

    def test_extract_metadata_from_json_empty(self):
        """Test extracting metadata from empty JSON."""
        data = {}
        
        extracted = extract_metadata_from_json(data)
        
        assert extracted == {}


class TestExtractMetadataFromMarkdown:
    def test_extract_metadata_from_markdown_with_metadata(self):
        """Test extracting metadata from markdown with metadata."""
        content = """<!--
metadata:
  model: gpt-4
  provider: openai
  base_url: https://api.openai.com/v1
  start_time: 2024-01-15T10:30:00Z
  command: summarize
  config_file: config.yaml
  version: 1.0.0
-->

# Security Overview

This is the content."""
        
        extracted = extract_metadata_from_markdown(content)
        
        assert "generation_info" in extracted
        info = extracted["generation_info"]
        assert info["model"] == "gpt-4"
        assert info["provider"] == "openai"
        assert info["base_url"] == "https://api.openai.com/v1"
        assert info["command"] == "summarize"
        assert info["config_file"] == "config.yaml"
        assert info["version"] == "1.0.0"

    def test_extract_metadata_from_markdown_without_metadata(self):
        """Test extracting metadata from markdown without metadata."""
        content = "# Security Overview\n\nThis is the content."
        
        extracted = extract_metadata_from_markdown(content)
        
        assert extracted == {}

    def test_extract_metadata_from_markdown_empty(self):
        """Test extracting metadata from empty markdown."""
        content = ""
        
        extracted = extract_metadata_from_markdown(content)
        
        assert extracted == {}

    def test_extract_metadata_from_markdown_malformed(self):
        """Test extracting metadata from malformed markdown."""
        content = """<!--
metadata:
  model: gpt-4
  provider: openai
-->

# Content"""
        
        extracted = extract_metadata_from_markdown(content)
        
        # Should still extract what it can
        assert "generation_info" in extracted
        info = extracted["generation_info"]
        assert info["model"] == "gpt-4"
        assert info["provider"] == "openai"

    def test_extract_metadata_from_markdown_no_end_comment(self):
        """Test extracting metadata from markdown with no end comment."""
        content = """<!--
metadata:
  model: gpt-4
  provider: openai

# Content"""
        
        extracted = extract_metadata_from_markdown(content)
        
        # Should handle gracefully
        assert extracted == {}


class TestMetadataIntegration:
    def test_full_metadata_cycle_json(self):
        """Test full cycle: generate -> inject -> extract for JSON."""
        original_data = {"requirements": [{"id": "AC-1"}]}
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="generate"
        )
        
        # Inject metadata
        data_with_metadata = inject_metadata_into_json(original_data, metadata)
        
        # Extract metadata
        extracted_metadata = extract_metadata_from_json(data_with_metadata)
        
        # Verify
        assert extracted_metadata == metadata
        assert data_with_metadata["requirements"] == original_data["requirements"]

    def test_full_metadata_cycle_markdown(self):
        """Test full cycle: generate -> inject -> extract for markdown."""
        original_content = "# Security Overview\n\nContent here."
        metadata = generate_metadata(
            model="gpt-4",
            provider="openai",
            base_url="https://api.openai.com/v1",
            command="summarize"
        )
        
        # Inject metadata
        content_with_metadata = inject_metadata_into_markdown(original_content, metadata)
        
        # Extract metadata
        extracted_metadata = extract_metadata_from_markdown(content_with_metadata)
        
        # Verify
        assert extracted_metadata["generation_info"]["model"] == metadata["generation_info"]["model"]
        assert extracted_metadata["generation_info"]["provider"] == metadata["generation_info"]["provider"]
        assert original_content in content_with_metadata 