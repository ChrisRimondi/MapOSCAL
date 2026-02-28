import pytest
from unittest.mock import mock_open, patch
from maposcal.inspectors import inspect_lang_python, inspect_lang_golang

PYTHON_SAMPLE = """
import os
import requests
import logging
API_KEY = os.getenv('API_KEY')
"""

GOLANG_SAMPLE = """
import (
    "os"
    "net/http"
    "log"
    "crypto/tls"
)

var apiKey = os.Getenv("API_KEY")
"""

# ---------------------------------------------------------------------------
# Parametrize helpers — one entry per language
# ---------------------------------------------------------------------------

INSPECTOR_PARAMS = [
    pytest.param(
        inspect_lang_python,
        PYTHON_SAMPLE,
        "fake.py",
        "Python",
        {
            "in_modules": ["os", "logging", "requests"],
            "in_network": ["requests"],
            "in_fs": ["os"],
            "in_logging": ["logging"],
        },
        id="python",
    ),
    pytest.param(
        inspect_lang_golang,
        GOLANG_SAMPLE,
        "fake.go",
        "Golang",
        {
            "in_modules": ["os"],
            "in_network": ["net/http"],
            "in_fs": ["os"],
            "in_logging": ["log"],
            "in_crypto": ["crypto/tls"],
        },
        id="golang",
    ),
]

# ---------------------------------------------------------------------------
# Parametrized tests shared across both languages
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("inspector,sample,filename,lang,expected", INSPECTOR_PARAMS)
@pytest.mark.unit
def test_identify_imported_modules(inspector, sample, filename, lang, expected):
    modules, network, fs, logging_mod, crypto = inspector.identify_imported_modules(sample)
    for m in expected.get("in_modules", []):
        assert m in modules
    for m in expected.get("in_network", []):
        assert m in network
    for m in expected.get("in_fs", []):
        assert m in fs
    for m in expected.get("in_logging", []):
        assert m in logging_mod
    for m in expected.get("in_crypto", []):
        assert m in crypto


@pytest.mark.parametrize("inspector,sample,filename,lang,expected", [
    pytest.param(inspect_lang_python, PYTHON_SAMPLE, "fake.py", "Python", "API_KEY", id="python"),
    pytest.param(inspect_lang_golang, GOLANG_SAMPLE, "fake.go", "Golang", "apiKey", id="golang"),
])
@pytest.mark.unit
def test_identify_imported_configuration_variables(inspector, sample, filename, lang, expected):
    results = inspector.identify_imported_configuration_variables(sample)
    assert any(
        r["variable"] == expected and r["method"].startswith("Environment")
        for r in results
    )


@pytest.mark.parametrize("inspector,sample,filename,lang,config_var,network,fs,log_mod", [
    pytest.param(
        inspect_lang_python, PYTHON_SAMPLE, "fake.py", "Python",
        "API_KEY", "requests", "os", "logging",
        id="python",
    ),
    pytest.param(
        inspect_lang_golang, GOLANG_SAMPLE, "fake.go", "Golang",
        "apiKey", "net/http", "os", "log",
        id="golang",
    ),
])
@pytest.mark.unit
def test_start_inspection(inspector, sample, filename, lang, config_var, network, fs, log_mod):
    with patch("builtins.open", mock_open(read_data=sample)):
        result = inspector.start_inspection(filename, None)
    assert result["language"] == lang
    assert config_var in str(result["configuration_settings"])
    assert network in str(result["loaded_modules"]["network_modules"])
    assert log_mod in str(result["loaded_modules"]["logging_modules"])
    assert fs in str(result["loaded_modules"]["file_system_modules"])
    assert "file_summary" in result


@pytest.mark.parametrize("inspector,sample,filename,lang", [
    pytest.param(inspect_lang_python, PYTHON_SAMPLE, "fake.py", "Python", id="python"),
    pytest.param(inspect_lang_golang, GOLANG_SAMPLE, "fake.go", "Golang", id="golang"),
])
@pytest.mark.unit
def test_summarize_discovery_content(inspector, sample, filename, lang):
    with patch("builtins.open", mock_open(read_data=sample)):
        result = inspector.start_inspection(filename, None)
    summary = inspector.summarize_discovery_content(result)
    assert lang in summary
    assert "networking modules" in summary
    assert "File system access is expected" in summary
    assert "Logging capabilities are expected" in summary


@pytest.mark.parametrize("inspector,sample,ext", [
    pytest.param(inspect_lang_python, PYTHON_SAMPLE, "py", id="python"),
    pytest.param(inspect_lang_golang, GOLANG_SAMPLE, "go", id="golang"),
])
@pytest.mark.unit
def test_path_truncation(inspector, sample, ext):
    with patch("builtins.open", mock_open(read_data=sample)):
        result = inspector.start_inspection(
            f"/Users/test/code/project/file.{ext}", "/Users/test/code/project"
        )
    assert result["file_path"] == f"file.{ext}"


@pytest.mark.parametrize("inspector,sample,ext", [
    pytest.param(inspect_lang_python, PYTHON_SAMPLE, "py", id="python"),
    pytest.param(inspect_lang_golang, GOLANG_SAMPLE, "go", id="golang"),
])
@pytest.mark.unit
def test_path_no_truncation(inspector, sample, ext):
    with patch("builtins.open", mock_open(read_data=sample)):
        result = inspector.start_inspection(
            f"/Users/test/code/project/file.{ext}", None
        )
    assert result["file_path"] == f"/Users/test/code/project/file.{ext}"


# ---------------------------------------------------------------------------
# Language-specific tests (Python only — no Go equivalent)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_python_summarize_discovery_content_missing_keys():
    """summarize_discovery_content handles a result with no loaded_modules sub-keys."""
    incomplete_result = {
        "file_path": "test.py",
        "language": "Python",
        "loaded_modules": {},
        "configuration_settings": [],
    }
    summary = inspect_lang_python.summarize_discovery_content(incomplete_result)
    assert "Python" in summary
    assert "No networking capabilities have been detected" in summary
    assert "No file system access has been detected" in summary
    assert "No logging capabilities have been detected" in summary
    assert "No configuration settings" in summary


@pytest.mark.unit
def test_python_summarize_discovery_content_partial_keys():
    """summarize_discovery_content handles partial loaded_modules gracefully."""
    partial_result = {
        "file_path": "test.py",
        "language": "Python",
        "loaded_modules": {
            "network_modules": ["requests"],
            # fs and logging keys deliberately absent
        },
        "configuration_settings": [],
    }
    summary = inspect_lang_python.summarize_discovery_content(partial_result)
    assert "Python" in summary
    assert "networking modules shows the following being used for connectivity: ['requests']" in summary
    assert "No file system access has been detected" in summary
    assert "No logging capabilities have been detected" in summary
