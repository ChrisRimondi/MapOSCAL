#!/usr/bin/env python3
from typing import Tuple
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMHandler:
    """
    A class to handle interactions with the LLM.
    """
    def __init__(self, model: str = "gpt-4.1-mini"):
        """
        Initialize the LLM handler.
        
        Args:
            model (str): The model to use for LLM interactions
        """
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        self.encoding = tiktoken.get_encoding("cl100k_base")    
    
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
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise 