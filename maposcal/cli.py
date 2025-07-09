"""
maposcal.cli
~~~~~~~~~~~~

Command-line interface for MapOSCAL.

This module provides the main CLI commands for analyzing repositories,
generating security overviews, creating OSCAL components, and evaluating existing components.

Commands:
- analyze: Analyze a repository and generate initial OSCAL definitions
- summarize: Generate comprehensive security overview of the service
- generate: Generate validated OSCAL components with comprehensive validation and security context
- evaluate: Evaluate the quality of existing OSCAL components using AI assessment

Key Features:
- Security overview integration for improved control mapping accuracy
- Comprehensive validation with automatic fixes and LLM-assisted resolution
- Quality evaluation with detailed scoring and recommendations
- Simplified file naming without service prefixes

The CLI uses Typer for command-line argument parsing and provides
comprehensive error handling, progress reporting, and output generation.
"""

import typer
from maposcal.analyzer.analyzer import Analyzer
import os
import yaml
import json
from maposcal import settings
from maposcal.generator.control_mapper import (
    map_control,
    parse_llm_response,
    get_relevant_chunks,
)
from maposcal.generator.profile_control_extractor import ProfileControlExtractor
from maposcal.embeddings import meta_store
from maposcal.generator.validation import (
    validate_unique_uuids,
    validate_control_status,
    validate_implemented_requirement,
)
from maposcal.llm.prompt_templates import (
    build_critique_prompt,
    build_revise_prompt,
    build_evaluate_prompt,
    build_service_overview_prompt,
)
from maposcal.llm.llm_handler import LLMHandler
import logging
from typing import List
from maposcal.utils.logging_config import configure_logging
from maposcal.utils.metadata import generate_metadata, inject_metadata_into_json, inject_metadata_into_markdown, extract_metadata_from_json, extract_metadata_from_markdown
import datetime

# Configure logging at module level
configure_logging()

logger = logging.getLogger(__name__)

app = typer.Typer()

SAMPLE_CONFIG_PATH = "sample_control_config.yaml"


