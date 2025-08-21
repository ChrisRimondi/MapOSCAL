"""
CLI command for generating Argo CD execution plans.

This module provides the `maposcal plan` command that analyzes Argo CD
Application repositories and generates execution plans.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..argo import ArgoCDParser, ManifestProcessor, WorkloadGrouper
from ..execution import PlanGenerator
import logging
from ..utils.logging_config import configure_logging


def create_plan_parser(subparsers) -> argparse.ArgumentParser:
    """Create the plan command parser.
    
    Args:
        subparsers: Subparsers object from main CLI
        
    Returns:
        Configured argument parser for the plan command
    """
    plan_parser = subparsers.add_parser(
        'plan',
        help='Generate execution plan for Argo CD Application repository'
    )
    
    plan_parser.add_argument(
        'repo_path',
        help='Path to the repository containing Argo CD manifests'
    )
    
    plan_parser.add_argument(
        '-o', '--output',
        help='Output file for the execution plan (default: plan.yaml)',
        default='plan.yaml'
    )
    
    plan_parser.add_argument(
        '--minimal',
        action='store_true',
        help='Generate minimal plan with only essential steps enabled'
    )
    
    plan_parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate the generated plan without saving'
    )
    
    plan_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return plan_parser


def plan_command(args) -> int:
    """Execute the plan command.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Setup logging
    configure_logging()
    logger = logging.getLogger(__name__)
    
    repo_path = Path(args.repo_path)
    
    # Validate repository path
    if not repo_path.exists():
        logger.error(f"Repository path does not exist: {repo_path}")
        return 1
    
    if not repo_path.is_dir():
        logger.error(f"Repository path is not a directory: {repo_path}")
        return 1
    
    try:
        logger.info(f"Analyzing Argo CD Application repository: {repo_path}")
        
        # Step 1: Parse Argo CD Applications
        logger.info("Step 1: Parsing Argo CD Applications...")
        parser = ArgoCDParser(str(repo_path))
        applications = parser.parse_repository()
        
        if not applications:
            logger.warning("No Argo CD Applications found in repository")
            # Create a minimal plan anyway
            application_name = repo_path.name
        else:
            application_name = applications[0].name
            logger.info(f"Found {len(applications)} Argo CD Application(s)")
        
        # Step 2: Process manifests for each application
        logger.info("Step 2: Processing Kubernetes manifests...")
        manifest_processor = ManifestProcessor()
        all_manifests = []
        
        for app in applications:
            manifests = parser.process_application_manifests(app)
            all_manifests.extend(manifests)
            logger.info(f"  Application '{app.name}': {len(manifests)} manifests")
        
        if not all_manifests:
            logger.warning("No Kubernetes manifests found")
            # Create a minimal plan anyway
            processed_manifests = {
                "workloads": [],
                "services": [],
                "config_maps": [],
                "secrets": [],
                "other_resources": [],
                "summary": {
                    "total_workloads": 0,
                    "total_services": 0,
                    "total_config_maps": 0,
                    "total_secrets": 0,
                    "total_other_resources": 0,
                    "total_container_images": 0,
                    "workload_types": {},
                    "namespaces": []
                }
            }
        else:
            processed_manifests = manifest_processor.process_manifests(all_manifests)
            summary = processed_manifests["summary"]
            logger.info(f"  Total workloads: {summary['total_workloads']}")
            logger.info(f"  Total services: {summary['total_services']}")
            logger.info(f"  Total container images: {summary['total_container_images']}")
        
        # Step 3: Group workloads
        logger.info("Step 3: Grouping related resources...")
        workload_grouper = WorkloadGrouper()
        grouped_resources = workload_grouper.group_resources(processed_manifests)
        
        workload_groups = grouped_resources["workload_groups"]
        logger.info(f"  Created {len(workload_groups)} workload groups")
        
        # Step 4: Generate execution plan
        logger.info("Step 4: Generating execution plan...")
        plan_generator = PlanGenerator()
        
        if args.minimal:
            plan = plan_generator.create_minimal_plan(application_name, workload_groups)
            logger.info("  Generated minimal execution plan")
        else:
            plan = plan_generator.generate_plan(
                application_name, 
                workload_groups,
                grouped_resources.get("namespace_policies", {}),
                grouped_resources.get("standalone_resources", [])
            )
            logger.info("  Generated full execution plan")
        
        # Step 5: Validate plan
        logger.info("Step 5: Validating execution plan...")
        validation_result = plan_generator.validate_plan(plan)
        
        if not validation_result["valid"]:
            logger.error("Plan validation failed:")
            for error in validation_result["errors"]:
                logger.error(f"  ERROR: {error}")
            return 1
        
        if validation_result["warnings"]:
            logger.warning("Plan validation warnings:")
            for warning in validation_result["warnings"]:
                logger.warning(f"  WARNING: {warning}")
        
        logger.info("  Plan validation passed")
        
        # Step 6: Output plan
        if args.validate_only:
            logger.info("Validation only mode - plan not saved")
            logger.info("Plan structure:")
            logger.info(f"  Application: {plan.application}")
            logger.info(f"  Steps: {len(plan.steps)}")
            logger.info(f"  Workload targets: {len(plan.targets.get('workloads', []))}")
        else:
            output_path = Path(args.output)
            plan.save_to_file(str(output_path))
            logger.info(f"Execution plan saved to: {output_path}")
            
            # Display plan summary
            logger.info("\nPlan Summary:")
            logger.info(f"  Application: {plan.application}")
            logger.info(f"  Total steps: {len(plan.steps)}")
            logger.info(f"  Workload targets: {len(plan.targets.get('workloads', []))}")
            
            # Count total images
            total_images = 0
            for workload in plan.targets.get('workloads', []):
                total_images += len(workload.get('images', []))
            logger.info(f"  Container images: {total_images}")
        
        logger.info("Plan generation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to generate execution plan: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


def main():
    """Main entry point for the plan command."""
    parser = argparse.ArgumentParser(
        description='Generate execution plan for Argo CD Application repository'
    )
    
    parser.add_argument(
        'repo_path',
        help='Path to the repository containing Argo CD manifests'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for the execution plan (default: plan.yaml)',
        default='plan.yaml'
    )
    
    parser.add_argument(
        '--minimal',
        action='store_true',
        help='Generate minimal plan with only essential steps enabled'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate the generated plan without saving'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    return plan_command(args)


if __name__ == '__main__':
    sys.exit(main())
