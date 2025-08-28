"""
maposcal.cli
~~~~~~~~~~~~

Command-line interface for MapOSCAL.

This module provides the main CLI commands for analyzing repositories,
generating security overviews, creating OSCAL components, and evaluating existing components.

Commands:
- run-all: Execute the complete MapOSCAL workflow (analyze → summarize → generate → evaluate)
- analyze: Analyze a repository and generate initial OSCAL definitions
- summarize: Generate comprehensive security overview of the service
- generate: Generate validated OSCAL components with comprehensive validation and security context
- evaluate: Evaluate the quality of existing OSCAL components using AI assessment
- metadata: Extract and display metadata from MapOSCAL output files

Key Features:
- Complete workflow automation with the run-all command
- Security overview integration for improved control mapping accuracy
- Comprehensive validation with automatic fixes and LLM-assisted resolution
- Quality evaluation with detailed scoring and recommendations
- Simplified file naming without service prefixes
- Progress reporting and error handling throughout the pipeline

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
from maposcal.utils.metadata import (
    generate_metadata,
    inject_metadata_into_json,
    inject_metadata_into_markdown,
    extract_metadata_from_json,
    extract_metadata_from_markdown,
)
import datetime

# Configure logging at module level
configure_logging()

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="maposcal",
    help="MapOSCAL - Generate OSCAL components from code repositories",
    add_completion=False,
)

SAMPLE_CONFIG_PATH = "sample_control_config.yaml"


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        None, 
        "--version", 
        "-v", 
        help="Show version information and exit"
    ),
    ctx: typer.Context = typer.Option(None, hidden=True),
):
    """
    MapOSCAL - Generate OSCAL components from code repositories.
    
    MapOSCAL analyzes code repositories and generates Open Security Controls Assessment Language (OSCAL)
    component definitions. It provides a complete workflow from code analysis to validated OSCAL outputs.
    
    Commands:
    • analyze: Initial repository analysis and code embedding
    • summarize: Generate security overview for improved control mapping  
    • generate: Create validated OSCAL components with comprehensive validation
    • evaluate: Assess the quality of generated components
    • k8s-process: Process Kubernetes resource YAML files for OSCAL generation
    • run-all: Execute the complete workflow (analyze → summarize → generate → evaluate)
    • metadata: Extract and display metadata from MapOSCAL output files
    
    For detailed help on any command, use: maposcal <command> --help
    """
    if version:
        typer.echo("MapOSCAL - Generate OSCAL components from code repositories")
        # You can add actual version info here when available
        typer.echo("Version: Development")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


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
        dict: LLM configuration with provider, model, and temperature
    """
    # Check if there's a global LLM config
    global_llm_config = config_data.get("llm", {})

    # Check if there's a command-specific LLM config
    command_llm_config = config_data.get("llm", {}).get(command, {})

    # Merge global and command-specific configs (command-specific takes precedence)
    llm_config = {**global_llm_config, **command_llm_config}

    # If no config provided, use defaults from settings
    if not llm_config:
        return settings.DEFAULT_LLM_CONFIGS.get(
            command, {"provider": "openai", "model": "gpt-4", "temperature": 0.7}
        )

    # Validate provider
    provider = llm_config.get("provider", "openai")
    if provider not in settings.LLM_PROVIDERS:
        typer.echo(
            f"Warning: Unsupported provider '{provider}'. Using 'openai' instead."
        )
        provider = "openai"

    # Get model and temperature (use defaults if not specified)
    model = llm_config.get("model", "gpt-4")
    temperature = llm_config.get("temperature", settings.DEFAULT_LLM_CONFIGS.get(command, {}).get("temperature", 0.7))

    return {"provider": provider, "model": model, "temperature": temperature}


