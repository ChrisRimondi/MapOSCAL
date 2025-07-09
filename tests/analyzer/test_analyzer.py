import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from maposcal.analyzer import chunker
from maposcal.analyzer.analyzer import Analyzer
import tempfile



# Test detect_chunk_type
@pytest.mark.parametrize(
    "suffix,expected",
    [
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
    ],
)
def test_detect_chunk_type(suffix, expected):
    assert chunker.detect_chunk_type(suffix) == expected


# Test analyze_repo with a mock parser
# (Removed at user request)
# def test_analyze_repo_excludes_patterns(tmp_path, monkeypatch):
#     ...


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


def test_analyzer_with_custom_config_extensions():
    """Test that Analyzer accepts custom configuration file extensions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary repository structure
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Create some test files
        (repo_path / "config.yaml").write_text("key: value")
        (repo_path / "config.json").write_text('{"key": "value"}')
        (repo_path / "config.env").write_text("KEY=value")
        (repo_path / "main.py").write_text("print('hello')")

        # Test with custom config extensions
        custom_extensions = [".yaml", ".env"]
        analyzer = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(repo_path / ".oscalgen"),
            config_extensions=custom_extensions,
            auto_discover_config=False,
        )

        # Verify that only specified extensions are treated as config files
        assert ".yaml" in analyzer.config_extensions
        assert ".env" in analyzer.config_extensions
        assert ".json" not in analyzer.config_extensions


def test_analyzer_with_default_config_extensions():
    """Test that Analyzer uses default configuration file extensions when none specified."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        analyzer = Analyzer(
            repo_path=str(repo_path), output_dir=str(repo_path / ".oscalgen")
        )

        # Should use default extensions from settings
        from maposcal import settings

        assert analyzer.config_extensions == settings.config_file_extensions


def test_analyzer_extension_normalization():
    """Test that file extensions are properly normalized (add dot if missing)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Test extensions without dots
        custom_extensions = ["yaml", "json", "env"]
        analyzer = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(repo_path / ".oscalgen"),
            config_extensions=custom_extensions,
        )

        # Should normalize to include dots
        assert ".yaml" in analyzer.config_extensions
        assert ".json" in analyzer.config_extensions
        assert ".env" in analyzer.config_extensions


def test_analyzer_with_manual_config_files():
    """Test that Analyzer accepts manual list of configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary repository structure
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Create some test files
        (repo_path / "config.yaml").write_text("key: value")
        (repo_path / "config.json").write_text('{"key": "value"}')
        (repo_path / "config.env").write_text("KEY=value")
        (repo_path / "main.py").write_text("print('hello')")

        # Test with manual file specification
        manual_files = ["config.yaml", "config.env"]
        analyzer = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(repo_path / ".oscalgen"),
            auto_discover_config=False,
            config_files=manual_files,
        )

        # Verify that manual files are set correctly
        assert Path("config.yaml") in analyzer.config_files_list
        assert Path("config.env") in analyzer.config_files_list
        assert Path("config.json") not in analyzer.config_files_list
        assert analyzer.auto_discover_config is False


def test_analyzer_auto_discovery_vs_manual():
    """Test the difference between auto-discovery and manual file specification."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Create test files
        (repo_path / "config.yaml").write_text("key: value")
        (repo_path / "config.json").write_text('{"key": "value"}')
        (repo_path / "main.py").write_text("print('hello')")

        # Test auto-discovery (should include both yaml and json)
        analyzer_auto = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(repo_path / ".oscalgen"),
            config_extensions=[".yaml", ".json"],
            auto_discover_config=True,
        )

        # Test manual specification (should only include yaml)
        analyzer_manual = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(repo_path / ".oscalgen"),
            auto_discover_config=False,
            config_files=["config.yaml"],
        )

        # Verify different behaviors
        assert ".yaml" in analyzer_auto.config_extensions
        assert ".json" in analyzer_auto.config_extensions
        assert analyzer_auto.auto_discover_config is True

        assert Path("config.yaml") in analyzer_manual.config_files_list
        assert Path("config.json") not in analyzer_manual.config_files_list
        assert analyzer_manual.auto_discover_config is False


def test_analyzer_with_llm_config():
    """Test that Analyzer accepts LLM configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        llm_config = {
            "analyze": {"provider": "gemini", "model": "gemini-2.5-flash"}
        }

        analyzer = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(repo_path / ".oscalgen"),
            llm_config=llm_config,
        )

        assert analyzer.llm_config == llm_config


def test_analyzer_metadata_injection():
    """Test that Analyzer injects metadata into output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()
        output_dir = repo_path / ".oscalgen"
        output_dir.mkdir()

        # Create test files
        (repo_path / "main.py").write_text("print('hello')")
        (repo_path / "config.yaml").write_text("key: value")

        analyzer = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(output_dir),
            llm_config={"analyze": {"provider": "openai", "model": "gpt-4"}},
        )

        # Mock the LLM handler to avoid API calls
        with patch("maposcal.analyzer.analyzer.LLMHandler") as mock_llm:
            mock_llm_instance = MagicMock()
            mock_llm_instance.query.return_value = "Test summary"
            mock_llm.return_value = mock_llm_instance

            # Run analysis
            analyzer.run()

            # Check that metadata was injected into meta.json
            meta_file = output_dir / "meta.json"
            assert meta_file.exists()
            
            with open(meta_file) as f:
                meta_data = json.load(f)
            
            assert "_metadata" in meta_data
            metadata = meta_data["_metadata"]
            assert "generation_info" in metadata
            info = metadata["generation_info"]
            assert info["model"] == "gpt-4"
            assert info["provider"] == "openai"
            assert info["command"] == "analyze"

            # Check that metadata was injected into summary_meta.json
            summary_file = output_dir / "summary_meta.json"
            assert summary_file.exists()
            
            with open(summary_file) as f:
                summary_data = json.load(f)
            
            assert "_metadata" in summary_data
            summary_metadata = summary_data["_metadata"]
            assert "generation_info" in summary_metadata
            summary_info = summary_metadata["generation_info"]
            assert summary_info["model"] == "gpt-4"
            assert summary_info["provider"] == "openai"
            assert summary_info["command"] == "analyze"


def test_analyzer_metadata_backward_compatibility():
    """Test that Analyzer maintains backward compatibility with old metadata format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()
        output_dir = repo_path / ".oscalgen"
        output_dir.mkdir()

        # Create test files
        (repo_path / "main.py").write_text("print('hello')")

        analyzer = Analyzer(
            repo_path=str(repo_path),
            output_dir=str(output_dir),
        )

        # Mock the LLM handler
        with patch("maposcal.analyzer.analyzer.LLMHandler") as mock_llm:
            mock_llm_instance = MagicMock()
            mock_llm_instance.query.return_value = "Test summary"
            mock_llm.return_value = mock_llm_instance

            # Run analysis
            analyzer.run()

            # Check that chunks are still accessible in the expected format
            meta_file = output_dir / "meta.json"
            with open(meta_file) as f:
                meta_data = json.load(f)
            
            # Should have both metadata and chunks
            assert "_metadata" in meta_data
            assert "chunks" in meta_data
            assert isinstance(meta_data["chunks"], list)
