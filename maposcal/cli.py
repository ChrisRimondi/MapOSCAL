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

@app.command()
def analyze(repo_path: str, output_dir: str = ".oscalgen"):
    analyzer = Analyzer(repo_path=repo_path, output_dir=output_dir)
    analyzer.run()

@app.command()
def generate(config: str = None, output_dir: str = ".oscalgen", top_k: int = 5):
    """Generate OSCAL component for control"""
    # Load the config file
    config_path = config or SAMPLE_CONFIG_PATH
    if not os.path.exists(config_path):
        typer.echo(f"Config file not found: {config_path}. Please create it or provide a valid config.")
        raise typer.Exit(code=1)
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
