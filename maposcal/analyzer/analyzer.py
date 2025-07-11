"""
Core analyzer module for processing repository code and generating embeddings.
This module handles the main analysis workflow including chunking, embedding,
feature extraction, and file summarization.
"""

from pathlib import Path
from maposcal.embeddings import local_embedder, faiss_index, meta_store
from maposcal.analyzer import chunker, rules
from maposcal.llm.llm_handler import LLMHandler
from maposcal.llm import prompt_templates as pt
from maposcal.utils.metadata import generate_metadata, inject_metadata_into_json
from typing import List, Dict, Any
import os
import numpy as np
from traceback import format_exc
import logging
from maposcal import settings
import hashlib
import json
import mimetypes
import yaml
import toml
import configparser

os.environ["TOKENIZERS_PARALLELISM"] = "false"

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


class Analyzer:
    """
    Analyzes a repository to extract and embed code files for OSCAL generation.
    This class performs comprehensive analysis of code repositories using a three-pass system:
    1. Vector embedding of code/config/docs for semantic search
    2. Semantic security summaries for file-level understanding
    3. Rule-based feature extraction for specific security patterns

    The analyzer generates FAISS indices and metadata files that enable efficient
    similarity search and provide the foundation for OSCAL control mapping.

    Key Features:
    - Intelligent file chunking based on file type and structure
    - Local embedding generation using sentence transformers
    - FAISS index creation for efficient similarity search
    - Security-focused file summarization using LLM analysis
    - Rule-based security pattern detection and flagging
    - Configurable configuration file extensions
    """

    def __init__(
        self,
        repo_path: str,
        output_dir: str = ".oscalgen",
        config_extensions: List[str] = None,
        auto_discover_config: bool = True,
        config_files: List[str] = None,
        llm_config: dict = None,
    ):
        """
        Initialize the analyzer.

        Args:
            repo_path: Path to the repository to analyze
            output_dir: Directory to store analysis results (default: .oscalgen)
            config_extensions: List of file extensions to treat as configuration files
                              (used when auto_discover_config is True)
            auto_discover_config: Whether to auto-discover configuration files by extension
                                 or use manual file list (default: True)
            config_files: List of specific file paths to treat as configuration files
                         (used when auto_discover_config is False)
        """
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set configuration file extensions for auto-discovery
        if config_extensions is not None:
            # Ensure extensions start with dot
            self.config_extensions = [
                ext if ext.startswith(".") else f".{ext}" for ext in config_extensions
            ]
        else:
            self.config_extensions = settings.config_file_extensions

        self.auto_discover_config = auto_discover_config

        # Set manual config files list
        if config_files is not None:
            # Convert to Path objects relative to repo root
            self.config_files_list = [Path(file_path) for file_path in config_files]
        else:
            self.config_files_list = []

        # Storage for analysis results
        self.chunks = []
        self.file_summaries = {}
        self.config_files = []

        # Store LLM configuration
        self.llm_config = llm_config

    def run(self) -> None:
        """
        Run the analysis workflow: chunk, embed, and summarize files.
        """

        logger.info("Chunking and embedding files...")
        self.chunks = chunker.analyze_repo(self.repo_path)
        logger.debug(f"Found {len(self.chunks)} chunks from repository")

        if not self.chunks:
            logger.error("No chunks were generated from the repository")
            raise ValueError(
                "No chunks were generated from the repository. Please check if the repository path is correct and contains valid files."
            )

        texts = [c["content"] for c in self.chunks]
        logger.debug(f"Extracted {len(texts)} text chunks for embedding")

        embeddings = local_embedder.embed_chunks(texts)
        index = faiss_index.build_faiss_index(embeddings)

        # Debug logging for file paths
        index_path = self.output_dir / "index.faiss"
        meta_path = self.output_dir / "meta.json"
        logger.debug(f"Saving index to: {index_path}")
        logger.debug(f"Saving metadata to: {meta_path}")

        faiss_index.save_index(index, index_path)

        # Generate metadata for this operation
        if self.llm_config:
            provider_config = settings.LLM_PROVIDERS[self.llm_config["provider"]]
            metadata = generate_metadata(
                model=self.llm_config["model"],
                provider=self.llm_config["provider"],
                base_url=provider_config["base_url"],
                command="analyze",
            )
            # Inject metadata into chunks data
            chunks_with_metadata = inject_metadata_into_json(
                {"chunks": self.chunks}, metadata
            )
            meta_store.save_metadata(chunks_with_metadata, meta_path)
        else:
            meta_store.save_metadata(self.chunks, meta_path)

        self.summarize_files()
        self.save_config_files()

    def summarize_files(self) -> None:
        """
        Generate summaries for each file in the repository.

        This method:
        1. Processes each file in the repository
        2. Generates a summary using LLM
        3. Creates embeddings for summaries
        4. Builds and saves a FAISS index for summary similarity search
        5. Saves summary metadata
        """
        logger.info("Generating file-level summaries...")
        summary_meta: Dict[str, Dict[str, Any]] = {}
        vectors: List[np.ndarray] = []
        idx = 0

        # Use provided LLM config or fall back to defaults
        if self.llm_config:
            llm_handler = LLMHandler(
                provider=self.llm_config["provider"], model=self.llm_config["model"]
            )
        else:
            llm_handler = LLMHandler(command="analyze")

        for file_path in self.repo_path.rglob("*"):
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

            # Check if this is a configuration file
            is_config_file = False

            if self.auto_discover_config:
                # Auto-discover by extension
                is_config_file = file_path.suffix.lower() in [
                    ext.lower() for ext in self.config_extensions
                ]
            else:
                # Manual file specification
                relative_path = file_path.relative_to(self.repo_path)
                is_config_file = relative_path in self.config_files_list

            # Handle config files separately
            if is_config_file:
                logger.info(f"Processing config file: {file_path}")
                self.process_config_file(file_path)
                continue

            try:
                # Begin manual enrichment before LLM involvement
                file_inspector_results = None
                try:
                    logger.info(f"Beginning rules-based inspection of {file_path}")
                    file_inspector_results = rules.begin_inspection(
                        str(file_path), str(self.repo_path)
                    )

                except Exception:
                    logger.error(
                        f"Failed to perform inspection on {str(file_path)} - {format_exc()}"
                    )

                try:
                    # Create embeddings from inspector's summary
                    if (
                        file_inspector_results is not None
                        and "file_summary" in file_inspector_results
                    ):
                        inspector_summary = file_inspector_results["file_summary"]
                        summary_vec = local_embedder.embed_one(inspector_summary)
                        vectors.append(summary_vec)
                        logger.info(
                            f"Successfully created embeddings for file {str(file_path)}."
                        )
                    else:
                        logger.debug(
                            f"No inspector summary available for {str(file_path)} - skipping inspector embeddings"
                        )
                except Exception:
                    logger.error(
                        f"Failed to generate and store vectorized embeddings for inspector's results on {str(file_path)} - {format_exc()}"
                    )

                content = file_path.read_text(encoding="utf-8")
                prompt = pt.build_file_summary_prompt(file_path.name, content)
                summary = llm_handler.query(prompt=prompt)
                vec = local_embedder.embed_one(summary)
                vectors.append(vec)

                # Use relative path as key instead of absolute path
                relative_path = str(file_path.relative_to(self.repo_path))
                summary_meta[relative_path] = {
                    "summary": summary,
                    "vector_id": idx,
                    "inspector_results": file_inspector_results,
                }
                idx += 1
                logger.debug(f"Processed file: {file_path}")
            except Exception as e:
                logger.error(f"Skipped {file_path} due to error: {e}")
                continue

        if vectors:
            all_vectors = np.vstack(vectors)
            summary_index = faiss_index.build_faiss_index(all_vectors)

            # Debug logging for summary file paths
            summary_index_path = self.output_dir / "summary_index.faiss"
            summary_meta_path = self.output_dir / "summary_meta.json"
            logger.debug(f"Saving summary index to: {summary_index_path}")
            logger.debug(f"Saving summary metadata to: {summary_meta_path}")

            faiss_index.save_index(summary_index, summary_index_path)

            # Generate metadata for summary operation
            if self.llm_config:
                provider_config = settings.LLM_PROVIDERS[self.llm_config["provider"]]
                metadata = generate_metadata(
                    model=self.llm_config["model"],
                    provider=self.llm_config["provider"],
                    base_url=provider_config["base_url"],
                    command="analyze",
                )
                # Inject metadata into summary data
                summary_with_metadata = inject_metadata_into_json(
                    summary_meta, metadata
                )
                meta_store.save_metadata(summary_with_metadata, summary_meta_path)
            else:
                meta_store.save_metadata(summary_meta, summary_meta_path)
        else:
            logger.warning("No vectors were generated for summaries.")

    def extract_keys_from_config(self, content: str, file_path: Path) -> List[str]:
        """
        Extract keys from configuration file content based on file type.

        Args:
            content: The file content as a string
            file_path: Path to the file for determining file type

        Returns:
            List of keys found in the configuration file
        """
        keys = []

        try:
            suffix_lower = file_path.suffix.lower()

            if suffix_lower in [".yaml", ".yml"]:
                # Parse YAML and extract keys
                yaml_data = yaml.safe_load(content)
                if yaml_data:
                    keys = self._extract_keys_recursive(yaml_data)

            elif suffix_lower == ".json":
                # Parse JSON and extract keys
                json_data = json.loads(content)
                if json_data:
                    keys = self._extract_keys_recursive(json_data)

            elif suffix_lower == ".toml":
                # Parse TOML and extract keys
                toml_data = toml.loads(content)
                if toml_data:
                    keys = self._extract_keys_recursive(toml_data)

            elif suffix_lower in [".ini", ".conf"]:
                # Parse INI/CONF files and extract keys
                keys = self._extract_keys_from_ini(content)

            elif suffix_lower == ".properties":
                # Parse PROPERTIES files and extract keys
                keys = self._extract_keys_from_properties(content)

        except Exception as e:
            logger.warning(f"Error extracting keys from {file_path}: {e}")

        return keys

    def _extract_keys_recursive(self, data: Any, prefix: str = "") -> List[str]:
        """
        Recursively extract keys from nested data structures.

        Args:
            data: The data structure to extract keys from
            prefix: Current key prefix for nested structures

        Returns:
            List of keys found in the data structure
        """
        keys = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_key = f"{prefix}.{key}" if prefix else key
                keys.append(current_key)

                # Recursively extract keys from nested structures
                if isinstance(value, (dict, list)):
                    keys.extend(self._extract_keys_recursive(value, current_key))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_key = f"{prefix}[{i}]" if prefix else f"[{i}]"

                # Recursively extract keys from nested structures
                if isinstance(item, (dict, list)):
                    keys.extend(self._extract_keys_recursive(item, current_key))

        return keys

    def _extract_keys_from_ini(self, content: str) -> List[str]:
        """
        Extract keys from INI/CONF file content.

        Args:
            content: The INI/CONF file content as a string

        Returns:
            List of keys found in the INI/CONF file
        """
        keys = []

        try:
            config = configparser.ConfigParser()
            config.read_string(content)

            for section in config.sections():
                keys.append(f"[{section}]")
                for option in config.options(section):
                    keys.append(f"[{section}].{option}")

        except Exception as e:
            logger.warning(f"Error parsing INI/CONF content: {e}")

        return keys

    def _extract_keys_from_properties(self, content: str) -> List[str]:
        """
        Extract keys from PROPERTIES file content.

        Args:
            content: The PROPERTIES file content as a string

        Returns:
            List of keys found in the PROPERTIES file
        """
        keys = []

        try:
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                # Skip empty lines, comments, and lines without '='
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("!")
                    or "=" not in line
                ):
                    continue

                # Extract the key part (before the first '=')
                key = line.split("=", 1)[0].strip()
                if key:
                    keys.append(key)

        except Exception as e:
            logger.warning(f"Error parsing PROPERTIES content: {e}")

        return keys

    def process_config_file(self, file_path: Path) -> None:
        """
        Process configuration files separately from the main chunking and embedding workflow.

        Creates a JSON object for each configuration file with the following structure:
        {
          "file_path": "relative/path/to/file",
          "selection_reason": "extension",
          "mime": "text/x-yaml",
          "hash": "sha256:...",
          "keys": [...]
        }

        Args:
            file_path: Path to the configuration file to process
        """
        logger.info(f"Processing configuration file: {file_path}")

        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")

            # Calculate SHA256 hash
            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Determine MIME type based on file extension
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type is None:
                # Fallback MIME types for common config formats
                mime_map = {
                    ".yaml": "text/x-yaml",
                    ".yml": "text/x-yaml",
                    ".json": "application/json",
                    ".toml": "text/x-toml",
                    ".ini": "text/x-ini",
                    ".conf": "text/plain",
                    ".properties": "text/x-properties",
                }
                mime_type = mime_map.get(file_path.suffix, "text/plain")

            # Get relative path from repo root
            relative_path = file_path.relative_to(self.repo_path)

            # Create config file object
            config_obj = {
                "file_path": str(relative_path),
                "selection_reason": "extension",
                "mime": mime_type,
                "hash": f"sha256:{file_hash}",
                "keys": self.extract_keys_from_config(content, file_path),
            }

            # Add to config files list
            self.config_files.append(config_obj)

            logger.debug(f"Processed config file: {file_path}")

        except Exception as e:
            logger.error(f"Error processing config file {file_path}: {e}")

    def save_config_files(self) -> None:
        """
        Save the processed configuration files data to a JSON file in the output directory.
        """
        if self.config_files:
            config_output_path = self.output_dir / "config_files.json"
            try:
                with open(config_output_path, "w", encoding="utf-8") as f:
                    json.dump(self.config_files, f, indent=2, ensure_ascii=False)
                logger.info(
                    f"Saved {len(self.config_files)} config files to {config_output_path}"
                )
            except Exception as e:
                logger.error(f"Error saving config files: {e}")
        else:
            logger.info("No config files to save")
