"""
Security rule analysis utilities.
This module provides functions for analyzing code chunks and identifying
security-related patterns and control mappings.
"""

from typing import List, Dict, Any

def apply_rules(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply security rules to code chunks and identify relevant security controls.
    
    Args:
        chunks: List of dictionaries containing code chunks with their content
        
    Returns:
        Updated list of chunks with added security flags and control hints:
        - security_flags: Dictionary of boolean flags for security features
        - control_hints: List of relevant security control identifiers
    """
    for chunk in chunks:
        content = chunk.get("content", "").lower()
        flags = {
            "uses_tls": "tls" in content or "https" in content,
            "hardcoded_secret": "secret" in content or "apikey" in content,
            "auth_check": "token" in content or "auth" in content
        }
        chunk["security_flags"] = flags
        chunk["control_hints"] = []
        if flags["uses_tls"]:
            chunk["control_hints"].append("SC-12")
        if flags["auth_check"]:
            chunk["control_hints"].append("AC-6")
    return chunks
