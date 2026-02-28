import os
import pytest
from unittest.mock import patch, MagicMock
from maposcal.llm.llm_handler import LLMHandler
import maposcal.llm.prompt_templates as prompt_templates


class TestLLMHandler:
    pytestmark = pytest.mark.unit

    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_count_tokens(self, mock_openai, mock_tiktoken):
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        # Mock the OpenAI client to avoid API key issues
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        handler = LLMHandler(model="test-model")
        assert handler.count_tokens("test text") == 4
        mock_encoding.encode.assert_called_once_with("test text")

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
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

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch("maposcal.llm.llm_handler.logger")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_query_rate_limit(self, mock_logger, mock_tiktoken, mock_openai):
        from openai import RateLimitError

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RateLimitError(
            message="rate limit", response=MagicMock(), body={}
        )
        mock_openai.return_value = mock_client
        handler = LLMHandler(model="test-model")
        with patch("time.sleep") as mock_sleep:
            handler.query("prompt")
            mock_logger.error.assert_called()
            mock_sleep.assert_called()

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch("maposcal.llm.llm_handler.logger")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_query_general_exception(self, mock_logger, mock_tiktoken, mock_openai):
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("general error")
        mock_openai.return_value = mock_client
        handler = LLMHandler(model="test-model")
        with pytest.raises(Exception):
            handler.query("prompt")
        mock_logger.error.assert_called()

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch.dict(
        os.environ, {"OPENAI_API_KEY": "sk-test-key", "GEMINI_API_KEY": "AIza-test-key"}
    )
    def test_llm_handler_openai_provider(self, mock_tiktoken, mock_openai):
        """Test LLMHandler with OpenAI provider."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        handler = LLMHandler(provider="openai", model="gpt-4")

        assert handler.provider == "openai"
        assert handler.model == "gpt-4"
        assert handler.base_url == "https://api.openai.com/v1"
        assert handler.api_key_env == "OPENAI_API_KEY"
        mock_openai.assert_called_with(
            api_key="sk-test-key", base_url="https://api.openai.com/v1"
        )

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch.dict(os.environ, {"GEMINI_API_KEY": "AIza-test-key"})
    def test_llm_handler_gemini_provider(self, mock_tiktoken, mock_openai):
        """Test LLMHandler with Gemini provider."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        handler = LLMHandler(provider="gemini", model="gemini-2.5-flash")

        assert handler.provider == "gemini"
        assert handler.model == "gemini-2.5-flash"
        assert (
            handler.base_url
            == "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        assert handler.api_key_env == "GEMINI_API_KEY"
        mock_openai.assert_called_with(
            api_key="AIza-test-key",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"})
    def test_llm_handler_command_defaults(self, mock_tiktoken, mock_openai):
        """Test LLMHandler with command-specific defaults."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        handler = LLMHandler(command="generate")
        
        assert handler.provider == "openai"
        assert handler.model == "gpt-4.1"
        mock_openai.assert_called_with(
            api_key="sk-test-key", base_url="https://api.openai.com/v1"
        )

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"})
    def test_llm_handler_custom_base_url(self, mock_tiktoken, mock_openai):
        """Test LLMHandler with custom base URL."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        with patch.dict(
            os.environ, {"OPENAI_BASE_URL": "https://custom.openai.com/v1"}
        ):
            LLMHandler(provider="openai", model="gpt-4")

            mock_openai.assert_called_with(
                api_key="sk-test-key", base_url="https://custom.openai.com/v1"
            )

    @patch("maposcal.llm.llm_handler.OpenAI")
    @patch("maposcal.llm.llm_handler.tiktoken")
    def test_llm_handler_missing_api_key(self, mock_tiktoken, mock_openai):
        """Test LLMHandler with missing API key."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        # Clear the environment completely for this test
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="No API key found for openai"):
                LLMHandler(provider="openai", model="gpt-4")

    def test_llm_handler_invalid_provider(self):
        """Test LLMHandler with invalid provider."""
        with pytest.raises(ValueError, match="Unsupported provider: invalid"):
            LLMHandler(provider="invalid", model="gpt-4")


class TestPromptTemplates:
    """Prompt template functions return non-empty strings containing expected substrings."""

    _EVIDENCE_CHUNK = {
        "chunk_type": "code",
        "source_file": "main.py",
        "start_line": 1,
        "end_line": 10,
        "content": "def foo(): pass",
    }

    @pytest.mark.parametrize("func,kwargs,expected_substrings", [
        pytest.param(
            prompt_templates.build_service_overview_prompt,
            {"context": "Service context"},
            ["Service Overview", "Service context"],
            id="service_overview",
        ),
        pytest.param(
            prompt_templates.build_file_summary_prompt,
            {"filename": "main.py", "file_content": "def foo(): pass"},
            ["main.py", "def foo(): pass", "Summary:"],
            id="file_summary",
        ),
        pytest.param(
            prompt_templates.build_control_prompt,
            {
                "control_id": "AC-1",
                "control_name": "Access Control",
                "control_description": "desc",
                "evidence_chunks": [_EVIDENCE_CHUNK],
                "main_uuid": "uuid1",
                "statement_uuid": "uuid2",
                "security_overview": "overview",
            },
            ["AC-1", "Access Control", "overview", "def foo(): pass", "Generate the JSON now"],
            id="control_prompt",
        ),
        pytest.param(
            prompt_templates.build_critique_prompt,
            {
                "implemented_requirements": [{"control-id": "AC-1"}],
                "security_overview": "overview",
            },
            ["violations", "overview", "AC-1"],
            id="critique",
        ),
        pytest.param(
            prompt_templates.build_revise_prompt,
            {
                "implemented_requirements": [{"control-id": "AC-1"}],
                "violations": [{"path": "props[0]", "issue": "Missing"}],
                "security_overview": "overview",
            },
            ["violations", "overview", "AC-1"],
            id="revise",
        ),
        pytest.param(
            prompt_templates.build_evaluate_prompt,
            {"requirement": {"control-id": "AC-1"}},
            ["control-id", "scores"],
            id="evaluate",
        ),
    ])
    @pytest.mark.unit
    def test_prompt_templates(self, func, kwargs, expected_substrings):
        result = func(**kwargs)
        assert isinstance(result, str)
        assert len(result) > 0
        for substring in expected_substrings:
            assert substring in result
