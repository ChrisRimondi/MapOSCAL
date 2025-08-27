"""
Control hints enumerator module.

This module provides functionality to enumerate all control hints from the control_hints.py and control_hints_k8s.py files,
both generic and language-specific, for use by language inspectors.
"""

import inspect
import re
from typing import Dict, List, Tuple
import maposcal.utils.control_hints as control_hints
import maposcal.utils.control_hints_k8s as control_hints_k8s
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = ["python", "golang", "java", "cpp", "kubernetes"]

# Pattern to extract control ID from variable names
CONTROL_ID_PATTERN = re.compile(r"^([a-z]+\d+(?:\.\d+)?)$", re.IGNORECASE)

# Configuration for enhanced search
SEARCH_CONFIG = {
    "exact_match_threshold": 1.0,      # Perfect match
    "fuzzy_match_threshold": 0.8,      # High similarity threshold
    "partial_match_threshold": 0.6,    # Partial match threshold
    "max_fuzzy_matches": 3,            # Maximum fuzzy matches per control
    "enable_fuzzy_matching": True,     # Enable fuzzy matching
    "enable_pattern_matching": True,   # Enable pattern matching
    "enable_partial_matching": True,   # Enable partial matching
}


def get_all_control_hints() -> Dict[str, Dict[str, List[str]]]:
    """
    Enumerate all control hints from the control_hints and control_hints_k8s modules.

    Returns:
        Dict mapping control IDs to their generic and language-specific hints.
        Format: {
            'control_id': {
                'generic': [list_of_generic_hints],
                'python': [list_of_python_hints],
                'golang': [list_of_golang_hints],
                'java': [list_of_java_hints],
                'cpp': [list_of_cpp_hints],
                'kubernetes': [list_of_kubernetes_hints]
            }
        }
    """
    control_hints_dict = {}

    # Process both control hints modules
    modules_to_process = [control_hints, control_hints_k8s]
    
    for module in modules_to_process:
        module_name = module.__name__.split('.')[-1]
        logger.debug(f"Processing control hints from {module_name}")
        
        # Get all attributes from the module
        for attr_name, attr_value in inspect.getmembers(module):
            # Skip private attributes and non-list attributes
            if attr_name.startswith("_") or not isinstance(attr_value, list):
                continue

            # Check if this is a control ID (generic hints)
            control_match = CONTROL_ID_PATTERN.match(attr_name)
            if control_match:
                control_id = control_match.group(1)
                if control_id not in control_hints_dict:
                    control_hints_dict[control_id] = {
                        "generic": [],
                        "python": [],
                        "golang": [],
                        "java": [],
                        "cpp": [],
                        "kubernetes": [],
                    }
                
                # Add hints to the appropriate category
                if module_name == "control_hints_k8s":
                    # K8s hints go to kubernetes category
                    control_hints_dict[control_id]["kubernetes"].extend(attr_value)
                    logger.debug(
                        f"Found kubernetes hints for control {control_id}: {len(attr_value)} hints"
                    )
                else:
                    # Regular hints go to generic category
                    control_hints_dict[control_id]["generic"].extend(attr_value)
                    logger.debug(
                        f"Found generic hints for control {control_id}: {len(attr_value)} hints"
                    )

            # Check if this is a language-specific control (e.g., ac10_python)
            for lang in SUPPORTED_LANGUAGES:
                lang_pattern = f"_{lang}$"
                if re.search(lang_pattern, attr_name):
                    # Extract the base control ID
                    base_control = attr_name[
                        : -len(f"_{lang}")
                    ]  # Remove _python, _golang, etc.
                    control_match = CONTROL_ID_PATTERN.match(base_control)
                    if control_match:
                        control_id = control_match.group(1)
                        if control_id not in control_hints_dict:
                            control_hints_dict[control_id] = {
                                "generic": [],
                                "python": [],
                                "golang": [],
                                "java": [],
                                "cpp": [],
                                "kubernetes": [],
                            }
                        control_hints_dict[control_id][lang] = attr_value
                        logger.debug(
                            f"Found {lang} hints for control {control_id}: {len(attr_value)} hints"
                        )

    logger.info(f"Enumerated {len(control_hints_dict)} controls with hints")
    return control_hints_dict


def get_control_hints_for_language(language: str) -> Dict[str, List[str]]:
    """
    Get all control hints for a specific language.

    Args:
        language (str): The language to get hints for ('python', 'golang', 'java', 'cpp', 'kubernetes')

    Returns:
        Dict mapping control IDs to their hints for the specified language.
        Format: {'control_id': [list_of_hints]}
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}. Supported languages: {SUPPORTED_LANGUAGES}"
        )

    all_hints = get_all_control_hints()
    language_hints = {}

    for control_id, hints_dict in all_hints.items():
        # Include both generic and language-specific hints
        combined_hints = hints_dict["generic"] + hints_dict[language]
        if combined_hints:
            language_hints[control_id] = combined_hints

    logger.info(f"Retrieved {len(language_hints)} controls with {language} hints")
    return language_hints


def _calculate_similarity_score(hint: str, content_word: str) -> float:
    """
    Calculate similarity score between a hint and a content word.
    
    Args:
        hint (str): The control hint to match
        content_word (str): The word from the content
        
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    hint_lower = hint.lower()
    content_lower = content_word.lower()
    
    # Exact match gets highest score
    if hint_lower == content_lower:
        return 1.0
    
    # Check if hint is contained within content word (partial match)
    if hint_lower in content_lower:
        return 0.9
    
    # Check if content word is contained within hint (partial match)
    if content_lower in hint_lower:
        return 0.8
    
    # Fuzzy matching using SequenceMatcher
    if SEARCH_CONFIG["enable_fuzzy_matching"]:
        similarity = SequenceMatcher(None, hint_lower, content_lower).ratio()
        return similarity
    
    return 0.0