@app.command()
def analyze(config: str = typer.Argument(None, help="Path to the configuration file.")):
    """
    Analyze a repository and generate initial OSCAL definitions.
    
    Performs initial analysis of a code repository to extract and embed code files,
    generate semantic summaries, and create initial OSCAL component definitions.
    
    The analysis results are stored in the specified output directory and serve
    as the foundation for the generate command.
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
    config: str = typer.Argument(None, help="Path to the configuration file."),
):
    """
    Generate a comprehensive security overview of the service.
    
    Analyzes the repository and generates a detailed security summary including service
    overview, authentication/authorization mechanisms, encryption measures, and audit
    logging capabilities.
    
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
        config_file=config,
    )

    # Query the LLM
    llm_handler = LLMHandler(provider=llm_config["provider"], model=llm_config["model"])
    # Set custom temperature if specified
    if "temperature" in llm_config:
        llm_handler.default_temperature = llm_config["temperature"]
    typer.echo(
        f"Generating service security overview using {llm_config['provider']}/{llm_config['model']}..."
    )
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
        llm_handler = LLMHandler(
            provider=llm_config["provider"], 
            model=llm_config["model"]
        )
        # Set custom temperature if specified
        if "temperature" in llm_config:
            llm_handler.default_temperature = llm_config["temperature"]
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
    config: str = typer.Argument(None, help="Path to the configuration file."),
):
    """
    Generate validated OSCAL components for controls.
    
    Performs the main OSCAL generation process with comprehensive validation including
    control extraction, LLM generation, local validation, automatic fixes, and
    cross-validation for UUID uniqueness.
    
    Produces three main output files:
    • implemented_requirements.json: Validated OSCAL components
    • validation_failures.json: Detailed validation failure information  
    • unvalidated_requirements.json: Requirements that failed validation
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
        config_file=config,
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

        # The result is now a complete OSCAL control mapping dict
        if not isinstance(result, dict):
            typer.echo(
                f"Warning: Invalid response format for control {control_id}. Skipping."
            )
            failed_controls.append((control_id, "Invalid response format"))
            continue

        # Add the control ID to the requirement for tracking
        result["control_id"] = control_id

        # Validate this individual requirement with comprehensive validation and fixing
        llm_handler = LLMHandler(
            provider=llm_config["provider"], model=llm_config["model"]
        )
        # Set custom temperature if specified
        if "temperature" in llm_config:
            llm_handler.default_temperature = llm_config["temperature"]
        is_valid = False
        final_validation_errors = []

        for attempt in range(max_critique_retries):
            # Use comprehensive validation - the template ensures structural integrity
            requirement_valid, violations = validate_implemented_requirement(result)

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

            # If not valid and we have retries left, try to fix issues
            if violations and attempt < max_critique_retries - 1:
                # Convert validation violations to LLM format
                llm_violations = []
                for v in violations:
                    llm_violations.append(
                        {
                            "path": v.get("field", "unknown"),
                            "issue": v.get("issue", "Unknown validation error"),
                            "suggestion": v.get("suggestion", ""),
                        }
                    )

                # Use LLM to fix remaining issues
                revise_prompt = build_revise_prompt(
                    [result], llm_violations, security_overview
                )
                revise_response = llm_handler.query(prompt=revise_prompt)
                revised_requirement = parse_llm_response(revise_response)

                if (
                    isinstance(revised_requirement, list)
                    and len(revised_requirement) == 1
                ):
                    result = revised_requirement[0]
                    result["control_id"] = control_id  # Ensure control_id is preserved
                else:
                    logger.error(
                        f"Invalid revise response format for control {control_id} on attempt {attempt + 1}"
                    )

        if is_valid:
            implemented_requirements.append(result)
            typer.echo(
                f"Successfully validated and added requirement for control {control_id}"
            )
        else:
            # Capture the final validation errors that couldn't be fixed
            _, final_violations = validate_implemented_requirement(result)
            final_validation_errors = final_violations

            failed_controls.append(
                (
                    control_id,
                    f"Failed validation after {max_critique_retries} attempts",
                    final_validation_errors,
                )
            )
            unvalidated_requirements.append(result)
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
        validation_failures_with_metadata = inject_metadata_into_json(
            validation_failures, metadata
        )
        failures_path = os.path.join(output_dir, "validation_failures.json")
        with open(failures_path, "w") as f:
            json.dump(validation_failures_with_metadata, f, indent=2)
        typer.echo(f"Validation failures written to {failures_path}")

    # Write unvalidated requirements to JSON file
    if unvalidated_requirements:
        unvalidated_data = {"unvalidated_requirements": unvalidated_requirements}
        unvalidated_data_with_metadata = inject_metadata_into_json(
            unvalidated_data, metadata
        )
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
    Evaluate the quality of existing OSCAL component definitions.
    
    Provides comprehensive quality evaluation of OSCAL implemented requirements using
    AI-powered assessment with scoring on 4 dimensions: status alignment, explanation
    quality, configuration support, and overall consistency.
    
    Produces detailed evaluation reports with scores, recommendations, and summary
    statistics for quality improvement.
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
        config_file=config,
    )

    # Initialize LLM handler
    llm_handler = LLMHandler(provider=llm_config["provider"], model=llm_config["model"])
    # Set custom temperature if specified
    if "temperature" in llm_config:
        llm_handler.default_temperature = llm_config["temperature"]
    typer.echo(
        f"Using {llm_config['provider']}/{llm_config['model']} for evaluation..."
    )
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

    evaluation_output_with_metadata = inject_metadata_into_json(
        evaluation_output, metadata
    )

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
def k8s_process(config: str = typer.Argument(None, help="Path to the configuration file.")):
    """
    Process Kubernetes resource YAML files and generate initial OSCAL component definitions.
    
    Analyzes Kubernetes manifests to extract resource metadata, deployment
    configurations, and security-relevant information. Generates initial OSCAL component
    structures based on the K8s resource properties.
    
    The analysis results are stored in the specified output directory and serve
    as the foundation for further OSCAL generation and validation.
    """
    config_data = load_config(config)
    output_dir = config_data.get("output_dir", ".oscalgen")
    
    # Get K8s-specific configuration
    k8s_paths = config_data.get("k8s", {}).get("k8s_paths", [])
    
    if not k8s_paths:
        typer.echo("K8s paths not specified in configuration. Please add 'k8s_paths' to the 'k8s' section.")
        raise typer.Exit(code=1)
    
    # Validate that all specified paths exist
    for k8s_path in k8s_paths:
        if not os.path.exists(k8s_path):
            typer.echo(f"K8s directory not found: {k8s_path}")
            raise typer.Exit(code=1)
    
    # Get LLM configuration from config
    llm_config = get_llm_config(config_data, "k8s_process")
    
    typer.echo(f"Processing K8s resources from {len(k8s_paths)} directories:")
    for k8s_path in k8s_paths:
        typer.echo(f"  - {k8s_path}")
    typer.echo(f"Output directory: {output_dir}")
    
    # TODO: Implement K8s processing logic
    # This will be expanded in future steps
    typer.echo("K8s processing command initialized successfully")
    typer.echo("Processing logic will be implemented in future steps")


@app.command()
def metadata(
    file_path: str = typer.Argument(
        ..., help="Path to the file to extract metadata from."
    ),
):
    """
    Extract and display metadata from a MapOSCAL output file.
    
    Shows the generation information including model, provider, timing, and
    configuration used to create the file.
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


