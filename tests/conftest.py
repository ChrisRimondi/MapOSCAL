"""Common test fixtures for the MapOSCAL test suite."""
import os
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def sample_oscal_file(test_data_dir):
    """Return the path to a sample OSCAL file."""
    return test_data_dir / "sample_oscal.json"

@pytest.fixture
def sample_control_config():
    """Return a sample control configuration."""
    return {
        "controls": [
            {
                "id": "AC-1",
                "title": "Access Control Policy and Procedures",
                "description": "The organization develops, disseminates, and reviews/updates..."
            }
        ]
    }

@pytest.fixture
def mock_openai_response():
    """Return a mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock response from OpenAI"
                }
            }
        ]
    } 