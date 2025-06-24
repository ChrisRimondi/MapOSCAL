"""
Repository chunking utilities for breaking down code files into manageable pieces.
This module handles the analysis of repository files and their chunking based on file types.
"""

from pathlib import Path
from typing import List, Dict, Any
from maposcal.analyzer.parser import parse_file
from traceback import format_exc
import logging
import settings

logger = logging.getLogger()

def analyze_repo(repo_path: Path) -> List[Dict[str, Any]]:
    """
    Analyze a repository and break its files into chunks.

    Args:
        repo_path: Path to the repository root

    Returns:
        List of dictionaries containing chunk information including:
        - content: The text content of the chunk
        - source_file: Path to the source file
        - chunk_type: Type of chunk (code, config, doc, or unknown)
        - start_line: Starting line number (if applicable)
        - end_line: Ending line number (if applicable)
        List of all applicable file names used to generate the chunks.
    """
    chunks = []
    for file_path in repo_path.rglob("*"):
        logger.debug(f"Analyzing repo ({repo_path}) and file {file_path}")
        if (
            not file_path.is_file()
            or file_path.suffix in settings.ignored_file_extensions
        ):
            continue
            
        # Exclude files with certain patterns in the name
        if any(
            pattern in file_path.name.lower()
            for pattern in settings.ignored_filename_patterns
        ):
            continue
            
        try:
            logger.info(f"Parsing file ({file_path}) into chunks.")
            try:
                parsed = parse_file(file_path)
            except:
                logger.error(f"Faile to parse ({file_path}) - {format_exc()}")

            logger.debug(f"Parsing ({file_path}) completed.")

            for chunk in parsed:
                chunk["source_file"] = str(file_path)
                chunk["chunk_type"] = detect_chunk_type(file_path.suffix)
                chunks.append(chunk)
        except Exception:
            continue

    return chunks


def detect_chunk_type(suffix: str) -> str:
    """
    Determine the type of chunk based on file extension.

    Args:
        suffix: File extension (including the dot)

    Returns:
        String indicating chunk type: "code", "config", "doc", or "unknown"
    """

    if suffix in [".py", ".go", ".java", ".js", ".ts", ".rb", ".cs"]:
        return "code"
    elif suffix in [".yaml", ".yml", ".json"]:
        return "config"
    elif suffix in [".md", ".rst", ".txt"]:
        return "doc"
    else:
        return "unknown"