@app.command()
def run_all(config: str = typer.Argument(None, help="Path to the configuration file.")):
    """
    Run the complete MapOSCAL workflow: analyze, summarize, generate, and evaluate.
    
    Executes all four major commands in their proper sequence with progress updates
    and continues through the pipeline even if individual steps encounter non-critical issues.
    """
    config_data = load_config(config)
    output_dir = config_data.get("output_dir", ".oscalgen")

    typer.echo("🚀 Starting complete MapOSCAL workflow...")
    typer.echo(f"📁 Output directory: {output_dir}")
    typer.echo("=" * 60)

    # Step 1: Analyze
    typer.echo("\n📊 Step 1/4: Analyzing repository...")
    try:
        repo_path = config_data.get("repo_path")
        config_extensions = config_data.get("config_extensions")
        auto_discover_config = config_data.get("auto_discover_config", True)
        config_files = config_data.get("config_files")
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
        typer.echo("✅ Analysis completed successfully")
    except Exception as e:
        typer.echo(f"❌ Analysis failed: {e}")
        typer.echo("Cannot continue without analysis. Exiting.")
        raise typer.Exit(code=1)

    # Step 2: Summarize
    typer.echo("\n📝 Step 2/4: Generating security overview...")
    try:
        # Check if analysis files exist
        meta_path = os.path.join(output_dir, "meta.json")
        summary_meta_path = os.path.join(output_dir, "summary_meta.json")

        if not os.path.exists(meta_path) or not os.path.exists(summary_meta_path):
            typer.echo("⚠️  Analysis files not found. Skipping summarize step.")
        else:
            # Load the analysis data to create context
            context_parts = []
            security_query = "security authentication authorization encryption logging monitoring audit data protection"

            try:
                relevant_chunks = get_relevant_chunks(
                    security_query, output_dir, top_k=50
                )

                for chunk in relevant_chunks:
                    if chunk.get("content"):
                        context_parts.append(
                            f"File: {chunk.get('source_file', 'unknown')}"
                        )
                        context_parts.append(f"Content: {chunk.get('content')}")
                        context_parts.append("---")
                    elif chunk.get("summary"):
                        context_parts.append(
                            f"File Summary: {chunk.get('source_file', 'unknown')}"
                        )
                        context_parts.append(f"Summary: {chunk.get('summary')}")
                        context_parts.append("---")
            except Exception as e:
                typer.echo(f"⚠️  Could not retrieve relevant chunks: {e}")
                typer.echo("Falling back to loading all chunks...")

                # Fallback: load all chunks if FAISS search fails
                chunks = meta_store.load_metadata(meta_path)
                for chunk in chunks:
                    if chunk.get("content"):
                        context_parts.append(
                            f"File: {chunk.get('source_file', 'unknown')}"
                        )
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
            prompt = build_service_overview_prompt(context)

            llm_config = get_llm_config(config_data, "summarize")
            provider_config = settings.LLM_PROVIDERS[llm_config["provider"]]
            metadata = generate_metadata(
                model=llm_config["model"],
                provider=llm_config["provider"],
                base_url=provider_config["base_url"],
                command="summarize",
                config_file=config,
            )

            llm_handler = LLMHandler(
                provider=llm_config["provider"], model=llm_config["model"]
            )
            # Set custom temperature if specified
            if "temperature" in llm_config:
                llm_handler.default_temperature = llm_config["temperature"]
            typer.echo(
                f"Generating service security overview using {llm_config['provider']}/{llm_config['model']}..."
            )
            response = llm_handler.query(prompt=prompt)

            response_with_metadata = inject_metadata_into_markdown(response, metadata)
            summary_path = os.path.join(output_dir, "security_overview.md")
            with open(summary_path, "w") as f:
                f.write(response_with_metadata)

            typer.echo(f"✅ Security overview written to: {summary_path}")
    except Exception as e:
        typer.echo(f"❌ Summarize failed: {e}")
        typer.echo("⚠️  Continuing without security overview...")

    # Step 3: Generate
    typer.echo("\n🔧 Step 3/4: Generating OSCAL components...")
    try:
        top_k = config_data.get("top_k", 5)
        max_critique_retries = config_data.get("max_critique_retries", 3)

        catalog_path = config_data.get("catalog_path")
        profile_path = config_data.get("profile_path")

        if not catalog_path or not profile_path:
            typer.echo(
                "❌ Both catalog_path and profile_path must be specified in the config."
            )
            raise typer.Exit(code=1)

        # Extract controls from profile using catalog
        extractor = ProfileControlExtractor(catalog_path, profile_path)

        # Get all controls from the profile
        controls_dict = {}
        for import_item in extractor.profile["profile"].get("imports", []):
            if isinstance(import_item, dict):
                for include in import_item.get("include-controls", []):
                    for control_id in include.get("with-ids", []):
                        control_data = extractor.extract_control_parameters(control_id)
                        if control_data:
                            controls_dict[control_id] = control_data
            else:
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

        llm_config = get_llm_config(config_data, "generate")
        provider_config = settings.LLM_PROVIDERS[llm_config["provider"]]
        metadata = generate_metadata(
            model=llm_config["model"],
            provider=llm_config["provider"],
            base_url=provider_config["base_url"],
            command="generate",
            config_file=config,
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

            result = map_control(control_data, output_dir, top_k, llm_config)

            if not isinstance(result, dict):
                typer.echo(
                    f"Warning: Invalid response format for control {control_id}. Skipping."
                )
                failed_controls.append((control_id, "Invalid response format"))
                continue

            result["control_id"] = control_id

            # Validate this individual requirement
            llm_handler = LLMHandler(
                provider=llm_config["provider"], model=llm_config["model"]
            )
            # Set custom temperature if specified
            if "temperature" in llm_config:
                llm_handler.default_temperature = llm_config["temperature"]
            is_valid = False
            final_validation_errors = []

            for attempt in range(max_critique_retries):
                requirement_valid, violations = validate_implemented_requirement(result)

                if requirement_valid:
                    is_valid = True
                    break

                if violations and attempt < max_critique_retries - 1:
                    llm_violations = []
                    for v in violations:
                        llm_violations.append(
                            {
                                "path": v.get("field", "unknown"),
                                "issue": v.get("issue", "Unknown validation error"),
                                "suggestion": v.get("suggestion", ""),
                            }
                        )

                    revise_prompt = build_revise_prompt(
                        [result], llm_violations, security_overview
                    )
                    revise_response = llm_handler.query(prompt=revise_prompt)
                    revised_requirement = parse_llm_response(revise_response)

                    if (
                        isinstance(revised_requirement, list)
                        and len(revised_requirement) == 1
                    ):
                        result = revised_requirement[0]
                        result["control_id"] = control_id
                    else:
                        logger.error(
                            f"Invalid revise response format for control {control_id} on attempt {attempt + 1}"
                        )

            if is_valid:
                implemented_requirements.append(result)
                typer.echo(
                    f"✅ Successfully validated requirement for control {control_id}"
                )
            else:
                _, final_violations = validate_implemented_requirement(result)
                final_validation_errors = final_violations

                failed_controls.append(
                    (
                        control_id,
                        f"Failed validation after {max_critique_retries} attempts",
                        final_validation_errors,
                    )
                )
                unvalidated_requirements.append(result)
                typer.echo(
                    f"⚠️  Failed to validate requirement for control {control_id}"
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

        # Write validation failures
        all_failures = []
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
        all_failures.extend(final_validation_failures)

        if all_failures:
            validation_failures = {"failed_controls": all_failures}
            validation_failures_with_metadata = inject_metadata_into_json(
                validation_failures, metadata
            )
            failures_path = os.path.join(output_dir, "validation_failures.json")
            with open(failures_path, "w") as f:
                json.dump(validation_failures_with_metadata, f, indent=2)
            typer.echo(f"Validation failures written to {failures_path}")

        # Write unvalidated requirements
        if unvalidated_requirements:
            unvalidated_data = {"unvalidated_requirements": unvalidated_requirements}
            unvalidated_data_with_metadata = inject_metadata_into_json(
                unvalidated_data, metadata
            )
            unvalidated_path = os.path.join(output_dir, "unvalidated_requirements.json")
            with open(unvalidated_path, "w") as f:
                json.dump(unvalidated_data_with_metadata, f, indent=2)
            typer.echo(f"Unvalidated requirements written to {unvalidated_path}")

        # Write implemented requirements
        output_data = {"implemented_requirements": implemented_requirements}
        output_data_with_metadata = inject_metadata_into_json(output_data, metadata)
        output_path = os.path.join(output_dir, "implemented_requirements.json")
        with open(output_path, "w") as f:
            json.dump(output_data_with_metadata, f, indent=2)

        typer.echo(f"✅ Generated OSCAL components written to {output_path}")
        typer.echo(
            f"✅ Successfully processed {len(implemented_requirements)} out of {len(controls_dict)} controls"
        )

    except Exception as e:
        typer.echo(f"❌ Generate failed: {e}")
        typer.echo("Cannot continue without generated components. Exiting.")
        raise typer.Exit(code=1)

    # Step 4: Evaluate
    typer.echo("\n📊 Step 4/4: Evaluating generated components...")
    try:
        requirements_file = os.path.join(output_dir, "implemented_requirements.json")

        if not os.path.exists(requirements_file):
            typer.echo(f"❌ Requirements file not found: {requirements_file}")
            typer.echo("Cannot evaluate without generated components. Exiting.")
            raise typer.Exit(code=1)

        with open(requirements_file, "r") as f:
            data = json.load(f)

        implemented_requirements = data.get("implemented_requirements", [])
        if not implemented_requirements:
            typer.echo("❌ No implemented_requirements found in the file.")
            raise typer.Exit(code=1)

        typer.echo(
            f"Evaluating {len(implemented_requirements)} implemented requirements..."
        )

        llm_config = get_llm_config(config_data, "evaluate")
        provider_config = settings.LLM_PROVIDERS[llm_config["provider"]]
        metadata = generate_metadata(
            model=llm_config["model"],
            provider=llm_config["provider"],
            base_url=provider_config["base_url"],
            command="evaluate",
            config_file=config,
        )

        llm_handler = LLMHandler(
            provider=llm_config["provider"], model=llm_config["model"]
        )
        # Set custom temperature if specified
        if "temperature" in llm_config:
            llm_handler.default_temperature = llm_config["temperature"]
        typer.echo(
            f"Using {llm_config['provider']}/{llm_config['model']} for evaluation..."
        )
        evaluation_results = []

        # Evaluate each requirement
        for requirement in implemented_requirements:
            control_id = requirement.get("control-id", "unknown")
            typer.echo(f"Evaluating control {control_id}...")

            evaluate_prompt = build_evaluate_prompt(requirement)

            try:
                evaluation_response = llm_handler.query(prompt=evaluate_prompt)
                evaluation_result = parse_llm_response(evaluation_response)

                if isinstance(evaluation_result, dict):
                    evaluation_results.append(evaluation_result)
                    typer.echo(f"✅ Evaluation completed for {control_id}")
                else:
                    typer.echo(
                        f"❌ Invalid evaluation response format for {control_id}"
                    )
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

        evaluation_output_with_metadata = inject_metadata_into_json(
            evaluation_output, metadata
        )
        output_path = os.path.join(output_dir, f"{base_name}_evaluation_results.json")
        with open(output_path, "w") as f:
            json.dump(evaluation_output_with_metadata, f, indent=2)

        typer.echo(f"✅ Evaluation results written to: {output_path}")

        # Summary
        valid_evaluations = [r for r in evaluation_results if "error" not in r]
        total_score = sum(r.get("total_score", 0) for r in valid_evaluations)
        avg_score = total_score / len(valid_evaluations) if valid_evaluations else 0

        typer.echo(
            f"✅ Evaluation completed: {len(valid_evaluations)}/{len(evaluation_results)} successful"
        )
        typer.echo(f"📊 Average total score: {avg_score:.1f}/8.0")

    except Exception as e:
        typer.echo(f"❌ Evaluate failed: {e}")
        typer.echo("⚠️  Continuing without evaluation...")

    # Final summary
    typer.echo("\n" + "=" * 60)
    typer.echo("🎉 MapOSCAL workflow completed!")
    typer.echo(f"📁 All outputs saved to: {output_dir}")
    typer.echo("\nGenerated files:")

    files_to_check = [
        "meta.json",
        "summary_meta.json",
        "security_overview.md",
        "implemented_requirements.json",
        "validation_failures.json",
        "unvalidated_requirements.json",
        "implemented_requirements_evaluation_results.json",
    ]

    for filename in files_to_check:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            typer.echo(f"  ✅ {filename}")
        else:
            typer.echo(f"  ❌ {filename} (not generated)")

    typer.echo(
        "\n🚀 Workflow complete! Review the generated files for your OSCAL components."
    )


if __name__ == "__main__":
    app()
