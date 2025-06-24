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
from typing import List, Dict, Any
import os
import numpy as np
from maposcal.analyzer.chunker import detect_chunk_type
import logging
import settings

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger()


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
    """

    def __init__(self, repo_path: str, output_dir: str = ".oscalgen"):
        """
        Initialize the analyzer.

        Args:
            repo_path: Path to the repository to analyze
            output_dir: Directory to store analysis results (default: .oscalgen)
        """
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Storage for analysis results
        self.chunks = []
        self.file_summaries = {}

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
        index_path = self.output_dir / f"index.faiss"
        meta_path = self.output_dir / f"meta.json"
        logger.debug(f"Saving index to: {index_path}")
        logger.debug(f"Saving metadata to: {meta_path}")

        faiss_index.save_index(index, index_path)
        meta_store.save_metadata(self.chunks, meta_path)

        self.summarize_files()

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

        llm_handler = LLMHandler()

        for file_path in self.repo_path.rglob("*"):
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
            chunk_type = detect_chunk_type(file_path.suffix)
            if chunk_type not in ["code", "config"]:
                continue
            try:
                # Begin manual enrichment before LLM involvement
                logger.info(f"Beginning rules-based inspection of {file_path}")
                file_inspector_results = rules.begin_inspection(str(file_path))

                content = file_path.read_text(encoding="utf-8")
                prompt = pt.build_file_summary_prompt(file_path.name, content)
                summary = llm_handler.query(prompt=prompt)
                vec = local_embedder.embed_one(summary)
                vectors.append(vec)
                summary_meta[str(file_path)] = {
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
            summary_index_path = self.output_dir / f"summary_index.faiss"
            summary_meta_path = self.output_dir / f"summary_meta.json"
            logger.debug(f"Saving summary index to: {summary_index_path}")
            logger.debug(f"Saving summary metadata to: {summary_meta_path}")

            faiss_index.save_index(summary_index, summary_index_path)
            meta_store.save_metadata(summary_meta, summary_meta_path)
        else:
            logger.warning("No vectors were generated for summaries.")
