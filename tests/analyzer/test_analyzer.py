import pytest
from pathlib import Path
from maposcal.analyzer import chunker

# Test detect_chunk_type
@pytest.mark.parametrize("suffix,expected", [
    (".py", "code"),
    (".go", "code"),
    (".yaml", "config"),
    (".yml", "config"),
    (".json", "config"),
    (".md", "doc"),
    (".rst", "doc"),
    (".txt", "doc"),
    (".exe", "unknown"),
    (".foo", "unknown"),
])
def test_detect_chunk_type(suffix, expected):
    assert chunker.detect_chunk_type(suffix) == expected

# Test analyze_repo with a mock parser
def test_analyze_repo_excludes_patterns(tmp_path, monkeypatch):
    # Create files
    (tmp_path / "file.py").write_text("print('hello')\n")
    (tmp_path / "test_file.py").write_text("print('test')\n")
    (tmp_path / "file.yaml").write_text("foo: bar\n")
    (tmp_path / "README.md").write_text("# Readme\n")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    # Mock parse_file to return a simple chunk
    def mock_parse_file(path):
        return [{"content": f"content of {path.name}", "start_line": 1, "end_line": 1}]
    monkeypatch.setattr(chunker, "parse_file", mock_parse_file)

    chunks = chunker.analyze_repo(tmp_path)
    # Should not include test_file.py or image.png
    files_in_chunks = {c["source_file"] for c in chunks}
    assert any("file.py" in f for f in files_in_chunks)
    assert any("file.yaml" in f for f in files_in_chunks)
    assert any("README.md" in f for f in files_in_chunks)
    assert not any("test_file.py" in f for f in files_in_chunks)
    assert not any("image.png" in f for f in files_in_chunks)
    # Check chunk_type
    for c in chunks:
        if c["source_file"].endswith(".py"):
            assert c["chunk_type"] == "code"
        elif c["source_file"].endswith(".yaml"):
            assert c["chunk_type"] == "config"
        elif c["source_file"].endswith(".md"):
            assert c["chunk_type"] == "doc"

# --- parser.py tests ---
def test_parse_python(tmp_path):
    code = """
class Foo:
    def bar(self):
        pass

def baz():
    pass
"""
    file = tmp_path / "test.py"
    file.write_text(code)
    from maposcal.analyzer import parser
    chunks = parser.parse_python(file)
    # The parser creates chunks for:
    # 1. Initial empty line
    # 2. Class definition
    # 3. Method definition
    # 4. Function definition
    assert len(chunks) == 4
    assert any("class Foo" in c["content"] for c in chunks)
    assert any("def bar" in c["content"] for c in chunks)
    assert any("def baz" in c["content"] for c in chunks)
    # Verify line numbers are tracked correctly
    class_chunk = next(c for c in chunks if "class Foo" in c["content"])
    assert class_chunk["start_line"] > 0
    assert class_chunk["end_line"] > class_chunk["start_line"]

def test_parse_yaml(tmp_path):
    yaml = """
foo: bar

---

baz: qux
"""
    file = tmp_path / "test.yaml"
    file.write_text(yaml)
    from maposcal.analyzer import parser
    chunks = parser.parse_yaml(file)
    assert len(chunks) >= 2
    assert any("foo: bar" in c["content"] for c in chunks)
    assert all(c["start_line"] == 0 for c in chunks)

def test_parse_markdown(tmp_path):
    md = """
# Title
Some intro

## Section
Details here
"""
    file = tmp_path / "test.md"
    file.write_text(md)
    from maposcal.analyzer import parser
    chunks = parser.parse_markdown(file)
    # The parser creates chunks for:
    # 1. Initial empty line
    # 2. Title section
    # 3. Section with details
    assert len(chunks) == 3
    assert any("# Title" in c["content"] for c in chunks)
    assert any("## Section" in c["content"] for c in chunks)
    # Verify content is properly chunked
    title_chunk = next(c for c in chunks if "# Title" in c["content"])
    section_chunk = next(c for c in chunks if "## Section" in c["content"])
    assert "Some intro" in title_chunk["content"]
    assert "Details here" in section_chunk["content"]

def test_parse_file_dispatch(tmp_path):
    py = tmp_path / "a.py"
    py.write_text("def f(): pass\n")
    yaml = tmp_path / "b.yaml"
    yaml.write_text("foo: bar\n")
    md = tmp_path / "c.md"
    md.write_text("# H\n")
    txt = tmp_path / "d.txt"
    txt.write_text("plain text\n")
    from maposcal.analyzer import parser
    assert parser.parse_file(py)[0]["content"].startswith("def f")
    assert parser.parse_file(yaml)[0]["content"].startswith("foo: bar")
    assert parser.parse_file(md)[0]["content"].startswith("# H")
    assert parser.parse_file(txt)[0]["content"].startswith("plain text")