def _find_best_matches(hint: str, content_words: List[str]) -> List[Tuple[str, float]]:
    """
    Find the best matches for a hint in the content words.
    
    Args:
        hint (str): The control hint to match
        content_words (List[str]): List of words from the content
        
    Returns:
        List[Tuple[str, float]]: List of (word, score) tuples, sorted by score descending
    """
    matches = []
    
    for word in content_words:
        score = _calculate_similarity_score(hint, word)
        if score >= SEARCH_CONFIG["partial_match_threshold"]:
            matches.append((word, score))
    
    # Sort by score descending and limit results
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:SEARCH_CONFIG["max_fuzzy_matches"]]


def _extract_yaml_patterns(content: str) -> List[str]:
    """
    Extract YAML patterns and keys from content for enhanced pattern matching.
    
    Args:
        content (str): The content to extract patterns from
        
    Returns:
        List[str]: List of extracted YAML patterns
    """
    patterns = []
    
    # Extract YAML keys (lines ending with :)
    yaml_keys = re.findall(r'^\s*([^:]+):', content, re.MULTILINE)
    patterns.extend(yaml_keys)
    
    # Extract YAML values (lines with key: value)
    yaml_values = re.findall(r'^\s*([^:]+):\s*(.+)$', content, re.MULTILINE)
    for key, value in yaml_values:
        patterns.append(key.strip())
        patterns.append(value.strip())
    
    # Extract resource types (kind: Deployment, apiVersion: apps/v1)
    resource_patterns = re.findall(r'kind:\s*(\w+)', content, re.IGNORECASE)
    patterns.extend(resource_patterns)
    
    # Extract annotations and labels
    annotation_patterns = re.findall(r'([^/]+/[^:]+):', content)
    patterns.extend(annotation_patterns)
    
    return patterns


def search_control_hints_in_content(file_contents: str, language: str) -> List[str]:
    """
    Search for control hints in file contents for a specific language using enhanced matching.

    Args:
        file_contents (str): The contents of the file to search
        language (str): The language to search for ('python', 'golang', 'java', 'cpp', 'kubernetes')

    Returns:
        List of control IDs that were found in the content
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}. Supported languages: {SUPPORTED_LANGUAGES}"
        )

    found_controls = []
    language_hints = get_control_hints_for_language(language)
    
    # Parse file contents into words for searching
    file_words = file_contents.lower().split()
    
    # Extract YAML patterns for enhanced matching
    yaml_patterns = []
    if SEARCH_CONFIG["enable_pattern_matching"] and language == "kubernetes":
        yaml_patterns = _extract_yaml_patterns(file_contents)
        yaml_patterns = [p.lower() for p in yaml_patterns if p.strip()]
    
    # Combine all searchable content
    all_searchable_content = file_words + yaml_patterns
    all_searchable_content = list(set(all_searchable_content))  # Remove duplicates
    
    logger.debug(f"Searching through {len(all_searchable_content)} content items")
    
    for control_id, hints in language_hints.items():
        best_match_score = 0.0
        best_matches = []
        
        for hint in hints:
            # Clean the hint (remove comments and extra whitespace)
            clean_hint = hint.split("#")[0].strip()
            if not clean_hint:
                continue
            
            # Find best matches for this hint
            matches = _find_best_matches(clean_hint, all_searchable_content)
            
            if matches:
                max_score = max(score for _, score in matches)
                if max_score > best_match_score:
                    best_match_score = max_score
                    best_matches = matches
        
        # If we found good matches, include this control
        if best_match_score >= SEARCH_CONFIG["partial_match_threshold"]:
            found_controls.append(control_id)
            logger.debug(
                f"Found control {control_id} with score {best_match_score:.2f} "
                f"based on matches: {[word for word, _ in best_matches[:2]]}"
            )

    logger.info(
        f"Found {len(found_controls)} applicable controls in {language} content"
    )
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
                'cpp': count,
                'kubernetes': count
            }
        }
    """
    all_hints = get_all_control_hints()
    summary = {}

    for control_id, hints_dict in all_hints.items():
        summary[control_id] = {
            "generic": len(hints_dict["generic"]),
            "python": len(hints_dict["python"]),
            "golang": len(hints_dict["golang"]),
            "java": len(hints_dict["java"]),
            "cpp": len(hints_dict["cpp"]),
            "kubernetes": len(hints_dict["kubernetes"]),
        }

    return summary


# Legacy compatibility function
def control_hints_strings_search(
    file_contents: str, search_strings: List[str], control_name: str
) -> bool:
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
        clean_hint = hint.split("#")[0].strip().lower()
        if clean_hint and clean_hint in file_words:
            logger.info(f"Found control {control_name} based on hint: {clean_hint}")
            return True

    return False


def configure_search_settings(**kwargs):
    """
    Configure search settings for enhanced matching.
    
    Args:
        **kwargs: Configuration options to update
    """
    global SEARCH_CONFIG
    SEARCH_CONFIG.update(kwargs)
    logger.info(f"Updated search configuration: {kwargs}")


def get_search_config() -> Dict[str, any]:
    """
    Get current search configuration.
    
    Returns:
        Dict: Current search configuration
    """
    return SEARCH_CONFIG.copy()
