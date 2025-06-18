# MapOSCAL

## TL;DR
Software must be accurately described for security and compliance purposes.  NIST's OSCAL appears to be the defined format of the immediate future, however industry adoption hasn't reached its potential.  This project makes OSCAL usable by providing automated discovery in an engineering-friendly CLI tool, which enables your security architects to be focused on the details, not the documentation generation!

## Overview

Cybersecurity, risk management, as well as regulatory compliance requirements all hinge on a method to accurately describe your system's working environment and configuration.  The purpose of this project is to assist the software industry in easily creating standardized software component definitions, specifically to further the interoperability of security and compliance requirements.  This takes place using the foundation of [Open Security Controls Assessment Language (OSCAL)](https://pages.nist.gov/OSCAL/) Framework developed by the National Institute of Standards and Technology (NIST).  

Creating and maintaining an OSCAL definition of your system/software is not a trivial task.  With OSCAL being a machine-readable format, it's usually accessed as JSON or XML, or using an programmatic SDK.  Some UI's exist to improve human interaction, however, it's still a tedious process that requires significant subject matter expertise for mundane tasks.  This project seeks to simplify that pain-point by providing an engineering-focused CLI interface that allows for the dynamic drafting of your OSCAL system defintion based on automated discovery techniques.  Released under the generous MIT License, its goal is to provide core discovery functionality to as wide an audience as possible.  Using the generated output, your system's SMEs (with their highly-valued time) load is shifted from weeks of creating tedious documentation to a more effecient review process of automatically-generated documentation.  Its goal and purpose is not to replace such individuals, but to enable them to serve where their expertise is most valuable, not drafting documentation.

### Generative AI and OSCAL Discovery

While extremely powerful, generative AI can be equally dangerous in producing false, hallucinatory results if not properly implemented with guardrails.  The benefits of using generative AI are only valuable when produced in a framework that allows its powerful pattern-recognition to be assured by non-generative methods.  In this open source project, pains have been taken to place guardrails at a high-level view of your application.  If there is project growth, in a future commercial version there is planned to be much more granular controls, moving from the application and file level, into functions, relationships, and other more granular aspects.

### Compliance Control Implementation Statements

Having an OSCAL-based system defintion is only half of the compliance battle.  To be truely effective that definition must be distilled into accurate implementation statements that are tied to one or more compliance frameworks.  In this open source implementation we have included a single control definition and mapping for example purposes.  If future growth occurs, more are desired to be offered as part of a future, commercial offering.

### Validation and Quality Assurance

MapOSCAL includes comprehensive validation and evaluation capabilities to ensure the quality and accuracy of generated OSCAL components:

- **Local Validation**: Fast, deterministic validation using Pydantic schemas for structural correctness
- **LLM-Assisted Fixes**: Intelligent fixing of complex issues that require understanding context
- **Quality Evaluation**: AI-powered assessment of control mapping quality and completeness
- **Comprehensive Reporting**: Detailed validation failures and evaluation results

### Future Growth

The industry is currently struggling to have a clean, clear, and actionable way to describe systems for security and compliance purposes.  Our view is that the ideal path forward to improve this problem space is two-fold:

1. **Foundational open source adoption** -  Having a wide-spread use of OSCAL across both commercial/propriatary as well as commonly-used open source projects is key to future, normalized usage and adoption.  With such service definitions an accurate, building-block approach can be achieved to accurately describe complex systems.  This movement grows everytime a project is defined in OSCAL and available for usage by others.

2. **Robust commercial support** - While this project is foundational and released as open source, requires significant investment in ongoing compliance-related content generation and maintenance.  As such, it is desirable to have commercial add-ons in the future to benefit users with turn-key compliance needs.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MapOSCAL.git
cd MapOSCAL
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install the package:
```bash
pip install -e .
```

For development, install with additional dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Configuration

