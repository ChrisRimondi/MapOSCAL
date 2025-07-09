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
load_dotenv()

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
        elif command and command in settings.DEFAULT_LLM_CONFIGS:
            # Use command-specific defaults
            config = settings.DEFAULT_LLM_CONFIGS[command]
            self.provider = config["provider"]
            self.model = config["model"]
        else:
            # Fall back to legacy defaults
            self.provider = "openai"
            self.model = settings.openai_model

        # Validate provider
        if self.provider not in settings.LLM_PROVIDERS:
            raise ValueError(f"Unsupported provider: {self.provider}")

        # Get provider configuration
        provider_config = settings.LLM_PROVIDERS[self.provider]
        self.base_url = provider_config["base_url"]
        self.api_key_env = provider_config["api_key_env"]
        
        # Initialize OpenAI client (works for OpenAI, Azure, and Gemini via OpenAI-compatible API)
        self.client = OpenAI(
            api_key=os.getenv(self.api_key_env),
            base_url=os.getenv(f"{self.provider.upper()}_BASE_URL", self.base_url),
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

    def query(self, prompt: str) -> str:
        """
        Query the LLM with a prompt.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            str: The LLM's response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=8000,
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.error(f"[{datetime.now()}] 429 Rate Limit hit: {e}")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise
