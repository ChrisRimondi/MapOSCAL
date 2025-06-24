"""
Central logging configuration for MapOSCAL.
"""

import logging
import os
from pathlib import Path
import sys


def configure_logging():
    """Configure logging for the entire project."""
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path(os.getcwd()) / "logs"
        log_dir.mkdir(exist_ok=True)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Remove any existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")

        # File handler
        log_file = log_dir / "maposcal.log"
        print(
            f"Creating log file at: {log_file}", file=sys.stderr
        )  # Debug print to stderr
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(
            sys.stderr
        )  # Use stderr for console output
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Configure specific loggers
        loggers = [
            "maposcal",
            "maposcal.analyzer",
            "maposcal.embeddings",
            "maposcal.generator",
            "maposcal.llm",
        ]

        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
            # Prevent propagation to avoid duplicate logs
            logger.propagate = False

            # Add handlers to each logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        # Log that configuration is complete
        logging.info(f"Logging configured. Log file location: {log_file}")
        return True
    except Exception as e:
        print(f"Error configuring logging: {e}", file=sys.stderr)
        return False
