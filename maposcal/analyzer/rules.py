from typing import List, Dict

def apply_rules(chunks: List[Dict]) -> List[Dict]:
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
