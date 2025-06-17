import typer
from maposcal.analyzer.analyzer import Analyzer
import os
import yaml
import json
from maposcal.generator.control_mapper import map_control, parse_llm_response
from maposcal.generator.profile_control_extractor import ProfileControlExtractor
from maposcal.embeddings import faiss_index, meta_store, local_embedder
from pathlib import Path
import re
import hashlib
from maposcal.generator.validation import validate_unique_uuids
import logging

logger = logging.getLogger(__name__)

app = typer.Typer()

SAMPLE_CONFIG_PATH = "sample_control_config.yaml"

def load_config(config_path: str = None) -> dict:
    """Load configuration from a YAML file."""
    config_path = config_path or SAMPLE_CONFIG_PATH
    if not os.path.exists(config_path):
        typer.echo(f"Config file not found: {config_path}. Please create it or provide a valid config.")
        raise typer.Exit(code=1)
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    typer.echo(f"Loaded config: {config_data}")
    return config_data

@app.command()
def analyze(config: str = typer.Argument(None, help="Path to the configuration file.")):
    """Analyze a repository using the provided configuration."""
    config_data = load_config(config)
    repo_path = config_data.get("repo_path")
    output_dir = config_data.get("output_dir", ".oscalgen")
    title = config_data.get("title", "")
    service_prefix = hashlib.md5(title.encode()).hexdigest()[:6]

    analyzer = Analyzer(repo_path=repo_path, output_dir=output_dir, service_prefix=service_prefix)
    analyzer.run()

@app.command()
def generate(config: str = typer.Argument(None, help="Path to the configuration file.")):
    """Generate OSCAL component for control using the provided configuration."""
    config_data = load_config(config)
    output_dir = config_data.get("output_dir", ".oscalgen")
    top_k = config_data.get("top_k", 5)
    title = config_data.get("title", "")
    service_prefix = hashlib.md5(title.encode()).hexdigest()[:6]
    
    # Get catalog and profile paths from config
    catalog_path = config_data.get("catalog_path")
    profile_path = config_data.get("profile_path")
    
    if not catalog_path or not profile_path:
        typer.echo("Both catalog_path and profile_path must be specified in the config.")
        raise typer.Exit(code=1)
        
    # Extract controls from profile using catalog
    extractor = ProfileControlExtractor(catalog_path, profile_path)
    
    # Get all controls from the profile
    controls_dict = {}
    for import_item in extractor.profile['profile'].get('imports', []):
        # Handle both direct control IDs and structured imports
        if isinstance(import_item, dict):
            # Handle structured imports with include-controls
            for include in import_item.get('include-controls', []):
                for control_id in include.get('with-ids', []):
                    control_data = extractor.extract_control_parameters(control_id)
                    if control_data:
                        controls_dict[control_id] = control_data
        else:
            # Handle direct control IDs
            control_data = extractor.extract_control_parameters(import_item)
            if control_data:
                controls_dict[import_item] = control_data
    
    typer.echo(f"Found {len(controls_dict)} controls to process")
    
    # Process each control and collect implemented requirements
    implemented_requirements = []
    for control_id, control_data in controls_dict.items():
        if not control_data:
            typer.echo(f"Missing control data for {control_id}. Skipping.")
            continue

        # Call map_control with the control dictionary
        result = map_control(
            control_data,
            output_dir,
            top_k,
            service_prefix
        )

        # Parse the LLM response as JSON
        parsed = parse_llm_response(result)
        
        # Add the control ID to the requirement
        if isinstance(parsed, dict):
            parsed['control_id'] = control_id
            implemented_requirements.append(parsed)
        else:
            typer.echo(f"Warning: Invalid response format for control {control_id}. Skipping.")

    # Validate unique UUIDs across all requirements
    is_valid, error_msg = validate_unique_uuids(implemented_requirements)
    if not is_valid:
        logger.error(f"Duplicate UUIDs found in final output: {error_msg}")
        typer.echo(f"Warning: {error_msg}")

    # Write all implemented requirements to a single JSON file
    output_path = os.path.join(output_dir, f"{service_prefix}_implemented_requirements.json")
    with open(output_path, "w") as f:
        json.dump({"implemented_requirements": implemented_requirements}, f, indent=2)
    typer.echo(f"Generated OSCAL component written to {output_path}")

if __name__ == "__main__":
    app()
