"""
CLI command for resuming interrupted MapOSCAL executions.

This module provides the `maposcal resume` command that continues
execution from where it left off after interruption.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..execution import ExecutionPlan, ExecutionEngine
from ..utils.logging_config import configure_logging
import logging


def create_resume_parser(subparsers) -> argparse.ArgumentParser:
    """Create the resume command parser.
    
    Args:
        subparsers: Subparsers object from main CLI
        
    Returns:
        Configured argument parser for the resume command
    """
    resume_parser = subparsers.add_parser(
        'resume',
        help='Resume an interrupted MapOSCAL execution'
    )
    
    resume_parser.add_argument(
        'plan_file',
        help='Path to the execution plan YAML file'
    )
    
    resume_parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-execution of failed steps'
    )
    
    resume_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return resume_parser


def resume_command(args) -> int:
    """Execute the resume command.
    
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
        logger.info(f"Resuming execution for plan: {plan_file}")
        
        # Load the execution plan
        with open(plan_file, 'r') as f:
            import yaml
            plan_data = yaml.safe_load(f)
        
        plan = ExecutionPlan.from_dict(plan_data)
        logger.info(f"Loaded plan for application: {plan.application}")
        
        # Create execution engine for resume
        logger.info("Initializing execution engine for resume...")
        engine = ExecutionEngine(
            plan=plan,
            force=args.force  # Use force to re-execute failed steps if requested
        )
        
        # Check if we can resume
        if not engine.state_manager.can_resume():
            logger.error("Cannot resume execution - no valid state found or all steps completed")
            return 1
        
        # Get execution summary
        summary = engine.get_execution_summary()
        logger.info(f"Resume summary: {summary['total_steps']} total steps")
        logger.info(f"  Completed: {summary['completed_steps']}")
        logger.info(f"  Failed: {summary['failed_steps']}")
        logger.info(f"  Pending: {summary['pending_steps']}")
        
        if args.force and summary['failed_steps'] > 0:
            logger.info("Force mode enabled - will re-execute failed steps")
        
        # Execute the plan (will resume from current state)
        logger.info("Resuming plan execution...")
        results = engine.execute()
        
        # Display results
        logger.info("Resume execution completed!")
        logger.info(f"  Total steps: {results['total_steps']}")
        logger.info(f"  Completed: {results['completed_steps']}")
        logger.info(f"  Failed: {results['failed_steps']}")
        logger.info(f"  Skipped: {results['skipped_steps']}")
        
        if results['failed_steps'] > 0:
            logger.warning("Some steps failed during resume execution")
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
        logger.error(f"Failed to resume execution: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


def main():
    """Main entry point for the resume command."""
    parser = argparse.ArgumentParser(
        description='Resume an interrupted MapOSCAL execution'
    )
    
    parser.add_argument(
        'plan_file',
        help='Path to the execution plan YAML file'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-execution of failed steps'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    return resume_command(args)


if __name__ == '__main__':
    sys.exit(main())
