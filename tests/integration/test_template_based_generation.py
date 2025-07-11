"""
Integration test for template-based control generation.

This test verifies that the new template-based approach works correctly
in an end-to-end scenario with mock LLM responses.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from maposcal.generator.control_mapper import map_control


class TestTemplateBasedGeneration:
    """Test the template-based generation approach end-to-end."""

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_template_based_generation_success(self, mock_get_chunks, mock_llm_handler_class):
        """Test successful template-based generation with valid LLM content."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        
        # Mock LLM response with valid content
        mock_llm_content = {
            "control-status": "applicable and inherently satisfied",
            "control-explanation": "The system implements comprehensive access control through JWT authentication and role-based permissions.",
            "control-configuration": [],
            "statement-description": "Access control is implemented using JWT tokens with role-based permissions and secure session management."
        }
        mock_llm_handler.query.return_value = json.dumps(mock_llm_content)
        
        # Mock evidence chunks
        mock_get_chunks.return_value = [
            {"source_file": "auth.py", "content": "JWT authentication code"},
            {"source_file": "config.yaml", "content": "Authentication configuration"}
        ]
        
        # Test control data
        control_dict = {
            "id": "AC-1",
            "title": "Access Control Policy and Procedures",
            "statement": "The organization develops, documents, and disseminates access control policy."
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()
            
            # Test the generation
            result = map_control(control_dict, temp_dir)
            
            # Verify the result is a complete OSCAL control mapping
            assert isinstance(result, dict)
            assert "uuid" in result
            assert "control-id" in result
            assert result["control-id"] == "AC-1"
            
            # Verify all required props are present
            props = result["props"]
            prop_names = {prop["name"] for prop in props}
            required_props = {
                "control-status", "control-name", "control-description", 
                "control-explanation", "control-configuration"
            }
            assert required_props.issubset(prop_names)
            
            # Verify content was merged correctly
            for prop in props:
                if prop["name"] == "control-status":
                    assert prop["value"] == "applicable and inherently satisfied"
                elif prop["name"] == "control-explanation":
                    assert "JWT authentication" in prop["value"]
                elif prop["name"] == "control-name":
                    assert prop["value"] == "Access Control Policy and Procedures"
            
            # Verify statements
            assert len(result["statements"]) == 1
            statement = result["statements"][0]
            assert statement["statement-id"] == "AC-1_smt.a"
            assert "JWT tokens" in statement["description"]
            
            # Verify source code references
            annotations = result["annotations"]
            source_ref_annotation = next(
                (a for a in annotations if a["name"] == "source-code-reference"), None
            )
            assert source_ref_annotation is not None
            assert "auth.py" in source_ref_annotation["value"]
            assert "config.yaml" in source_ref_annotation["value"]

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_template_based_generation_with_configuration(self, mock_get_chunks, mock_llm_handler_class):
        """Test template-based generation with configuration details."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        
        # Mock LLM response with configuration
        mock_llm_content = {
            "control-status": "applicable but only satisfied through configuration",
            "control-explanation": "The system implements access control through configuration settings.",
            "control-configuration": [
                {
                    "file_path": "config.yaml",
                    "key_path": "auth.enabled",
                    "line_number": 10
                }
            ],
            "statement-description": "Access control is configured through YAML settings."
        }
        mock_llm_handler.query.return_value = json.dumps(mock_llm_content)
        
        # Mock evidence chunks
        mock_get_chunks.return_value = [
            {"source_file": "config.yaml", "content": "auth:\n  enabled: true"}
        ]
        
        # Test control data
        control_dict = {
            "id": "AC-2",
            "title": "Account Management",
            "statement": "The organization manages information system accounts."
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()
            
            # Test the generation
            result = map_control(control_dict, temp_dir)
            
            # Verify configuration was merged correctly
            for prop in result["props"]:
                if prop["name"] == "control-configuration":
                    assert len(prop["value"]) == 1
                    config = prop["value"][0]
                    assert config["file_path"] == "config.yaml"
                    assert config["key_path"] == "auth.enabled"
                    assert config["line_number"] == 10

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_template_based_generation_fallback(self, mock_get_chunks, mock_llm_handler_class):
        """Test template-based generation with fallback to template when LLM fails."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        
        # Mock LLM response with invalid content (missing required fields)
        mock_llm_content = {
            "control-status": "invalid status",  # Invalid status
            "control-explanation": "Short",  # Too short
        }
        mock_llm_handler.query.return_value = json.dumps(mock_llm_content)
        
        # Mock evidence chunks
        mock_get_chunks.return_value = [
            {"source_file": "auth.py", "content": "Authentication code"}
        ]
        
        # Test control data
        control_dict = {
            "id": "AC-3",
            "title": "Access Control",
            "statement": "The organization implements access control."
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            index_path.touch()
            meta_path.touch()
            
            # Test the generation (should fall back to template after retries)
            result = map_control(control_dict, temp_dir)
            
            # Verify we get a valid template with default content
            assert isinstance(result, dict)
            assert "uuid" in result
            assert "control-id" in result
            assert result["control-id"] == "AC-3"
            
            # Verify default control-status is used
            for prop in result["props"]:
                if prop["name"] == "control-status":
                    assert prop["value"] == "applicable and not satisfied"  # Default fallback

    @patch("maposcal.generator.control_mapper.LLMHandler")
    @patch("maposcal.generator.control_mapper.get_relevant_chunks")
    def test_template_based_generation_with_security_overview(self, mock_get_chunks, mock_llm_handler_class):
        """Test template-based generation with security overview integration."""
        # Setup mocks
        mock_llm_handler = Mock()
        mock_llm_handler_class.return_value = mock_llm_handler
        
        # Mock LLM response
        mock_llm_content = {
            "control-status": "applicable and inherently satisfied",
            "control-explanation": "The system implements access control based on the security overview.",
            "control-configuration": [],
            "statement-description": "Access control is implemented according to the security architecture."
        }
        mock_llm_handler.query.return_value = json.dumps(mock_llm_content)
        
        # Mock evidence chunks
        mock_get_chunks.return_value = [
            {"source_file": "auth.py", "content": "Authentication code"}
        ]
        
        # Test control data
        control_dict = {
            "id": "AC-4",
            "title": "Access Control",
            "statement": "The organization implements access control."
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create required files
            index_path = Path(temp_dir) / "index.faiss"
            meta_path = Path(temp_dir) / "meta.json"
            security_overview_path = Path(temp_dir) / "security_overview.md"
            
            index_path.touch()
            meta_path.touch()
            security_overview_path.write_text("Security overview content")
            
            # Test the generation
            result = map_control(control_dict, temp_dir)
            
            # Verify the result is valid
            assert isinstance(result, dict)
            assert result["control-id"] == "AC-4"
            
            # Verify LLM was called with security overview context
            # (The prompt should include the security overview)
            mock_llm_handler.query.assert_called()
            call_args = mock_llm_handler.query.call_args
            assert call_args is not None
            # The prompt is the first positional argument
            prompt = call_args[0][0] if call_args[0] else call_args[1]['prompt']
            assert "Security overview" in prompt 