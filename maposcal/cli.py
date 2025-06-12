import typer
from maposcal.analyzer.analyzer import Analyzer
import os
import yaml
import json
from maposcal.generator.control_mapper import map_control, parse_llm_response
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

    # Call map_control
    result = map_control(
        config_data["control_id"],
        config_data["control_name"],
        config_data["control_description"],
        output_dir,
        top_k
    )

    # Parse the LLM response as JSON
    parsed = parse_llm_response(result)

    # Write result to output_dir as JSON
    output_path = os.path.join(output_dir, f"{config_data['control_id']}_oscal_component.json")
    with open(output_path, "w") as f:
        json.dump(parsed, f, indent=2)
    typer.echo(f"Generated OSCAL component written to {output_path}")

if __name__ == "__main__":
    app()
