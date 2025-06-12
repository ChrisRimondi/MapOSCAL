import typer
from maposcal.analyzer.analyzer import Analyzer
import os
import yaml
import json
from maposcal.generator.control_mapper import map_control
from maposcal.embeddings import faiss_index, meta_store, local_embedder
from pathlib import Path
import re

app = typer.Typer()

SAMPLE_CONFIG_PATH = "sample_control_config.yaml"
SAMPLE_CONFIG_CONTENT = {
    "control_id": "SC-8",
    "control_name": "Transmission Confidentiality And Integrity",
    "control_description": "The information system protects the [Selection (one or more): confidentiality; integrity] of transmitted information."
}

@app.command()
def analyze(repo_path: str, output_dir: str = ".oscalgen"):
    analyzer = Analyzer(repo_path=repo_path, output_dir=output_dir)
    analyzer.run()

@app.command()
def generate(config: str = None, output_dir: str = ".oscalgen", top_k: int = 5):
    """Generate OSCAL component for control"""
    # If no config is provided, use or create the sample config
    config_path = config or SAMPLE_CONFIG_PATH
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            yaml.dump(SAMPLE_CONFIG_CONTENT, f)
        typer.echo(f"Sample config created at {config_path}. Please edit it or provide your own.")
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    typer.echo(f"Loaded config: {config_data}")

    # Embed the control description for querying
    query_embedding = local_embedder.embed_one(config_data["control_description"])

    # Query index.faiss (chunk-level)
    index_path = Path(output_dir) / "index.faiss"
    meta_path = Path(output_dir) / "meta.json"
    if not index_path.exists() or not meta_path.exists():
        typer.echo(f"Could not find {index_path} or {meta_path}. Please run analyze first.")
        raise typer.Exit(code=1)
    index = faiss_index.load_index(index_path)
    meta = meta_store.load_metadata(meta_path)
    chunk_indices, _ = faiss_index.search_index(index, query_embedding, k=top_k)
    chunk_results = [meta_store.get_chunk_by_index(meta, idx) for idx in chunk_indices if idx < len(meta)]

    # Query summary_index.faiss (file-level summaries)
    summary_index_path = Path(output_dir) / "summary_index.faiss"
    summary_meta_path = Path(output_dir) / "summary_meta.json"
    summary_results = []
    if summary_index_path.exists() and summary_meta_path.exists():
        summary_index = faiss_index.load_index(summary_index_path)
        summary_meta = meta_store.load_metadata(summary_meta_path)
        summary_indices, _ = faiss_index.search_index(summary_index, query_embedding, k=top_k)
        for idx in summary_indices:
            if str(idx) in summary_meta:
                summary_results.append(summary_meta[str(idx)])
            else:
                # Try to get by file path if available
                for k, v in summary_meta.items():
                    if v.get("vector_id") == idx:
                        summary_results.append(v)
                        break

    # Combine and deduplicate relevant chunks
    relevant_chunks = chunk_results + summary_results
    # Optionally deduplicate by file path or content
    seen = set()
    unique_relevant_chunks = []
    for c in relevant_chunks:
        key = c.get("source_file") if "source_file" in c else c.get("summary")
        if key and key not in seen:
            unique_relevant_chunks.append(c)
            seen.add(key)

    # Call map_control
    result = map_control(
        config_data["control_id"],
        config_data["control_name"],
        config_data["control_description"],
        unique_relevant_chunks
    )

    # Clean and parse the LLM response as JSON
    try:
        cleaned = result.strip()
        cleaned = re.sub(r"^```json|```$", "", cleaned, flags=re.MULTILINE).strip()
        parsed = json.loads(cleaned)
    except Exception as e:
        typer.echo(f"Failed to parse LLM response as JSON: {e}")
        parsed = {"llm_raw_response": result}

    # Write result to output_dir as JSON
    output_path = os.path.join(output_dir, f"{config_data['control_id']}_oscal_component.json")
    with open(output_path, "w") as f:
        json.dump(parsed, f, indent=2)
    typer.echo(f"Generated OSCAL component written to {output_path}")

if __name__ == "__main__":
    app()
