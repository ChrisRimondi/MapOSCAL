"""
Core analyzer module for processing repository code and generating embeddings.
This module handles the main analysis workflow including chunking, embedding,
feature extraction, and file summarization.
"""

from pathlib import Path
from maposcal.embeddings import local_embedder, faiss_index, meta_store
from maposcal.analyzer import chunker, rules
from maposcal.llm.llm_handler import LLMHandler
from typing import List, Dict, Any

import numpy as np

class Analyzer:
    """
    Main analyzer class for processing repository code and generating embeddings.
    
    This class orchestrates the analysis workflow including:
    - Chunking and embedding repository files
    - Extracting security features
    - Generating file-level summaries
    """
    
    def __init__(self, repo_path: str, output_dir: str = ".oscalgen"):
        """
        Initialize the analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
            output_dir: Directory to store analysis outputs (default: ".oscalgen")
        """
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
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
        print("Chunking and embedding files...")
        self.chunks = chunker.analyze_repo(self.repo_path)
        texts = [c['content'] for c in self.chunks]
        embeddings = local_embedder.embed_chunks(texts)
        index = faiss_index.build_faiss_index(embeddings)
        faiss_index.save_index(index, self.output_dir / "index.faiss")
        meta_store.save_metadata(self.chunks, self.output_dir / "meta.json")

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
        meta_store.save_metadata(self.chunks, self.output_dir / "meta.json")

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
        print("Generating file-level summaries...")
        summary_meta: Dict[str, Dict[str, Any]] = {}
        vectors: List[np.ndarray] = []
        idx = 0

        for file_path in self.repo_path.rglob("*"):
            if not file_path.is_file() or file_path.suffix in [".png", ".jpg", ".exe", ".dll"]:
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                summary = LLMHandler.query(content)
                vec = local_embedder.embed_one(summary)
                vectors.append(vec)
                summary_meta[str(file_path)] = {
                    "summary": summary,
                    "vector_id": idx
                }
                idx += 1
            except Exception:
                continue

        if vectors:
            all_vectors = np.vstack(vectors)
            summary_index = faiss_index.build_faiss_index(all_vectors)
            faiss_index.save_index(summary_index, self.output_dir / "summary_index.faiss")
            meta_store.save_metadata(summary_meta, self.output_dir / "summary_meta.json")