def load_config(config_path: str = None) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file. If None, uses SAMPLE_CONFIG_PATH.

    Returns:
        dict: Configuration data loaded from the YAML file

    Raises:
        typer.Exit: If the config file doesn't exist
    """
    config_path = config_path or SAMPLE_CONFIG_PATH
    if not os.path.exists(config_path):
        typer.echo(
            f"Config file not found: {config_path}. Please create it or provide a valid config."
        )
        raise typer.Exit(code=1)
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    typer.echo(f"Loaded config: {config_data}")
    return config_data


def get_llm_config(config_data: dict, command: str) -> dict:
    """
    Get LLM configuration for a specific command.
    
    Args:
        config_data: The loaded configuration data
        command: The command being executed (analyze, summarize, generate, evaluate)
        
    Returns:
        dict: LLM configuration with provider and model
    """
    # Check if there's a global LLM config
    global_llm_config = config_data.get("llm", {})
    
    # Check if there's a command-specific LLM config
    command_llm_config = config_data.get("llm", {}).get(command, {})
    
    # Merge global and command-specific configs (command-specific takes precedence)
    llm_config = {**global_llm_config, **command_llm_config}
    
    # If no config provided, use defaults from settings
    if not llm_config:
        return settings.DEFAULT_LLM_CONFIGS.get(command, {"provider": "openai", "model": "gpt-4"})
    
    # Validate provider
    provider = llm_config.get("provider", "openai")
    if provider not in settings.LLM_PROVIDERS:
        typer.echo(f"Warning: Unsupported provider '{provider}'. Using 'openai' instead.")
        provider = "openai"
    
    # Get model (use default if not specified)
    model = llm_config.get("model", "gpt-4")
    
    return {"provider": provider, "model": model}


@app.command()
def analyze(config: str = typer.Argument(None, help="Path to the configuration file.")):
    """
    Analyze a repository using the provided configuration.

    This command performs the initial analysis of a code repository to:
    - Extract and embed code files
    - Generate semantic summaries
    - Create initial OSCAL component definitions

    The analysis results are stored in the specified output directory
    and serve as the foundation for the generate command.

    Configuration options:
    - config_extensions: List of file extensions to treat as configuration files (when auto_discover_config is True)
    - auto_discover_config: Whether to auto-discover by extension or use manual file list (default: True)
    - config_files: List of specific file paths to treat as configuration files (when auto_discover_config is False)
    """
    config_data = load_config(config)
    repo_path = config_data.get("repo_path")
    output_dir = config_data.get("output_dir", ".oscalgen")

    # Get configuration file settings
    config_extensions = config_data.get("config_extensions")
    auto_discover_config = config_data.get("auto_discover_config", True)
    config_files = config_data.get("config_files")
    
    # Get LLM configuration from config
    llm_config = get_llm_config(config_data, "analyze")

    analyzer = Analyzer(
        repo_path=repo_path,
        output_dir=output_dir,
        config_extensions=config_extensions,
        auto_discover_config=auto_discover_config,
        config_files=config_files,
        llm_config=llm_config,
    )
    analyzer.run()


@app.command()
def summarize(
    config: str = typer.Argument(None, help="Path to the configuration file.")
):
    """
    Generate a comprehensive security overview of the service.

    This command analyzes the repository and generates a detailed security summary that includes:
    - Service overview and architecture
    - Authentication and authorization mechanisms
    - Encryption and data protection measures
    - Audit logging and monitoring capabilities

    The summary provides a high-level security assessment based on the codebase analysis
    and serves as a foundation for understanding the service's security posture.
    """
    config_data = load_config(config)
    output_dir = config_data.get("output_dir", ".oscalgen")

    # Check if analysis has already been run
    meta_path = os.path.join(output_dir, "meta.json")
    summary_meta_path = os.path.join(output_dir, "summary_meta.json")

    if not os.path.exists(meta_path):
        typer.echo("Analysis files not found. Please run 'analyze' command first.")
        typer.echo(f"Expected file: {meta_path}")
        raise typer.Exit(code=1)

    if not os.path.exists(summary_meta_path):
        typer.echo(
            "Summary analysis files not found. Please run 'analyze' command first."
        )
        typer.echo(f"Expected file: {summary_meta_path}")
        raise typer.Exit(code=1)

    # Load the analysis data to create context
    context_parts = []

    security_query = "security authentication authorization encryption logging monitoring audit data protection"

    try:
        relevant_chunks = get_relevant_chunks(security_query, output_dir, top_k=50)

        for chunk in relevant_chunks:
            if chunk.get("content"):
                context_parts.append(f"File: {chunk.get('source_file', 'unknown')}")
                context_parts.append(f"Content: {chunk.get('content')}")
                context_parts.append("---")
            elif chunk.get("summary"):
                context_parts.append(
                    f"File Summary: {chunk.get('source_file', 'unknown')}"
                )
                context_parts.append(f"Summary: {chunk.get('summary')}")
                context_parts.append("---")
    except Exception as e:
        typer.echo(
            f"Warning: Could not retrieve relevant chunks using FAISS search: {e}"
        )
        typer.echo("Falling back to loading all chunks...")

        # Fallback: load all chunks if FAISS search fails
        chunks = meta_store.load_metadata(meta_path)
        for chunk in chunks:
            if chunk.get("content"):
                context_parts.append(f"File: {chunk.get('source_file', 'unknown')}")
                context_parts.append(f"Content: {chunk.get('content')}")
                context_parts.append("---")

        # Add file summaries
        summary_meta = meta_store.load_metadata(summary_meta_path)
        for file_path, summary_data in summary_meta.items():
            if summary_data.get("summary"):
                context_parts.append(f"File Summary: {file_path}")
                context_parts.append(f"Summary: {summary_data.get('summary')}")
                context_parts.append("---")

    context = "\n".join(context_parts)

    # Build the service overview prompt
    prompt = build_service_overview_prompt(context)

    # Get LLM configuration from config
    llm_config = get_llm_config(config_data, "summarize")
    
    # Generate metadata for this operation
    provider_config = settings.LLM_PROVIDERS[llm_config["provider"]]
    metadata = generate_metadata(
        model=llm_config["model"],
        provider=llm_config["provider"],
        base_url=provider_config["base_url"],
        command="summarize",
        config_file=config
    )
    
    # Query the LLM
    llm_handler = LLMHandler(provider=llm_config["provider"], model=llm_config["model"])
    typer.echo(f"Generating service security overview using {llm_config['provider']}/{llm_config['model']}...")
    response = llm_handler.query(prompt=prompt)

    # Inject metadata and save the markdown response to disk
    response_with_metadata = inject_metadata_into_markdown(response, metadata)
    summary_path = os.path.join(output_dir, "security_overview.md")
    with open(summary_path, "w") as f:
        f.write(response_with_metadata)

    typer.echo(f"Security overview written to: {summary_path}")


def critique_and_revise(
    implemented_requirements: List[dict],
    max_retries: int = 3,
    security_overview: str = None,
    llm_config: dict = None,
) -> List[dict]:
    """
    Critique and revise implemented requirements until valid or max retries reached.

    Args:
        implemented_requirements: List of implemented requirement dictionaries
        max_retries: Maximum number of critique-revise cycles
        security_overview: Optional security overview content to include as reference

    Returns:
        List of revised implemented requirements
    """
    # Use provided LLM config or fall back to defaults
    if llm_config:
        llm_handler = LLMHandler(provider=llm_config["provider"], model=llm_config["model"])
    else:
        llm_handler = LLMHandler(command="generate")

    for attempt in range(max_retries):
        # Critique the current requirements

        critique_prompt = build_critique_prompt(
            implemented_requirements, security_overview
        )
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
                        control_id = req.get("control_id")
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
                    if v.get("suggestion"):
                        logger.warning(f"    Suggestion: {v.get('suggestion')}")

        # If not valid, revise based on violations
        revise_prompt = build_revise_prompt(
            implemented_requirements, violations, security_overview
        )
        revise_response = llm_handler.query(prompt=revise_prompt)
        revised_requirements = parse_llm_response(revise_response)

        if isinstance(revised_requirements, list):
            implemented_requirements = revised_requirements
        else:
            logger.error(f"Invalid revise response format on attempt {attempt + 1}")

    logger.warning(f"Failed to achieve valid requirements after {max_retries} attempts")
    return implemented_requirements


@app.command()
def generate(
    config: str = typer.Argument(None, help="Path to the configuration file.")
):
    """
    Generate validated OSCAL components for controls using the provided configuration.

    This command performs the main OSCAL generation process with comprehensive validation:

    1. **Control Extraction**: Extracts controls from the specified profile and catalog
    2. **LLM Generation**: Generates initial OSCAL implementations for each control
    3. **Local Validation**: Validates each requirement using deterministic validation functions
    4. **Automatic Fixes**: Applies automatic fixes for common validation issues
    5. **LLM-Assisted Fixes**: Uses LLM for complex fixes that require understanding
    6. **Cross-Validation**: Validates UUID uniqueness across all requirements
    7. **Reporting**: Generates comprehensive validation reports and failure logs

    The command produces three main output files:
    - implemented_requirements.json: Validated OSCAL components
    - validation_failures.json: Detailed validation failure information
    - unvalidated_requirements.json: Requirements that failed validation
    """
    config_data = load_config(config)
    output_dir = config_data.get("output_dir", ".oscalgen")
    top_k = config_data.get("top_k", 5)
    max_critique_retries = config_data.get("max_critique_retries", 3)

    # Get catalog and profile paths from config
    catalog_path = config_data.get("catalog_path")
    profile_path = config_data.get("profile_path")

    if not catalog_path or not profile_path:
        typer.echo(
            "Both catalog_path and profile_path must be specified in the config."
        )
        raise typer.Exit(code=1)

    # Extract controls from profile using catalog
    extractor = ProfileControlExtractor(catalog_path, profile_path)

    # Get all controls from the profile
    controls_dict = {}
    for import_item in extractor.profile["profile"].get("imports", []):
        # Handle both direct control IDs and structured imports
        if isinstance(import_item, dict):
            # Handle structured imports with include-controls
            for include in import_item.get("include-controls", []):
                for control_id in include.get("with-ids", []):
                    control_data = extractor.extract_control_parameters(control_id)
                    if control_data:
                        controls_dict[control_id] = control_data
        else:
            # Handle direct control IDs
            control_data = extractor.extract_control_parameters(import_item)
            if control_data:
                controls_dict[import_item] = control_data

    typer.echo(f"Found {len(controls_dict)} controls to process")

    # Load security overview if available
    security_overview = None
    security_overview_path = os.path.join(output_dir, "security_overview.md")
    if os.path.exists(security_overview_path):
        try:
            with open(security_overview_path, "r") as f:
                security_overview = f.read().strip()
            typer.echo(f"Loaded security overview from {security_overview_path}")
        except Exception as e:
            typer.echo(f"Warning: Failed to load security overview: {e}")
    else:
        typer.echo(
            f"Security overview not found at {security_overview_path}. Run 'summarize' command first for better results."
        )

    # Get LLM configuration from config
    llm_config = get_llm_config(config_data, "generate")
    
    # Generate metadata for this operation
    provider_config = settings.LLM_PROVIDERS[llm_config["provider"]]
    metadata = generate_metadata(
        model=llm_config["model"],
        provider=llm_config["provider"],
        base_url=provider_config["base_url"],
        command="generate",
        config_file=config
    )
    
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
        result = map_control(control_data, output_dir, top_k, llm_config)

        # Parse the LLM response as JSON
        parsed = parse_llm_response(result)

        if not isinstance(parsed, dict):
            typer.echo(
                f"Warning: Invalid response format for control {control_id}. Skipping."
            )
            failed_controls.append((control_id, "Invalid response format"))
            continue

        # Add the control ID to the requirement
        parsed["control_id"] = control_id

        # Validate this individual requirement with comprehensive validation and fixing
        llm_handler = LLMHandler(provider=llm_config["provider"], model=llm_config["model"])
        is_valid = False
        final_validation_errors = []

        for attempt in range(max_critique_retries):
            # First, validate control-status using JSON parser
            control_status_valid, control_status_error = validate_control_status(parsed)
            if not control_status_valid:
                logger.warning(
                    f"Control-status validation failed for {control_id}: {control_status_error}"
                )
                # Try to fix control-status by setting a default value
                for prop in parsed.get("props", []):
                    if prop.get("name") == "control-status":
                        prop["value"] = (
                            "applicable and not satisfied"  # Default fallback
                        )
                        break
                else:
                    # Add control-status prop if it doesn't exist
                    parsed.setdefault("props", []).append(
                        {
                            "name": "control-status",
                            "value": "applicable and not satisfied",
                            "ns": "https://fedramp.gov/ns/oscal",
                        }
                    )

            # Use comprehensive validation instead of LLM critique
            requirement_valid, violations = validate_implemented_requirement(parsed)

            if requirement_valid:
                is_valid = True
                break

            # Log validation failures
            if violations:
                logger.warning(
                    f"Validation failures for control {control_id} on attempt {attempt + 1}:"
                )
                for v in violations:
                    logger.warning(f"  - {v.get('issue')} (at {v.get('field')})")
                    if v.get("suggestion"):
                        logger.warning(f"    Suggestion: {v.get('suggestion')}")

            # If not valid, try to fix common issues automatically first
            if violations and attempt < max_critique_retries - 1:
                # Try to fix some common issues automatically
                for violation in violations:
                    field = violation.get("field", "")
                    issue = violation.get("issue", "")

                    # Fix empty control-configuration when status contains configuration
                    if "control-configuration" in field and "non-empty" in issue:
                        for prop in parsed.get("props", []):
                            if prop.get("name") == "control-configuration":
                                if not prop.get("value") or (
                                    isinstance(prop.get("value"), list)
                                    and not prop.get("value")
                                ):
                                    # Set a default configuration or change status
                                    for status_prop in parsed.get("props", []):
                                        if status_prop.get("name") == "control-status":
                                            status_prop["value"] = (
                                                "applicable and not satisfied"
                                            )
                                            break
                                break

                    # Fix invalid file extensions
                    elif "file_path" in field and "Invalid file extension" in issue:
                        for prop in parsed.get("props", []):
                            if prop.get("name") == "control-configuration":
                                if isinstance(prop.get("value"), list):
                                    for config_obj in prop.get("value", []):
                                        if (
                                            isinstance(config_obj, dict)
                                            and "file_path" in config_obj
                                        ):
                                            # Change to a valid extension
                                            file_path = config_obj["file_path"]
                                            if file_path.endswith((".md", ".txt")):
                                                config_obj["file_path"] = "config.yaml"
                                break

                # If there are still violations after auto-fixes, use LLM to fix them
                requirement_valid_after_auto, violations_after_auto = (
                    validate_implemented_requirement(parsed)
                )
                if not requirement_valid_after_auto and violations_after_auto:
                    # Convert validation violations to LLM format
                    llm_violations = []
                    for v in violations_after_auto:
                        llm_violations.append(
                            {
                                "path": v.get("field", "unknown"),
                                "issue": v.get("issue", "Unknown validation error"),
                                "suggestion": v.get("suggestion", ""),
                            }
                        )

                    # Use LLM to fix remaining issues
                    revise_prompt = build_revise_prompt(
                        [parsed], llm_violations, security_overview
                    )
                    revise_response = llm_handler.query(prompt=revise_prompt)
                    revised_requirement = parse_llm_response(revise_response)

                    if (
                        isinstance(revised_requirement, list)
                        and len(revised_requirement) == 1
                    ):
                        parsed = revised_requirement[0]
                        parsed["control_id"] = (
                            control_id  # Ensure control_id is preserved
                        )
                    else:
                        logger.error(
                            f"Invalid revise response format for control {control_id} on attempt {attempt + 1}"
                        )

        if is_valid:
            implemented_requirements.append(parsed)
            typer.echo(
                f"Successfully validated and added requirement for control {control_id}"
            )
        else:
            # Capture the final validation errors that couldn't be fixed
            _, final_violations = validate_implemented_requirement(parsed)
            final_validation_errors = final_violations

            failed_controls.append(
                (
                    control_id,
                    f"Failed validation after {max_critique_retries} attempts",
                    final_validation_errors,
                )
            )
            unvalidated_requirements.append(parsed)
            typer.echo(
                f"Warning: Failed to validate requirement for control {control_id} after {max_critique_retries} attempts"
            )

    # Validate unique UUIDs across all requirements
    is_valid, error_msg = validate_unique_uuids(implemented_requirements)
    if not is_valid:
        logger.error(f"Duplicate UUIDs found in final output: {error_msg}")
        typer.echo(f"Warning: {error_msg}")
        final_validation_failures.append(
            {
                "type": "duplicate_uuids",
                "error": error_msg,
                "timestamp": str(datetime.datetime.now()),
            }
        )

    # Write validation failures to JSON file (combining individual and final failures)
    all_failures = []

    # Add individual control failures
    for control_id, reason, details in failed_controls:
        all_failures.append(
            {
                "control_id": control_id,
                "reason": reason,
                "type": "individual_validation",
                "timestamp": str(datetime.datetime.now()),
                "details": details,
            }
        )

    # Add final validation failures
    all_failures.extend(final_validation_failures)

    if all_failures:
        validation_failures = {"failed_controls": all_failures}
        validation_failures_with_metadata = inject_metadata_into_json(validation_failures, metadata)
        failures_path = os.path.join(output_dir, "validation_failures.json")
        with open(failures_path, "w") as f:
            json.dump(validation_failures_with_metadata, f, indent=2)
        typer.echo(f"Validation failures written to {failures_path}")

    # Write unvalidated requirements to JSON file
    if unvalidated_requirements:
        unvalidated_data = {"unvalidated_requirements": unvalidated_requirements}
        unvalidated_data_with_metadata = inject_metadata_into_json(unvalidated_data, metadata)
        unvalidated_path = os.path.join(output_dir, "unvalidated_requirements.json")
        with open(unvalidated_path, "w") as f:
            json.dump(unvalidated_data_with_metadata, f, indent=2)
        typer.echo(f"Unvalidated requirements written to {unvalidated_path}")

    # Report on failed controls
    if failed_controls:
        typer.echo("\nFailed Controls:")
        for control_id, reason, details in failed_controls:
            typer.echo(f"- {control_id}: {reason}")
            for detail in details:
                typer.echo(f"  - {detail['field']}: {detail['issue']}")
                if detail["suggestion"]:
                    typer.echo(f"    Suggestion: {detail['suggestion']}")

    # Write all implemented requirements to a single JSON file
    output_data = {"implemented_requirements": implemented_requirements}
    output_data_with_metadata = inject_metadata_into_json(output_data, metadata)
    output_path = os.path.join(output_dir, "implemented_requirements.json")
    with open(output_path, "w") as f:
        json.dump(output_data_with_metadata, f, indent=2)
    typer.echo(f"Generated OSCAL component written to {output_path}")
    typer.echo(
        f"Successfully processed {len(implemented_requirements)} out of {len(controls_dict)} controls"
    )


@app.command()
def evaluate(config: str = typer.Argument(..., help="Path to the configuration file.")):
    """
    Evaluate the quality of existing OSCAL component definitions using AI-powered assessment.

    This command provides comprehensive quality evaluation of OSCAL implemented requirements:

    1. **Individual Control Evaluation**: Evaluates each control using AI assessment
    2. **Quality Scoring**: Scores each control on 4 dimensions (0-2 scale):
       - Status Alignment: Is the control-status correct given the explanation and configuration?
       - Explanation Quality: Is the control-explanation clear, accurate, and grounded?
       - Configuration Support: Is the control-configuration specific, correct, and valid?
       - Overall Consistency: Do all parts reinforce each other without contradiction?
    3. **Detailed Justifications**: Provides specific reasoning for each score
    4. **Improvement Recommendations**: Offers actionable suggestions for improvement
    5. **Comprehensive Reporting**: Generates detailed evaluation reports with statistics

    The command produces:
    - Console output with real-time evaluation progress
    - {filename}_evaluation_results.json: Detailed evaluation results with scores and recommendations
    - Summary statistics including average scores and success rates
    """
    # Load config to get output directory
    config_data = load_config(config)
    output_dir = config_data.get("output_dir", ".oscalgen")

    # Construct the path to implemented_requirements.json
    requirements_file = os.path.join(output_dir, "implemented_requirements.json")

    if not os.path.exists(requirements_file):
        typer.echo(f"Requirements file not found: {requirements_file}")
        typer.echo(
            "Please run 'generate' command first to create the implemented_requirements.json file."
        )
        raise typer.Exit(code=1)

    try:
        with open(requirements_file, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        typer.echo(f"Invalid JSON in requirements file: {e}")
        raise typer.Exit(code=1)

    implemented_requirements = data.get("implemented_requirements", [])
    if not implemented_requirements:
        typer.echo("No implemented_requirements found in the file.")
        raise typer.Exit(code=1)

    typer.echo(
        f"Evaluating {len(implemented_requirements)} implemented requirements..."
    )

    # Get LLM configuration from config
    llm_config = get_llm_config(config_data, "evaluate")
    
    # Generate metadata for this operation
    provider_config = settings.LLM_PROVIDERS[llm_config["provider"]]
    metadata = generate_metadata(
        model=llm_config["model"],
        provider=llm_config["provider"],
        base_url=provider_config["base_url"],
        command="evaluate",
        config_file=config
    )
    
    # Initialize LLM handler
    llm_handler = LLMHandler(provider=llm_config["provider"], model=llm_config["model"])
    typer.echo(f"Using {llm_config['provider']}/{llm_config['model']} for evaluation...")
    evaluation_results = []

    # Evaluate each requirement
    for requirement in implemented_requirements:
        control_id = requirement.get("control-id", "unknown")
        typer.echo(f"Evaluating control {control_id}...")

        # Build evaluation prompt
        evaluate_prompt = build_evaluate_prompt(requirement)

        # Query LLM for evaluation
        try:
            evaluation_response = llm_handler.query(prompt=evaluate_prompt)
            evaluation_result = parse_llm_response(evaluation_response)

            if isinstance(evaluation_result, dict):
                evaluation_results.append(evaluation_result)
                typer.echo(f"✅ Evaluation completed for {control_id}")
            else:
                typer.echo(f"❌ Invalid evaluation response format for {control_id}")
                evaluation_results.append(
                    {
                        "control-id": control_id,
                        "error": "Invalid evaluation response format",
                    }
                )

        except Exception as e:
            typer.echo(f"❌ Error evaluating {control_id}: {e}")
            evaluation_results.append({"control-id": control_id, "error": str(e)})

    # Write evaluation results
    base_name = "implemented_requirements"

    evaluation_output = {
        "evaluation_results": evaluation_results,
        "evaluation_timestamp": str(datetime.datetime.now()),
    }
    
    evaluation_output_with_metadata = inject_metadata_into_json(evaluation_output, metadata)

    output_path = os.path.join(output_dir, f"{base_name}_evaluation_results.json")
    with open(output_path, "w") as f:
        json.dump(evaluation_output_with_metadata, f, indent=2)

    typer.echo(f"📄 Evaluation results written to: {output_path}")

    # Summary
    valid_evaluations = [r for r in evaluation_results if "error" not in r]
    total_score = sum(r.get("total_score", 0) for r in valid_evaluations)
    avg_score = total_score / len(valid_evaluations) if valid_evaluations else 0

    typer.echo("\n📊 Evaluation Summary:")
    typer.echo(f"   Total controls evaluated: {len(evaluation_results)}")
    typer.echo(f"   Successful evaluations: {len(valid_evaluations)}")
    typer.echo(f"   Average total score: {avg_score:.1f}/8.0")


@app.command()
def metadata(file_path: str = typer.Argument(..., help="Path to the file to extract metadata from.")):
    """
    Extract and display metadata from a MapOSCAL output file.
    
    This command shows the generation information including model, provider,
    timing, and configuration used to create the file.
    """
    if not os.path.exists(file_path):
        typer.echo(f"File not found: {file_path}")
        raise typer.Exit(code=1)
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        metadata = {}
        
        # Try to extract metadata based on file type
        if file_path.endswith(".json"):
            try:
                data = json.loads(content)
                metadata = extract_metadata_from_json(data)
            except json.JSONDecodeError:
                typer.echo(f"Invalid JSON in file: {file_path}")
                raise typer.Exit(code=1)
        elif file_path.endswith(".md"):
            metadata = extract_metadata_from_markdown(content)
        else:
            typer.echo(f"Unsupported file type: {file_path}")
            typer.echo("Supported types: .json, .md")
            raise typer.Exit(code=1)
        
        if not metadata:
            typer.echo("No metadata found in file.")
            return
        
        typer.echo("📋 File Metadata:")
        generation_info = metadata.get("generation_info", {})
        
        for key, value in generation_info.items():
            typer.echo(f"   {key}: {value}")
            
    except Exception as e:
        typer.echo(f"Error reading file: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
