"""
CLI command for executing MapOSCAL plans.

This module provides the `maposcal execute-plan` command that executes
generated execution plans with step-by-step processing.
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Optional, List

from ..execution import ExecutionPlan, ExecutionEngine
from ..utils.logging_config import configure_logging
import logging


def create_execute_plan_parser(subparsers) -> argparse.ArgumentParser:
    """Create the execute-plan command parser.
    
    Args:
        subparsers: Subparsers object from main CLI
        
    Returns:
        Configured argument parser for the execute-plan command
    """
    execute_parser = subparsers.add_parser(
        'execute-plan',
        help='Execute a generated MapOSCAL execution plan'
    )
    
    execute_parser.add_argument(
        'plan_file',
        help='Path to the execution plan YAML file'
    )
    
    execute_parser.add_argument(
        '--force',
        action='store_true',
        help='Force execution even if cached results exist'
    )
    
    execute_parser.add_argument(
        '--only-steps',
        help='Comma-separated list of step IDs to execute (e.g., render,inventory)'
    )
    
    execute_parser.add_argument(
        '--skip-steps',
        help='Comma-separated list of step IDs to skip (e.g., sbom,provenance)'
    )
    
    execute_parser.add_argument(
        '--only-targets',
        help='Comma-separated list of targets to execute (e.g., workload:frontend)'
    )
    
    execute_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return execute_parser


def execute_plan_command(args) -> int:
    """Execute the execute-plan command.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Setup logging
    configure_logging()
    logger = logging.getLogger(__name__)
    
    plan_file = Path(args.plan_file)
    
    # Validate plan file
    if not plan_file.exists():
        logger.error(f"Plan file does not exist: {plan_file}")
        return 1
    
    if not plan_file.is_file():
        logger.error(f"Plan file is not a file: {plan_file}")
        return 1
    
    try:
        logger.info(f"Loading execution plan: {plan_file}")
        
        # Load the execution plan
        with open(plan_file, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        plan = ExecutionPlan.from_dict(plan_data)
        logger.info(f"Loaded plan for application: {plan.application}")
        
        # Parse step filters
        only_steps = None
        if args.only_steps:
            only_steps = [step.strip() for step in args.only_steps.split(',')]
            logger.info(f"Only executing steps: {only_steps}")
        
        skip_steps = None
        if args.skip_steps:
            skip_steps = [step.strip() for step in args.skip_steps.split(',')]
            logger.info(f"Skipping steps: {skip_steps}")
        
        # Parse target filters
        only_targets = None
        if args.only_targets:
            only_targets = [target.strip() for target in args.only_targets.split(',')]
            logger.info(f"Only executing targets: {only_targets}")
        
        # Create execution engine
        logger.info("Initializing execution engine...")
        engine = ExecutionEngine(
            plan=plan,
            force=args.force,
            only_steps=only_steps,
            skip_steps=skip_steps,
            only_targets=only_targets
        )
        
        # Get execution summary
        summary = engine.get_execution_summary()
        logger.info(f"Execution summary: {summary['total_steps']} total steps")
        
        # Execute the plan
        logger.info("Starting plan execution...")
        results = engine.execute()
        
        # Display results
        logger.info("Execution completed!")
        logger.info(f"  Total steps: {results['total_steps']}")
        logger.info(f"  Completed: {results['completed_steps']}")
        logger.info(f"  Failed: {results['failed_steps']}")
        logger.info(f"  Skipped: {results['skipped_steps']}")
        
        if results['failed_steps'] > 0:
            logger.warning("Some steps failed during execution")
            for step_id, step_result in results['step_results'].items():
                if 'error' in step_result:
                    logger.warning(f"  Step {step_id}: {step_result['error']}")
        
        # Display step results
        if args.verbose:
            logger.info("Step results:")
            for step_id, step_result in results['step_results'].items():
                if 'error' in step_result:
                    logger.info(f"  {step_id}: ❌ {step_result['error']}")
                else:
                    logger.info(f"  {step_id}: ✅ {step_result.get('message', 'Completed')}")
        
        return 0 if results['failed_steps'] == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed to execute plan: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


def main():
    """Main entry point for the execute-plan command."""
    parser = argparse.ArgumentParser(
        description='Execute a generated MapOSCAL execution plan'
    )
    
    parser.add_argument(
        'plan_file',
        help='Path to the execution plan YAML file'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force execution even if cached results exist'
    )
    
    parser.add_argument(
        '--only-steps',
        help='Comma-separated list of step IDs to execute (e.g., render,inventory)'
    )
    
    parser.add_argument(
        '--skip-steps',
        help='Comma-separated list of step IDs to skip (e.g., sbom,provenance)'
    )
    
    parser.add_argument(
        '--only-targets',
        help='Comma-separated list of targets to execute (e.g., workload:frontend)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    return execute_plan_command(args)


if __name__ == '__main__':
    sys.exit(main())
