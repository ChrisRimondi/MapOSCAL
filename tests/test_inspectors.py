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


def test_python_identify_imported_modules():
    modules, network, fs, logging_mod, crypto = (
        inspect_lang_python.identify_imported_modules(PYTHON_SAMPLE)
    )
    assert "os" in modules
    assert "requests" in network
    assert "logging" in logging_mod
    assert "os" in fs
    assert "logging" in modules
    assert "requests" in modules


def test_python_identify_imported_configuration_variables():
    results = inspect_lang_python.identify_imported_configuration_variables(
        PYTHON_SAMPLE
    )
    assert any(
        r["variable"] == "API_KEY" and r["method"].startswith("Environment")
        for r in results
    )


def test_python_start_inspection():
    with patch("builtins.open", mock_open(read_data=PYTHON_SAMPLE)):
        result = inspect_lang_python.start_inspection("fake.py", None)
    assert result["language"] == "Python"
    assert "API_KEY" in str(result["configuration_settings"])
    assert "requests" in str(result["loaded_modules"]["network_modules"])
    assert "logging" in str(result["loaded_modules"]["logging_modules"])
    assert "os" in str(result["loaded_modules"]["file_system_modules"])
    assert "file_summary" in result


def test_python_summarize_discovery_content():
    with patch("builtins.open", mock_open(read_data=PYTHON_SAMPLE)):
        result = inspect_lang_python.start_inspection("fake.py", None)
    summary = inspect_lang_python.summarize_discovery_content(result)
    assert "Python" in summary
    assert "networking modules" in summary
    assert "File system access is expected" in summary
    assert "Logging capabilities are expected" in summary


def test_golang_identify_imported_modules():
    modules, network, fs, logging_mod, crypto = (
        inspect_lang_golang.identify_imported_modules(GOLANG_SAMPLE)
    )
    assert "os" in modules
    assert "net/http" in network
    assert "log" in logging_mod
    assert "os" in fs
    assert "crypto/tls" in crypto


def test_golang_identify_imported_configuration_variables():
    results = inspect_lang_golang.identify_imported_configuration_variables(
        GOLANG_SAMPLE
    )
    assert any(
        r["variable"] == "apiKey" and r["method"].startswith("Environment")
        for r in results
    )


def test_golang_start_inspection():
    with patch("builtins.open", mock_open(read_data=GOLANG_SAMPLE)):
        result = inspect_lang_golang.start_inspection("fake.go", None)
    assert result["language"] == "Golang"
    assert "apiKey" in str(result["configuration_settings"])
    assert "net/http" in str(result["loaded_modules"]["network_modules"])
    assert "log" in str(result["loaded_modules"]["logging_modules"])
    assert "os" in str(result["loaded_modules"]["file_system_modules"])
    assert "file_summary" in result


def test_golang_summarize_discovery_content():
    with patch("builtins.open", mock_open(read_data=GOLANG_SAMPLE)):
        result = inspect_lang_golang.start_inspection("fake.go", None)
    summary = inspect_lang_golang.summarize_discovery_content(result)
    assert "Golang" in summary
    assert "networking modules" in summary
    assert "File system access is expected" in summary
    assert "Logging capabilities are expected" in summary


def test_python_path_truncation():
    """Test that file paths are truncated when base_dir is provided."""
    with patch("builtins.open", mock_open(read_data=PYTHON_SAMPLE)):
        result = inspect_lang_python.start_inspection("/Users/test/code/project/file.py", "/Users/test/code/project")
    assert result["file_path"] == "file.py"


def test_golang_path_truncation():
    """Test that file paths are truncated when base_dir is provided."""
    with patch("builtins.open", mock_open(read_data=GOLANG_SAMPLE)):
        result = inspect_lang_golang.start_inspection("/Users/test/code/project/file.go", "/Users/test/code/project")
    assert result["file_path"] == "file.go"


def test_python_path_no_truncation():
    """Test that file paths are not truncated when base_dir is not provided."""
    with patch("builtins.open", mock_open(read_data=PYTHON_SAMPLE)):
        result = inspect_lang_python.start_inspection("/Users/test/code/project/file.py", None)
    assert result["file_path"] == "/Users/test/code/project/file.py"


def test_golang_path_no_truncation():
    """Test that file paths are not truncated when base_dir is not provided."""
    with patch("builtins.open", mock_open(read_data=GOLANG_SAMPLE)):
        result = inspect_lang_golang.start_inspection("/Users/test/code/project/file.go", None)
    assert result["file_path"] == "/Users/test/code/project/file.go"
