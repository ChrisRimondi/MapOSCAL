"""
File parsing utilities for different file types.
This module provides specialized parsers for different file formats including
Python, YAML, and Markdown files.
"""

from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger()

def parse_python(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a Python file into chunks based on function and class definitions.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of dictionaries containing:
        - content: The text content of the chunk
        - start_line: Starting line number
        - end_line: Ending line number
    """
    chunks = []
    lines = file_path.read_text(encoding='utf-8').splitlines()
    block = []
    start_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("def ") or line.strip().startswith("class "):
            if block:
                chunks.append({"content": "\n".join(block), "start_line": start_line, "end_line": i})
                block = []
            start_line = i
        block.append(line)
    if block:
        chunks.append({"content": "\n".join(block), "start_line": start_line, "end_line": len(lines)})
    return chunks

def parse_yaml(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a YAML file into chunks based on document separators.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        List of dictionaries containing:
        - content: The text content of the chunk
        - start_line: Always 0 (not tracked for YAML)
        - end_line: Always 0 (not tracked for YAML)
    """
    text = file_path.read_text(encoding='utf-8')
    return [{"content": block, "start_line": 0, "end_line": 0} for block in text.split("\n\n")]

def parse_markdown(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a Markdown file into chunks based on headers.
    
    Args:
        file_path: Path to the Markdown file
        
    Returns:
        List of dictionaries containing:
        - content: The text content of the chunk
    """
    lines = file_path.read_text(encoding='utf-8').splitlines()
    chunks = []
    block = []
    for line in lines:
        if line.startswith("#"):
            if block:
                chunks.append({"content": "\n".join(block)})
                block = []
        block.append(line)
    if block:
        chunks.append({"content": "\n".join(block)})
    return chunks

def parse_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a file based on its extension.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        List of dictionaries containing parsed chunks. The structure depends on the file type:
        - Python: Includes start_line and end_line
        - YAML: Includes start_line and end_line (always 0)
        - Markdown: Only includes content
        - Other: Only includes content
    """
    logger.info(f"Parsing file {file_path}")
    
    ext = file_path.suffix.lower()
    if ext == ".py":
        return parse_python(file_path)
    elif ext in [".yaml", ".yml"]:
        return parse_yaml(file_path)
    elif ext in [".md", ".markdown"]:
        return parse_markdown(file_path)
    else:
        return [{"content": file_path.read_text(encoding='utf-8')}]
