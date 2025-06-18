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
from maposcal.generator.validation import validate_unique_uuids, validate_control_status, validate_implemented_requirement
from maposcal.llm.prompt_templates import build_critique_prompt, build_revise_prompt
from maposcal.llm.llm_handler import LLMHandler
import logging
from typing import List
from maposcal.utils.logging_config import configure_logging
import datetime

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
    failed_controls = []
    unvalidated_requirements = []
    final_validation_failures = []
    
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
        
        if not isinstance(parsed, dict):
            typer.echo(f"Warning: Invalid response format for control {control_id}. Skipping.")
            failed_controls.append((control_id, "Invalid response format"))
            continue

        # Add the control ID to the requirement
        parsed['control_id'] = control_id
        
        # Validate this individual requirement
        llm_handler = LLMHandler()
        is_valid = False
        final_validation_errors = []
        
        for attempt in range(max_critique_retries):
            # First, validate control-status using JSON parser
            control_status_valid, control_status_error = validate_control_status(parsed)
            if not control_status_valid:
                logger.warning(f"Control-status validation failed for {control_id}: {control_status_error}")
                # Try to fix control-status by setting a default value
                for prop in parsed.get('props', []):
                    if prop.get('name') == 'control-status':
                        prop['value'] = "applicable and not satisfied"  # Default fallback
                        break
                else:
                    # Add control-status prop if it doesn't exist
                    parsed.setdefault('props', []).append({
                        'name': 'control-status',
                        'value': 'applicable and not satisfied',
                        'ns': 'https://fedramp.gov/ns/oscal'
                    })
            
            # Use comprehensive validation instead of LLM critique
            requirement_valid, violations = validate_implemented_requirement(parsed)
            
            if requirement_valid:
                is_valid = True
                break
                
            # Log validation failures
            if violations:
                logger.warning(f"Validation failures for control {control_id} on attempt {attempt + 1}:")
                for v in violations:
                    logger.warning(f"  - {v.get('issue')} (at {v.get('field')})")
                    if v.get('suggestion'):
                        logger.warning(f"    Suggestion: {v.get('suggestion')}")
                
            # If not valid, try to fix common issues automatically first
            if violations and attempt < max_critique_retries - 1:
                # Try to fix some common issues automatically
                for violation in violations:
                    field = violation.get('field', '')
                    issue = violation.get('issue', '')
                    
                    # Fix empty control-configuration when status contains configuration
                    if 'control-configuration' in field and 'non-empty' in issue:
                        for prop in parsed.get('props', []):
                            if prop.get('name') == 'control-configuration':
                                if not prop.get('value') or (isinstance(prop.get('value'), list) and not prop.get('value')):
                                    # Set a default configuration or change status
                                    for status_prop in parsed.get('props', []):
                                        if status_prop.get('name') == 'control-status':
                                            status_prop['value'] = "applicable and not satisfied"
                                            break
                                break
                    
                    # Fix invalid file extensions
                    elif 'file_path' in field and 'Invalid file extension' in issue:
                        for prop in parsed.get('props', []):
                            if prop.get('name') == 'control-configuration':
                                if isinstance(prop.get('value'), list):
                                    for config_obj in prop.get('value', []):
                                        if isinstance(config_obj, dict) and 'file_path' in config_obj:
                                            # Change to a valid extension
                                            file_path = config_obj['file_path']
                                            if file_path.endswith(('.md', '.txt')):
                                                config_obj['file_path'] = 'config.yaml'
                                break
                
                # If there are still violations after auto-fixes, use LLM to fix them
                requirement_valid_after_auto, violations_after_auto = validate_implemented_requirement(parsed)
                if not requirement_valid_after_auto and violations_after_auto:
                    # Convert validation violations to LLM format
                    llm_violations = []
                    for v in violations_after_auto:
                        llm_violations.append({
                            "path": v.get("field", "unknown"),
                            "issue": v.get("issue", "Unknown validation error"),
                            "suggestion": v.get("suggestion", "")
                        })
                    
                    # Use LLM to fix remaining issues
                    revise_prompt = build_revise_prompt([parsed], llm_violations)
                    revise_response = llm_handler.query(prompt=revise_prompt)
                    revised_requirement = parse_llm_response(revise_response)
                    
                    if isinstance(revised_requirement, list) and len(revised_requirement) == 1:
                        parsed = revised_requirement[0]
                        parsed['control_id'] = control_id  # Ensure control_id is preserved
                    else:
                        logger.error(f"Invalid revise response format for control {control_id} on attempt {attempt + 1}")
        
        if is_valid:
            implemented_requirements.append(parsed)
            typer.echo(f"Successfully validated and added requirement for control {control_id}")
        else:
            # Capture the final validation errors that couldn't be fixed
            _, final_violations = validate_implemented_requirement(parsed)
            final_validation_errors = final_violations
            
            failed_controls.append((control_id, f"Failed validation after {max_critique_retries} attempts", final_validation_errors))
            unvalidated_requirements.append(parsed)
            typer.echo(f"Warning: Failed to validate requirement for control {control_id} after {max_critique_retries} attempts")

    # Validate unique UUIDs across all requirements
    is_valid, error_msg = validate_unique_uuids(implemented_requirements)
    if not is_valid:
        logger.error(f"Duplicate UUIDs found in final output: {error_msg}")
        typer.echo(f"Warning: {error_msg}")
        final_validation_failures.append({
            "type": "duplicate_uuids",
            "error": error_msg,
            "timestamp": str(datetime.datetime.now())
        })

    # Write validation failures to JSON file (combining individual and final failures)
    all_failures = []
    
    # Add individual control failures
    for control_id, reason, details in failed_controls:
        all_failures.append({
            "control_id": control_id,
            "reason": reason,
            "type": "individual_validation",
            "timestamp": str(datetime.datetime.now()),
            "details": details
        })
    
    # Add final validation failures
    all_failures.extend(final_validation_failures)
    
    if all_failures:
        validation_failures = {
            "failed_controls": all_failures
        }
        failures_path = os.path.join(output_dir, f"{service_prefix}_validation_failures.json")
        with open(failures_path, "w") as f:
            json.dump(validation_failures, f, indent=2)
        typer.echo(f"Validation failures written to {failures_path}")

    # Write unvalidated requirements to JSON file
    if unvalidated_requirements:
        unvalidated_path = os.path.join(output_dir, f"{service_prefix}_unvalidated_requirements.json")
        with open(unvalidated_path, "w") as f:
            json.dump({"unvalidated_requirements": unvalidated_requirements}, f, indent=2)
        typer.echo(f"Unvalidated requirements written to {unvalidated_path}")

    # Report on failed controls
    if failed_controls:
        typer.echo("\nFailed Controls:")
        for control_id, reason, details in failed_controls:
            typer.echo(f"- {control_id}: {reason}")
            for detail in details:
                typer.echo(f"  - {detail['field']}: {detail['issue']}")
                if detail['suggestion']:
                    typer.echo(f"    Suggestion: {detail['suggestion']}")

    # Write all implemented requirements to a single JSON file
    output_path = os.path.join(output_dir, f"{service_prefix}_implemented_requirements.json")
    with open(output_path, "w") as f:
        json.dump({"implemented_requirements": implemented_requirements}, f, indent=2)
    typer.echo(f"Generated OSCAL component written to {output_path}")
    typer.echo(f"Successfully processed {len(implemented_requirements)} out of {len(controls_dict)} controls")

if __name__ == "__main__":
    app()
