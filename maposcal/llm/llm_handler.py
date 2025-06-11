#!/usr/bin/env python3
from typing import Tuple
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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
    
    def query(self, prompt: str) -> Tuple[str, int]:
        """
        Query the LLM with a prompt and return the response and token count.
        
        Args:
            prompt (str): The prompt to send to the LLM
            
        Returns:
            Tuple[str, int]: The response content and token count
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        token_count = self.count_tokens(content)
        return content.strip("```json").strip("```"), token_count 