"""
This modules is only intended for the storage of various global settings.
"""
global openai_model
global openai_base_url
global tiktoken_encoding
global local_embeddings_model

openai_model = 'gpt-4.1-mini'
openai_base_url = 'https://api.openai.com/v1'
tiktoken_encoding = 'cl100k_base'
local_embeddings_model = 'all-MiniLM-L6-v2'


if __name__ == "__main__":
    print('This module not intended for interactive use.  Pleaes use cli.py.')