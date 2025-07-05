"""
Control hints enumerator module.

This module provides functionality to enumerate all control hints from the control_hints.py file,
both generic and language-specific, for use by language inspectors.
"""

import inspect
import re
from typing import Dict, List, Tuple, Optional
import maposcal.utils.control_hints as control_hints
import logging

logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = ['python', 'golang', 'java', 'cpp']

# Pattern to extract control ID from variable names
CONTROL_ID_PATTERN = re.compile(r'^([a-z]+\d+(?:\.\d+)?)$', re.IGNORECASE)


def get_all_control_hints() -> Dict[str, Dict[str, List[str]]]:
    """
    Enumerate all control hints from the control_hints module.
    
    Returns:
        Dict mapping control IDs to their generic and language-specific hints.
        Format: {
            'control_id': {
                'generic': [list_of_generic_hints],
                'python': [list_of_python_hints],
                'golang': [list_of_golang_hints],
                'java': [list_of_java_hints],
                'cpp': [list_of_cpp_hints]
            }
        }
    """
    control_hints_dict = {}
    
    # Get all attributes from the control_hints module
    for attr_name, attr_value in inspect.getmembers(control_hints):
        # Skip private attributes and non-list attributes
        if attr_name.startswith('_') or not isinstance(attr_value, list):
            continue
            
        # Check if this is a control ID (generic hints)
        control_match = CONTROL_ID_PATTERN.match(attr_name)
        if control_match:
            control_id = control_match.group(1)
            if control_id not in control_hints_dict:
                control_hints_dict[control_id] = {
                    'generic': [],
                    'python': [],
                    'golang': [],
                    'java': [],
                    'cpp': []
                }
            control_hints_dict[control_id]['generic'] = attr_value
            logger.debug(f"Found generic hints for control {control_id}: {len(attr_value)} hints")
            
        # Check if this is a language-specific control (e.g., ac10_python)
        for lang in SUPPORTED_LANGUAGES:
            lang_pattern = f'_{lang}$'
            if re.search(lang_pattern, attr_name):
                # Extract the base control ID
                base_control = attr_name[:-len(f'_{lang}')]  # Remove _python, _golang, etc.
                control_match = CONTROL_ID_PATTERN.match(base_control)
                if control_match:
                    control_id = control_match.group(1)
                    if control_id not in control_hints_dict:
                        control_hints_dict[control_id] = {
                            'generic': [],
                            'python': [],
                            'golang': [],
                            'java': [],
                            'cpp': []
                        }
                    control_hints_dict[control_id][lang] = attr_value
                    logger.debug(f"Found {lang} hints for control {control_id}: {len(attr_value)} hints")
    
    logger.info(f"Enumerated {len(control_hints_dict)} controls with hints")
    return control_hints_dict


def get_control_hints_for_language(language: str) -> Dict[str, List[str]]:
    """
    Get all control hints for a specific language.
    
    Args:
        language (str): The language to get hints for ('python', 'golang', 'java', 'cpp')
        
    Returns:
        Dict mapping control IDs to their hints for the specified language.
        Format: {'control_id': [list_of_hints]}
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}. Supported languages: {SUPPORTED_LANGUAGES}")
    
    all_hints = get_all_control_hints()
    language_hints = {}
    
    for control_id, hints_dict in all_hints.items():
        # Include both generic and language-specific hints
        combined_hints = hints_dict['generic'] + hints_dict[language]
        if combined_hints:
            language_hints[control_id] = combined_hints
    
    logger.info(f"Retrieved {len(language_hints)} controls with {language} hints")
    return language_hints


def search_control_hints_in_content(file_contents: str, language: str) -> List[str]:
    """
    Search for control hints in file contents for a specific language.
    
    Args:
        file_contents (str): The contents of the file to search
        language (str): The language to search for ('python', 'golang', 'java', 'cpp')
        
    Returns:
        List of control IDs that were found in the content
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}. Supported languages: {SUPPORTED_LANGUAGES}")
    
    found_controls = []
    language_hints = get_control_hints_for_language(language)
    
    # Parse file contents into words for searching
    file_words = set(file_contents.lower().split())
    
    for control_id, hints in language_hints.items():
        for hint in hints:
            # Clean the hint (remove comments and extra whitespace)
            clean_hint = hint.split('#')[0].strip().lower()
            if clean_hint and clean_hint in file_words:
                logger.info(f"Found control {control_id} based on hint: {clean_hint}")
                found_controls.append(control_id)
                break  # One match is enough for this control
    
    logger.info(f"Found {len(found_controls)} applicable controls in {language} content")
    return found_controls


def get_control_hints_summary() -> Dict[str, Dict[str, int]]:
    """
    Get a summary of all available control hints.
    
    Returns:
        Dict with control IDs and counts of hints for each language
        Format: {
            'control_id': {
                'generic': count,
                'python': count,
                'golang': count,
                'java': count,
                'cpp': count
            }
        }
    """
    all_hints = get_all_control_hints()
    summary = {}
    
    for control_id, hints_dict in all_hints.items():
        summary[control_id] = {
            'generic': len(hints_dict['generic']),
            'python': len(hints_dict['python']),
            'golang': len(hints_dict['golang']),
            'java': len(hints_dict['java']),
            'cpp': len(hints_dict['cpp'])
        }
    
    return summary


# Legacy compatibility function
def control_hints_strings_search(file_contents: str, search_strings: List[str], control_name: str) -> bool:
    """
    Legacy compatibility function that maintains the same interface as the original.
    
    Args:
        file_contents (str): The contents of a file to search
        search_strings (list): A list of strings to search for
        control_name (str): The control name (e.g., 'SC-8')
        
    Returns:
        bool: True if any hints were found, False otherwise
    """
    # Parse file contents into words
    file_words = set(file_contents.lower().split())
    
    for hint in search_strings:
        clean_hint = hint.split('#')[0].strip().lower()
        if clean_hint and clean_hint in file_words:
            logger.info(f"Found control {control_name} based on hint: {clean_hint}")
            return True
    
    return False 