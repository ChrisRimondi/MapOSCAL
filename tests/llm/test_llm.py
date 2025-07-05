import os
import pytest
from unittest.mock import patch, MagicMock
from maposcal.llm.llm_handler import LLMHandler
import maposcal.llm.prompt_templates as prompt_templates

class TestLLMHandler:
    @patch('maposcal.llm.llm_handler.tiktoken')
    def test_count_tokens(self, mock_tiktoken):
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        handler = LLMHandler(model="test-model")
        assert handler.count_tokens("test text") == 4
        mock_encoding.encode.assert_called_once_with("test text")

    @patch('maposcal.llm.llm_handler.OpenAI')
    @patch('maposcal.llm.llm_handler.tiktoken')
    def test_query_success(self, mock_tiktoken, mock_openai):
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "LLM response"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        handler = LLMHandler(model="test-model")
        result = handler.query("prompt")
        assert result == "LLM response"
        mock_client.chat.completions.create.assert_called_once()

    @patch('maposcal.llm.llm_handler.OpenAI')
    @patch('maposcal.llm.llm_handler.tiktoken')
    @patch('maposcal.llm.llm_handler.logger')
    def test_query_rate_limit(self, mock_logger, mock_tiktoken, mock_openai):
        from openai import RateLimitError
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RateLimitError(
            message='rate limit', response=MagicMock(), body={}
        )
        mock_openai.return_value = mock_client
        handler = LLMHandler(model="test-model")
        with patch('time.sleep') as mock_sleep:
            handler.query("prompt")
            mock_logger.error.assert_called()
            mock_sleep.assert_called()

    @patch('maposcal.llm.llm_handler.OpenAI')
    @patch('maposcal.llm.llm_handler.tiktoken')
    @patch('maposcal.llm.llm_handler.logger')
    def test_query_general_exception(self, mock_logger, mock_tiktoken, mock_openai):
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception('general error')
        mock_openai.return_value = mock_client
        handler = LLMHandler(model="test-model")
        with pytest.raises(Exception):
            handler.query("prompt")
        mock_logger.error.assert_called()

class TestPromptTemplates:
    def test_build_service_overview_prompt(self):
        context = "Service context"
        prompt = prompt_templates.build_service_overview_prompt(context)
        assert "Service Overview" in prompt
        assert context in prompt

    def test_build_file_summary_prompt(self):
        filename = "main.py"
        file_content = "def foo(): pass"
        prompt = prompt_templates.build_file_summary_prompt(filename, file_content)
        assert filename in prompt
        assert file_content in prompt
        assert "Summary:" in prompt

    def test_build_control_prompt(self):
        prompt = prompt_templates.build_control_prompt(
            control_id="AC-1",
            control_name="Access Control",
            control_description="desc",
            evidence_chunks=[{"chunk_type": "code", "source_file": "main.py", "start_line": 1, "end_line": 10, "content": "def foo(): pass"}],
            main_uuid="uuid1",
            statement_uuid="uuid2",
            security_overview="overview"
        )
        assert "AC-1" in prompt
        assert "Access Control" in prompt
        assert "overview" in prompt
        assert "def foo(): pass" in prompt
        assert "Generate the JSON now" in prompt

    def test_build_critique_prompt(self):
        implemented_requirements = [{"control-id": "AC-1"}]
        prompt = prompt_templates.build_critique_prompt(implemented_requirements, security_overview="overview")
        assert "violations" in prompt
        assert "overview" in prompt
        assert "AC-1" in prompt

    def test_build_revise_prompt(self):
        implemented_requirements = [{"control-id": "AC-1"}]
        violations = [{"path": "props[0]", "issue": "Missing"}]
        prompt = prompt_templates.build_revise_prompt(implemented_requirements, violations, security_overview="overview")
        assert "violations" in prompt
        assert "overview" in prompt
        assert "AC-1" in prompt

    def test_build_evaluate_prompt(self):
        requirement = {"control-id": "AC-1"}
        prompt = prompt_templates.build_evaluate_prompt(requirement)
        assert "control-id" in prompt
        assert "scores" in prompt or "Score" in prompt
