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

os.environ["TOKENIZERS_PARALLELISM"] = "false"

EXCLUDED_FILENAME_PATTERNS = ["test", "mock", "example", "sample"]

logger = logging.getLogger()

class Analyzer:
    """
    Main analyzer class for processing repository code and generating embeddings.
    
    This class orchestrates the analysis workflow including:
    - Chunking and embedding repository files
    - Extracting security features
    - Generating file-level summaries
    """
    
    def __init__(self, repo_path: str, output_dir: str = ".oscalgen", service_prefix: str = None):
        """
        Initialize the analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
            output_dir: Directory to store analysis outputs (default: ".oscalgen")
            service_prefix: Prefix for output files (default: None)
        """
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.service_prefix = service_prefix
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        """
        Run the complete analysis workflow.
        
        This method executes the analysis in three steps:
        1. Chunk and embed repository files
        2. Extract security features
        3. Generate file summaries
        """
        print("Starting repository analysis...")
        self.chunk_and_embed()
        self.extract_features()
        self.summarize_files()

    def chunk_and_embed(self) -> None:
        """
        Chunk repository files and generate embeddings.
        
        This method:
        1. Chunks repository files into manageable pieces
        2. Generates embeddings for each chunk
        3. Creates and saves a FAISS index for similarity search
        4. Saves chunk metadata
        """
        logger.info("Chunking and embedding files...")
        self.chunks = chunker.analyze_repo(self.repo_path)
        logger.debug(f"Found {len(self.chunks)} chunks from repository")
        
        if not self.chunks:
            logger.error("No chunks were generated from the repository")
            raise ValueError("No chunks were generated from the repository. Please check if the repository path is correct and contains valid files.")
            
        texts = [c['content'] for c in self.chunks]
        logger.debug(f"Extracted {len(texts)} text chunks for embedding")
        
        embeddings = local_embedder.embed_chunks(texts)
        index = faiss_index.build_faiss_index(embeddings)
        
        # Debug logging for file paths
        index_path = self.output_dir / f"{self.service_prefix}_index.faiss"
        meta_path = self.output_dir / f"{self.service_prefix}_meta.json"
        logger.debug(f"Saving index to: {index_path}")
        logger.debug(f"Saving metadata to: {meta_path}")
        
        faiss_index.save_index(index, index_path)
        meta_store.save_metadata(self.chunks, meta_path)

    def extract_features(self) -> None:
        """
        Extract security features from chunks using rule-based analysis.
        
        This method:
        1. Applies security rules to each chunk
        2. Updates chunk metadata with security flags and control hints
        3. Saves updated metadata
        """
        print("Extracting rule-based features...")
        self.chunks = rules.apply_rules(self.chunks)
        meta_store.save_metadata(self.chunks, self.output_dir / f"{self.service_prefix}_meta.json")

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
            if not file_path.is_file() or file_path.suffix in [".png", ".jpg", ".exe", ".dll", ".gitignore", ".idx",  ".pack"]:
                continue
            # Exclude files with certain patterns in the name
            if any(pattern in file_path.name.lower() for pattern in EXCLUDED_FILENAME_PATTERNS):
                continue
            chunk_type = detect_chunk_type(file_path.suffix)
            if chunk_type not in ["code", "config"]:
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                prompt = pt.build_file_summary_prompt(file_path.name, content)
                summary = llm_handler.query(prompt=prompt)
                vec = local_embedder.embed_one(summary)
                vectors.append(vec)
                summary_meta[str(file_path)] = {
                    "summary": summary,
                    "vector_id": idx
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
            summary_index_path = self.output_dir / f"{self.service_prefix}_summary_index.faiss"
            summary_meta_path = self.output_dir / f"{self.service_prefix}_summary_meta.json"
            logger.debug(f"Saving summary index to: {summary_index_path}")
            logger.debug(f"Saving summary metadata to: {summary_meta_path}")
            
            faiss_index.save_index(summary_index, summary_index_path)
            meta_store.save_metadata(summary_meta, summary_meta_path)
        else:
            logger.warning("No vectors were generated for summaries.")
