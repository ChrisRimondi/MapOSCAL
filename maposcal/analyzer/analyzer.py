from pathlib import Path
from maposcal.embeddings import local_embedder, faiss_index, meta_store
from maposcal.analyzer import chunker, rules
from maposcal.llm.llm_handler import query_llm

import numpy as np

class Analyzer:
    def __init__(self, repo_path: str, output_dir: str = ".oscalgen"):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        print("Starting repository analysis...")
        self.chunk_and_embed()
        self.extract_features()
        self.summarize_files()

    def chunk_and_embed(self):
        print("Chunking and embedding files...")
        self.chunks = chunker.analyze_repo(self.repo_path)
        texts = [c['content'] for c in self.chunks]
        embeddings = local_embedder.embed_chunks(texts)
        index = faiss_index.build_faiss_index(embeddings)
        faiss_index.save_index(index, self.output_dir / "index.faiss")
        meta_store.save_metadata(self.chunks, self.output_dir / "meta.json")

    def extract_features(self):
        print("Extracting rule-based features...")
        self.chunks = rules.apply_rules(self.chunks)
        meta_store.save_metadata(self.chunks, self.output_dir / "meta.json")

    def summarize_files(self):
        print("Generating file-level summaries...")
        summary_meta = {}
        vectors = []
        idx = 0

        for file_path in self.repo_path.rglob("*"):
            if not file_path.is_file() or file_path.suffix in [".png", ".jpg", ".exe", ".dll"]:
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                summary = query_llm(content)
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
