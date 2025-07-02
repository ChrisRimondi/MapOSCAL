from maposcal import settings
from typing import Tuple
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

    def __init__(self, model: str = settings.openai_model):
        """
        Initialize the LLM handler.

        Args:
            model (str): The model to use for LLM interactions
        """
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", settings.openai_base_url),
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
