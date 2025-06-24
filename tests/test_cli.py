"""Tests for the MapOSCAL CLI."""

import pytest
from typer.testing import CliRunner
from maposcal.cli import app

runner = CliRunner()


def test_cli_help():
    """Test that the CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
