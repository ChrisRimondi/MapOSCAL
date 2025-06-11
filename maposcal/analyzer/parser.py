from pathlib import Path
from typing import List, Dict

def parse_python(file_path: Path) -> List[Dict]:
    chunks = []
    lines = file_path.read_text(encoding='utf-8').splitlines()
    block = []
    start_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("def ") or line.strip().startswith("class "):
            if block:
                chunks.append({"content": "\n".join(block), "start_line": start_line, "end_line": i})
                block = []
            start_line = i
        block.append(line)
    if block:
        chunks.append({"content": "\n".join(block), "start_line": start_line, "end_line": len(lines)})
    return chunks

def parse_yaml(file_path: Path) -> List[Dict]:
    text = file_path.read_text(encoding='utf-8')
    return [{"content": block, "start_line": 0, "end_line": 0} for block in text.split("\n\n")]

def parse_markdown(file_path: Path) -> List[Dict]:
    lines = file_path.read_text(encoding='utf-8').splitlines()
    chunks = []
    block = []
    for line in lines:
        if line.startswith("#"):
            if block:
                chunks.append({"content": "\n".join(block)})
                block = []
        block.append(line)
    if block:
        chunks.append({"content": "\n".join(block)})
    return chunks

def parse_file(file_path: Path) -> List[Dict]:
    ext = file_path.suffix.lower()
    if ext == ".py":
        return parse_python(file_path)
    elif ext in [".yaml", ".yml"]:
        return parse_yaml(file_path)
    elif ext in [".md", ".markdown"]:
        return parse_markdown(file_path)
    else:
        return [{"content": file_path.read_text(encoding='utf-8')}]
