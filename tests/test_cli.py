"""Tests for the MapOSCAL CLI."""

import pytest
from typer.testing import CliRunner
from maposcal.cli import app
from unittest.mock import patch, MagicMock, mock_open
import os

runner = CliRunner()


def test_cli_help():
    """Test that the CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout

@patch("maposcal.cli.Analyzer")
@patch("maposcal.cli.load_config")
def test_analyze_command(mock_load_config, mock_analyzer):
    mock_load_config.return_value = {
        "repo_path": "repo/",
        "output_dir": ".oscalgen",
        "config_extensions": [".yaml"],
        "auto_discover_config": True,
        "config_files": None,
    }
    mock_instance = MagicMock()
    mock_analyzer.return_value = mock_instance
    result = runner.invoke(app, ["analyze", "dummy.yaml"])
    assert result.exit_code == 0
    mock_load_config.assert_called_once_with("dummy.yaml")
    mock_instance.run.assert_called_once()

@patch("maposcal.cli.os.path.exists", return_value=True)
@patch("maposcal.cli.load_config")
@patch("maposcal.cli.get_relevant_chunks", return_value=[{"content": "test", "source_file": "file.py"}])
@patch("maposcal.cli.LLMHandler")
@patch("maposcal.cli.build_service_overview_prompt", return_value="prompt")
@patch("maposcal.cli.open", new_callable=mock_open)
def test_summarize_command(mock_open_file, mock_build_prompt, mock_llm_handler, mock_get_chunks, mock_load_config, mock_exists):
    mock_load_config.return_value = {"repo_path": "repo/", "output_dir": ".oscalgen"}
    mock_llm = MagicMock()
    mock_llm.query.return_value = "summary"
    mock_llm_handler.return_value = mock_llm
    result = runner.invoke(app, ["summarize", "dummy.yaml"])
    assert result.exit_code == 0
    assert "Security overview written to" in result.stdout
    mock_open_file.assert_called()
    mock_llm.query.assert_called()

@patch("maposcal.cli.ProfileControlExtractor")
@patch("maposcal.cli.LLMHandler")
@patch("maposcal.cli.load_config")
@patch("maposcal.cli.map_control", return_value='{"foo": "bar"}')
@patch("maposcal.cli.parse_llm_response", return_value={"props": [], "control_id": "AC-1"})
@patch("maposcal.cli.validate_control_status", return_value=(True, None))
@patch("maposcal.cli.validate_implemented_requirement", return_value=(True, []))
@patch("maposcal.cli.validate_unique_uuids", return_value=(True, None))
@patch("maposcal.cli.open", new_callable=mock_open)
@patch("os.path.exists", return_value=True)
def test_generate_command(mock_exists, mock_open_file, mock_validate_uuids, mock_validate_req, mock_validate_status, mock_parse_llm, mock_map_control, mock_load_config, mock_llm_handler, mock_profile_extractor):
    mock_load_config.return_value = {
        "output_dir": ".oscalgen",
        "top_k": 1,
        "max_critique_retries": 1,
        "catalog_path": "cat.json",
        "profile_path": "prof.json",
    }
    mock_profile = MagicMock()
    mock_profile.profile = {"profile": {"imports": ["AC-1"]}}
    mock_profile_extractor.return_value = mock_profile
    result = runner.invoke(app, ["generate", "dummy.yaml"])
    assert result.exit_code == 0
    assert "Generated OSCAL component written to" in result.stdout
    mock_open_file.assert_called()

@patch("maposcal.cli.LLMHandler")
@patch("maposcal.cli.load_config")
@patch("maposcal.cli.os.path.exists", return_value=True)
@patch("maposcal.cli.open", new_callable=mock_open)
@patch("maposcal.cli.build_evaluate_prompt", return_value="prompt")
@patch("maposcal.cli.parse_llm_response", return_value={"total_score": 8})
@patch("maposcal.cli.json.load", return_value={"implemented_requirements": [{"control-id": "AC-1"}]})
def test_evaluate_command(mock_json_load, mock_parse_llm, mock_build_prompt, mock_open_file, mock_exists, mock_load_config, mock_llm_handler):
    mock_load_config.return_value = {"output_dir": ".oscalgen"}
    mock_llm = MagicMock()
    mock_llm.query.return_value = "eval_result"
    mock_llm_handler.return_value = mock_llm
    result = runner.invoke(app, ["evaluate", "dummy.yaml"])
    assert result.exit_code == 0
    assert "Evaluation results written to" in result.stdout
    mock_open_file.assert_called()
    mock_llm.query.assert_called()

# Error case: missing config file for analyze
@patch("maposcal.cli.os.path.exists", return_value=False)
def test_analyze_missing_config(mock_exists):
    result = runner.invoke(app, ["analyze", "missing.yaml"])
    assert result.exit_code != 0
    assert "Config file not found" in result.stdout
