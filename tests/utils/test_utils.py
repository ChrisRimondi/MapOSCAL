import pytest
from unittest.mock import patch, MagicMock

import maposcal.utils.utilities as utilities
import maposcal.utils.control_hints_enumerator as enumerator
import maposcal.utils.logging_config as logging_config


# --- utilities.py ---
def test_parse_file_into_strings_basic():
    text = "foo bar baz"
    result = utilities.parse_file_into_strings(text)
    assert result == ["foo", "bar", "baz"]


def test_parse_file_into_strings_empty():
    assert utilities.parse_file_into_strings("") == []
    assert utilities.parse_file_into_strings("   ") == []


def test_parse_file_into_strings_punctuation():
    text = "foo, bar! baz?"
    result = utilities.parse_file_into_strings(text)
    assert "foo," in result and "bar!" in result and "baz?" in result


def test_control_hints_strings_search_positive():
    file_contents = "foo bar baz"
    search_strings = ["bar"]
    assert (
        utilities.control_hints_strings_search(file_contents, search_strings, "SC-8")
        is True
    )


def test_control_hints_strings_search_negative():
    file_contents = "foo bar baz"
    search_strings = ["qux"]
    assert (
        utilities.control_hints_strings_search(file_contents, search_strings, "SC-8")
        is False
    )


def test_control_hints_strings_search_multiple():
    file_contents = "foo bar baz"
    search_strings = ["qux", "baz"]
    assert (
        utilities.control_hints_strings_search(file_contents, search_strings, "SC-8")
        is True
    )


# --- control_hints_enumerator.py ---
@patch("maposcal.utils.control_hints_enumerator.control_hints")
def test_get_all_control_hints_structure(mock_control_hints):
    # Simulate control_hints module attributes
    mock_control_hints.ac1 = ["foo"]
    mock_control_hints.ac1_python = ["bar"]
    mock_control_hints.ac2 = ["baz"]
    mock_control_hints.ac2_golang = ["qux"]
    result = enumerator.get_all_control_hints()
    assert "ac1" in result and "ac2" in result
    assert result["ac1"]["generic"] == ["foo"]
    assert result["ac1"]["python"] == ["bar"]
    assert result["ac2"]["generic"] == ["baz"]
    assert result["ac2"]["golang"] == ["qux"]


@patch("maposcal.utils.control_hints_enumerator.get_all_control_hints")
def test_get_control_hints_for_language_valid(mock_get_all):
    mock_get_all.return_value = {
        "ac1": {
            "generic": ["foo"],
            "python": ["bar"],
            "golang": [],
            "java": [],
            "cpp": [],
        },
        "ac2": {"generic": [], "python": ["baz"], "golang": [], "java": [], "cpp": []},
    }
    result = enumerator.get_control_hints_for_language("python")
    assert result["ac1"] == ["foo", "bar"]
    assert result["ac2"] == ["baz"]


def test_get_control_hints_for_language_invalid():
    with pytest.raises(ValueError):
        enumerator.get_control_hints_for_language("ruby")


@patch("maposcal.utils.control_hints_enumerator.get_control_hints_for_language")
def test_search_control_hints_in_content_found(mock_get_for_lang):
    mock_get_for_lang.return_value = {"ac1": ["foo", "bar"]}
    content = "foo something else"
    result = enumerator.search_control_hints_in_content(content, "python")
    assert "ac1" in result


def test_search_control_hints_in_content_not_found():
    # Use real function with no hints
    with patch(
        "maposcal.utils.control_hints_enumerator.get_control_hints_for_language",
        return_value={},
    ):
        result = enumerator.search_control_hints_in_content("nothing here", "python")
        assert result == []


def test_search_control_hints_in_content_invalid_language():
    with pytest.raises(ValueError):
        enumerator.search_control_hints_in_content("foo", "ruby")


@patch("maposcal.utils.control_hints_enumerator.get_all_control_hints")
def test_get_control_hints_summary(mock_get_all):
    mock_get_all.return_value = {
        "ac1": {
            "generic": ["foo"],
            "python": ["bar"],
            "golang": [],
            "java": [],
            "cpp": [],
        },
        "ac2": {
            "generic": [],
            "python": ["baz"],
            "golang": ["qux"],
            "java": [],
            "cpp": [],
        },
    }
    summary = enumerator.get_control_hints_summary()
    assert summary["ac1"]["generic"] == 1
    assert summary["ac2"]["golang"] == 1


def test_legacy_control_hints_strings_search():
    file_contents = "foo bar baz"
    search_strings = ["bar"]
    assert (
        enumerator.control_hints_strings_search(file_contents, search_strings, "SC-8")
        is True
    )
    assert (
        enumerator.control_hints_strings_search(file_contents, ["qux"], "SC-8") is False
    )


# --- logging_config.py ---
@patch("maposcal.utils.logging_config.Path")
@patch("maposcal.utils.logging_config.logging")
def test_configure_logging_success(mock_logging, mock_path):
    mock_log_dir = MagicMock()
    mock_log_dir.mkdir.return_value = None
    mock_path.return_value.__truediv__.return_value = mock_log_dir
    mock_file_handler = MagicMock()
    mock_console_handler = MagicMock()
    mock_logging.FileHandler.return_value = mock_file_handler
    mock_logging.StreamHandler.return_value = mock_console_handler
    mock_logging.getLogger.return_value.handlers = []
    result = logging_config.configure_logging()
    assert result is True
    mock_log_dir.mkdir.assert_called()
    mock_logging.getLogger.assert_called()
    mock_logging.FileHandler.assert_called()
    mock_logging.StreamHandler.assert_called()


@patch("maposcal.utils.logging_config.Path")
@patch("maposcal.utils.logging_config.logging")
def test_configure_logging_failure(mock_logging, mock_path):
    mock_path.side_effect = Exception("fail")
    result = logging_config.configure_logging()
    assert result is False
