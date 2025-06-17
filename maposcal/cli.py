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
from maposcal.llm.prompt_templates import build_critique_prompt, build_revise_prompt
from maposcal.llm.llm_handler import LLMHandler
import logging
from typing import List
from maposcal.utils.logging_config import configure_logging

# Configure logging at module level
configure_logging()

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

def critique_and_revise(implemented_requirements: List[dict], max_retries: int = 3) -> List[dict]:
    """
    Critique and revise implemented requirements until valid or max retries reached.
    
    Args:
        implemented_requirements: List of implemented requirement dictionaries
        max_retries: Maximum number of critique-revise cycles
        
    Returns:
        List of revised implemented requirements
    """
    llm_handler = LLMHandler()
    
    for attempt in range(max_retries):
        # Critique the current requirements
        critique_prompt = build_critique_prompt(implemented_requirements)
        critique_response = llm_handler.query(prompt=critique_prompt)
        critique_result = parse_llm_response(critique_response)
        
        if not isinstance(critique_result, dict):
            logger.error(f"Invalid critique response format on attempt {attempt + 1}")
            continue
            
        if critique_result.get("valid", False):
            return implemented_requirements
            
        # Log validation failures
        violations = critique_result.get("violations", [])
        if violations:
            logger.warning(f"Validation failures on attempt {attempt + 1}:")
            # Group violations by control ID
            violations_by_control = {}
            for violation in violations:
                # Extract control ID from the JSONPath
                path = violation.get("path", "")
                control_id = None
                for req in implemented_requirements:
                    if f"$[{req.get('control_id')}]" in path:
                        control_id = req.get('control_id')
                        break
                
                if control_id:
                    if control_id not in violations_by_control:
                        violations_by_control[control_id] = []
                    violations_by_control[control_id].append(violation)
            
            # Log violations grouped by control
            for control_id, control_violations in violations_by_control.items():
                logger.warning(f"Control {control_id} violations:")
                for v in control_violations:
                    logger.warning(f"  - {v.get('issue')} (at {v.get('path')})")
                    if v.get('suggestion'):
                        logger.warning(f"    Suggestion: {v.get('suggestion')}")
            
        # If not valid, revise based on violations
        revise_prompt = build_revise_prompt(implemented_requirements, violations)
        revise_response = llm_handler.query(prompt=revise_prompt)
        revised_requirements = parse_llm_response(revise_response)
        
        if isinstance(revised_requirements, list):
            implemented_requirements = revised_requirements
        else:
            logger.error(f"Invalid revise response format on attempt {attempt + 1}")
            
    logger.warning(f"Failed to achieve valid requirements after {max_retries} attempts")
    return implemented_requirements

@app.command()
def generate(config: str = typer.Argument(None, help="Path to the configuration file.")):
    """Generate OSCAL component for control using the provided configuration."""
    config_data = load_config(config)
    output_dir = config_data.get("output_dir", ".oscalgen")
    top_k = config_data.get("top_k", 5)
    title = config_data.get("title", "")
    service_prefix = hashlib.md5(title.encode()).hexdigest()[:6]
    max_critique_retries = config_data.get("max_critique_retries", 3)
    
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

    # Run critique-revise loop on the entire set of requirements
    implemented_requirements = critique_and_revise(implemented_requirements, max_critique_retries)

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
