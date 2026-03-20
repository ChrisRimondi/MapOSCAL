from maposcal import settings
import tiktoken
from openai import OpenAI
from openai import RateLimitError
from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime

# Load environment variables
load_dotenv(override=True)

logger = logging.getLogger()


class LLMHandler:
    """
    A class to handle interactions with the LLM.
    """

    def __init__(self, provider: str = None, model: str = None, command: str = None):
        """
        Initialize the LLM handler.

        Args:
            provider (str): The LLM provider to use (openai, gemini, anthropic, azure)
            model (str): The specific model to use
            command (str): The command being executed (analyze, summarize, generate, evaluate)
        """
        # Determine provider and model based on parameters
        if provider and model:
            # Use provided provider and model
            self.provider = provider
            self.model = model
            self.default_temperature = 0.7  # Legacy default
        elif command and command in settings.DEFAULT_LLM_CONFIGS:
            # Use command-specific defaults
            config = settings.DEFAULT_LLM_CONFIGS[command]
            self.provider = config["provider"]
            self.model = config["model"]
            self.default_temperature = config.get("temperature", 0.7)
        else:
            # Fall back to legacy defaults
            self.provider = "openai"
            self.model = settings.openai_model
            self.default_temperature = 0.7

        # Validate provider
        if self.provider not in settings.LLM_PROVIDERS:
            raise ValueError(f"Unsupported provider: {self.provider}")

        # Get provider configuration
        provider_config = settings.LLM_PROVIDERS[self.provider]
        self.base_url = provider_config["base_url"]
        self.api_key_env = provider_config["api_key_env"]

        # Get the API key
        api_key = os.getenv(self.api_key_env)
        base_url = os.getenv(f"{self.provider.upper()}_BASE_URL", self.base_url)

        # Log for debugging (mask the key for security)
        logger.info(f"Provider: {self.provider}")
        logger.info(f"Looking for API key in environment variable: {self.api_key_env}")
        logger.info(f"Default temperature: {self.default_temperature}")

        # Validate API key
        if not api_key:
            logger.error(
                f"No API key found for environment variable: {self.api_key_env}"
            )
            logger.error(
                f"Available environment variables: {[k for k in os.environ.keys() if 'API_KEY' in k]}"
            )

            # Show all API key environment variables (masked)
            for key in os.environ.keys():
                if "API_KEY" in key:
                    value = os.environ[key]
                    masked_value = (
                        value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                    )
                    logger.error(f"  {key}: {masked_value}")

        # Validate API key
        if not api_key:
            raise ValueError(
                f"No API key found for {self.provider}. Please set the {self.api_key_env} environment variable."
            )

        # Initialize OpenAI client (works for OpenAI, Azure, Gemini, and Anthropic via OpenAI-compatible API)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.encoding = tiktoken.get_encoding(settings.tiktoken_encoding)

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.

        Args:
            text (str): Text to count tokens for

        Returns:
            int: Number of tokens
        """
        return len(self.encoding.encode(text))

    def query(self, prompt: str, max_tokens: int = 8000, temperature: float = None) -> str:
        """
        Query the LLM with a prompt.

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate (default: 8000)
            temperature: Temperature for response randomness (default: uses command-specific default)

        Returns:
            str: The LLM's response
        """
        # Use default temperature if none specified
        if temperature is None:
            temperature = self.default_temperature
            
        logger.debug(f"Using temperature: {temperature} for model: {self.model}")
        
        try:
            # Determine which parameters to use based on model
            model_params = self._get_model_parameters(max_tokens, temperature)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **model_params
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.error(f"[{datetime.now()}] 429 Rate Limit hit: {e}")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise
    
    def _get_model_parameters(self, max_tokens: int, temperature: float = 0.7) -> dict:
        """
        Get the appropriate parameters based on the model.
        
        Args:
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for response randomness
            
        Returns:
            dict: Parameters to use in the API call
        """
        # Models that use max_completion_tokens instead of max_tokens
        new_token_models = [
            "gpt-5-mini",
            "gpt-5",
            "gpt-5o",
            "gpt-5o-mini",
            "gpt-5o-flash"
        ]
        
        # Models that have restricted temperature (only support default value)
        restricted_temperature_models = [
            "gpt-5-mini",
            "gpt-5"
        ]
        
        params = {}
        
        # Handle token parameters
        if any(model in self.model.lower() for model in new_token_models):
            logger.debug(f"Using max_completion_tokens for model: {self.model}")
            params["max_completion_tokens"] = max_tokens
        else:
            logger.debug(f"Using max_tokens for model: {self.model}")
            params["max_tokens"] = max_tokens
        
        # Handle temperature parameter
        if any(model in self.model.lower() for model in restricted_temperature_models):
            logger.debug(f"Using default temperature for restricted model: {self.model}")
            # Don't set temperature - let it use the default
        else:
            logger.debug(f"Using custom temperature {temperature} for model: {self.model}")
            params["temperature"] = temperature
        
        return params
