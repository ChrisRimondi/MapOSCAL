from pathlib import Path
from typing import List, Dict
from maposcal.analyzer import parser

def analyze_repo(repo_path: Path) -> List[Dict]:
    chunks = []
    for file_path in repo_path.rglob("*"):
        if not file_path.is_file() or file_path.suffix in [".png", ".jpg", ".exe", ".dll"]:
            continue
        try:
            parsed = parser.parse_file(file_path)
            for chunk in parsed:
                chunk["source_file"] = str(file_path)
                chunk["chunk_type"] = detect_chunk_type(file_path.suffix)
                chunks.append(chunk)
        except Exception:
            continue
    return chunks

def detect_chunk_type(suffix: str) -> str:
    if suffix in [".py", ".js", ".go"]:
        return "code"
    elif suffix in [".yaml", ".yml", ".json"]:
        return "config"
    elif suffix in [".md", ".rst"]:
        return "doc"
    else:
        return "unknown"