Create a configuration file (e.g., `config.yaml`) with the following structure:
```yaml
title: "your_service_name"
description: "Description of your service"
repo_path: "/path/to/your/repository"
output_dir: ".oscalgen"
top_k: 5
catalog_path: "path/to/NIST_catalog.json"
profile_path: "path/to/NIST_profile.json"
max_critique_retries: 3  # Number of validation/fix attempts
```

### Commands

The tool provides three main commands:

1. **Analyze Repository**
```bash
maposcal analyze config.yaml
```
This command analyzes your repository and generates initial OSCAL component definitions.

2. **Generate OSCAL Component**
```bash
maposcal generate config.yaml
```
This command generates the final OSCAL component definitions based on the analysis and control mappings. It includes:
- Individual control validation with automatic fixes
- LLM-assisted resolution of complex issues
- Comprehensive validation reporting
- Generation of validation failure logs

3. **Evaluate OSCAL Component Quality**
```bash
maposcal evaluate path/to/implemented_requirements.json
```
This command evaluates the quality of existing OSCAL component definitions using AI-powered assessment:
- Scores each control on 4 quality dimensions (0-2 scale)
- Provides detailed justifications for scores
- Offers improvement recommendations
- Generates comprehensive evaluation reports

### Output Files

The tool generates several output files in the specified `output_dir`:

#### Generated Files
- `{service_prefix}_implemented_requirements.json` - Validated OSCAL component definitions
- `{service_prefix}_validation_failures.json` - Detailed validation failure information
- `{service_prefix}_unvalidated_requirements.json` - Requirements that failed validation

#### Evaluation Files
- `{filename}_evaluation_results.json` - Quality assessment results with scores and recommendations

### Validation Features

#### Local Validation (Fast & Deterministic)
- **Control Status Validation**: Ensures valid control-status values
- **Configuration Structure**: Validates control-configuration format and file extensions
- **OSCAL Structure**: Checks required fields and UUID formats
- **Cross-Reference Validation**: Ensures consistency between status and configuration

#### LLM-Assisted Fixes
- **Automatic Fixes**: Simple issues fixed automatically (file extensions, missing fields)
- **Intelligent Resolution**: Complex issues sent to LLM for context-aware fixing
- **Retry Logic**: Multiple attempts to resolve validation issues

#### Quality Evaluation
- **Status Alignment**: Is the control-status correct given the explanation and configuration?
- **Explanation Quality**: Is the control-explanation clear, accurate, and grounded?
- **Configuration Support**: Is the control-configuration specific, correct, and valid?
- **Overall Consistency**: Do all parts reinforce each other without contradiction?

### Example Workflow

1. Create a configuration file:
```yaml
title: "my_service"
description: "My security-critical service"
repo_path: "./my_service"
output_dir: ".oscalgen"
top_k: 5
catalog_path: "examples/NIST_SP-800-53_rev5_catalog.json"
profile_path: "examples/NIST_SP-800-53_rev5_HIGH-baseline_profile.json"
max_critique_retries: 3
```

2. Run the analysis:
```bash
maposcal analyze config.yaml
```

3. Generate the OSCAL component:
```bash
maposcal generate config.yaml
```

4. Evaluate the quality of generated components:
```bash
maposcal evaluate .oscalgen/abc123_implemented_requirements.json
```

## Project Structure

- `maposcal/` - Main package directory
  - `analyzer/` - Code analysis components
  - `generator/` - OSCAL generation components
    - `validation.py` - Comprehensive validation schemas and functions
  - `llm/` - Language model integration
    - `prompt_templates.py` - LLM prompt templates for generation and evaluation
  - `embeddings/` - Code embedding functionality
  - `utils/` - Utility functions
  - `cli.py` - Command-line interface with analyze, generate, and evaluate commands

- `tests/` - Test suite
- `examples/` - Example configurations and outputs
- `config/` - Configuration templates

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project uses:
- Black for code formatting
- Ruff for linting
- MyPy for type checking

Run the formatters:
```bash
black .
ruff check .
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure code style compliance
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
