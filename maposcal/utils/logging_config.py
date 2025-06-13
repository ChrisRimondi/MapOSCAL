"""
Central logging configuration for MapOSCAL.
"""

import logging

def configure_logging():
    """Configure logging for the entire project."""
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("maposcal.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set all loggers to ERROR level
    for logger_name in [
        'maposcal',
        'maposcal.analyzer',
        'maposcal.embeddings',
        'maposcal.generator',
        'maposcal.llm'
    ]:
        logging.getLogger(logger_name).setLevel(logging.ERROR) 