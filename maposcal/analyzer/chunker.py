"""
Repository chunking utilities for breaking down code files into manageable pieces.
This module handles the analysis of repository files and their chunking based on file types.
"""

from pathlib import Path
from typing import List, Dict, Any
from maposcal.analyzer.parser import parse_file
from traceback import format_exc
import logging
from maposcal import settings

logger = logging.getLogger()


def should_ignore_path(path: Path) -> bool:
    """
    Check if a path should be ignored based on directory patterns.

    Args:
        path: Path to check

    Returns:
        True if the path should be ignored, False otherwise
    """
    # Check if any part of the path matches ignored directory patterns
    for part in path.parts:
        if any(
            pattern in part.lower() for pattern in settings.ignored_directory_patterns
        ):
            return True
    return False


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

        # Skip if not a file
        if not file_path.is_file():
            continue

        # Skip hidden files (files that start with ".")
        if file_path.name.startswith("."):
            logger.debug(f"Skipping hidden file {file_path}")
            continue

        # Skip if path contains ignored directory patterns
        if should_ignore_path(file_path):
            logger.debug(f"Skipping {file_path} due to ignored directory pattern")
            continue

        # Skip if file extension is ignored
        if file_path.suffix in settings.ignored_file_extensions:
            logger.debug(f"Skipping {file_path} due to ignored file extension")
            continue

        # Exclude files with certain patterns in the name
        if any(
            pattern in file_path.name.lower()
            for pattern in settings.ignored_filename_patterns
        ):
            logger.debug(f"Skipping {file_path} due to ignored filename pattern")
            continue

        # Skip config files - they will be handled separately
        if detect_chunk_type(file_path.suffix) == "config":
            logger.debug(
                f"Skipping config file {file_path} - will be processed separately"
            )
            continue

        try:
            logger.info(f"Parsing file ({file_path}) into chunks.")
            try:
                parsed = parse_file(file_path)
            except Exception:
                logger.error(f"Failed to parse ({file_path}) - {format_exc()}")
                continue

            logger.debug(f"Parsing ({file_path}) completed.")

            for chunk in parsed:
                # Use relative path instead of absolute path
                relative_path = str(file_path.relative_to(repo_path))
                chunk["source_file"] = relative_path
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
    elif suffix in settings.config_file_extensions:
        return "config"
    elif suffix in [".md", ".rst", ".txt"]:
        return "doc"
    else:
        return "unknown"
