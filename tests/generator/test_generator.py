"""
Tests for maposcal.generator.control_mapper and maposcal.generator.security_section_mapper.

Covers:
- parse_llm_response: JSON extraction from raw LLM output
- security_section_mapper: pure helper functions (no I/O)
- get_relevant_chunks: FAISS-backed retrieval (mocked)
- map_control: end-to-end control generation (mocked LLM + chunks)
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from maposcal.generator.control_mapper import (
    parse_llm_response,
    get_relevant_chunks,
    map_control,
    validate_content_quality,
)
from maposcal.generator.security_section_mapper import (
    get_control_family,
    get_relevant_security_sections,
    parse_security_overview_sections,
    build_selective_security_overview_section,
    validate_security_overview_structure,
)


# ---------------------------------------------------------------------------
# Fixtures / shared test data
# ---------------------------------------------------------------------------

VALID_LLM_CONTENT = {
    "control-status": "applicable and inherently satisfied",
    "control-explanation": "The system implements access control through authentication mechanisms.",
    "control-configuration": [],
    "statement-description": "Access control is implemented through role-based authentication.",
}

SAMPLE_CONTROL_DICT = {
    "id": "AC-1",
    "title": "Access Control Policy and Procedures",
    "statement": "The organization develops, documents, and disseminates an access control policy.",
}

SAMPLE_SECURITY_OVERVIEW = """\
# Service Overview
This service is a REST API for user management.

## Authentication and Authorization
OAuth 2.0 with JWT tokens is used for all endpoints.

## Encryption and Data Protection
All data at rest is encrypted with AES-256.

## Audit Logging and Monitoring
All authentication events are logged to CloudWatch.
"""


# ---------------------------------------------------------------------------
# A. parse_llm_response
# ---------------------------------------------------------------------------

class TestParseLlmResponse:
    """parse_llm_response extracts JSON from various LLM output formats."""

    @pytest.mark.parametrize("raw,expected", [
        # Markdown fenced block with json label
        (
            '```json\n{"key": "value"}\n```',
            {"key": "value"},
        ),
        # Markdown fenced block without label
        (
            '```\n{"key": "value"}\n```',
            {"key": "value"},
        ),
        # Plain JSON string
        (
            '{"key": "value"}',
            {"key": "value"},
        ),
        # JSON with leading/trailing whitespace
        (
            '  {"key": "value"}  ',
            {"key": "value"},
        ),
        # Extra prose before and after fenced block
        (
            'Here is the result:\n```json\n{"key": "value"}\n```\nDone.',
            {"key": "value"},
        ),
        # Nested JSON object
        (
            '{"outer": {"inner": 1}}',
            {"outer": {"inner": 1}},
        ),
    ])
    @pytest.mark.unit
    def test_parse_valid_json(self, raw, expected):
        assert parse_llm_response(raw) == expected

    @pytest.mark.unit
    def test_parse_malformed_json_returns_raw_key(self):
        result = parse_llm_response("not valid json at all")
        assert "llm_raw_response" in result

    @pytest.mark.unit
    def test_parse_empty_string_returns_raw_key(self):
        result = parse_llm_response("")
        assert "llm_raw_response" in result

    @pytest.mark.unit
    def test_parse_realistic_control_json(self):
        raw = json.dumps(VALID_LLM_CONTENT)
        result = parse_llm_response(raw)
        assert result["control-status"] == "applicable and inherently satisfied"
        assert "control-explanation" in result


# ---------------------------------------------------------------------------
# B. security_section_mapper — pure functions
# ---------------------------------------------------------------------------

class TestGetControlFamily:
    """get_control_family extracts the family prefix from a NIST control ID."""

    @pytest.mark.parametrize("control_id,expected", [
        ("AC-1", "AC"),
        ("SC-28", "SC"),
        ("AU-2", "AU"),
        ("IA-5", "IA"),
        ("CM-6", "CM"),
    ])
    @pytest.mark.unit
    def test_standard_control_ids(self, control_id, expected):
        assert get_control_family(control_id) == expected

    @pytest.mark.unit
    def test_empty_string_returns_default(self):
        assert get_control_family("") == "DEFAULT"

    @pytest.mark.unit
    def test_none_returns_default(self):
        assert get_control_family(None) == "DEFAULT"

    @pytest.mark.unit
    def test_no_hyphen_returns_full_string_uppercased(self):
        # "NOHYPHEN" has no hyphen, so split("-")[0] == "NOHYPHEN"
        assert get_control_family("nohyphen") == "NOHYPHEN"


class TestGetRelevantSecuritySections:
    """get_relevant_security_sections maps a control ID to section keys."""

    @pytest.mark.parametrize("control_id,expected_sections", [
        ("AC-1", ["service_overview", "authentication_authorization"]),
        ("AU-2", ["service_overview", "audit_logging_monitoring"]),
        ("SC-8", ["service_overview", "encryption_data_protection"]),
        ("IA-5", ["service_overview", "authentication_authorization"]),
    ])
    @pytest.mark.unit
    def test_known_families(self, control_id, expected_sections):
        sections = get_relevant_security_sections(control_id)
        assert sections == expected_sections

    @pytest.mark.unit
    def test_unknown_family_returns_service_overview(self):
        # Any family not in the map falls back to DEFAULT → ["service_overview"]
        sections = get_relevant_security_sections("ZZ-99")
        assert "service_overview" in sections


class TestParseSecurityOverviewSections:
    """parse_security_overview_sections splits markdown into a section dict."""

    @pytest.mark.unit
    def test_parses_all_four_sections(self):
        result = parse_security_overview_sections(SAMPLE_SECURITY_OVERVIEW)
        assert "service_overview" in result
        assert "authentication_authorization" in result
        assert "encryption_data_protection" in result
        assert "audit_logging_monitoring" in result

    @pytest.mark.unit
    def test_section_content_contains_header(self):
        result = parse_security_overview_sections(SAMPLE_SECURITY_OVERVIEW)
        assert "Service Overview" in result["service_overview"]
        assert "OAuth 2.0" in result["authentication_authorization"]

    @pytest.mark.unit
    def test_empty_string_returns_empty_dict(self):
        assert parse_security_overview_sections("") == {}

    @pytest.mark.unit
    def test_none_returns_empty_dict(self):
        assert parse_security_overview_sections(None) == {}


class TestBuildSelectiveSecurityOverviewSection:
    """build_selective_security_overview_section returns focused context strings."""

    @pytest.mark.unit
    def test_returns_relevant_sections_for_ac_control(self):
        sections = parse_security_overview_sections(SAMPLE_SECURITY_OVERVIEW)
        result = build_selective_security_overview_section("AC-1", sections)
        assert "Service Overview" in result
        assert "Authentication" in result
        # Encryption section should NOT be included for AC-1
        assert "Encryption" not in result

    @pytest.mark.unit
    def test_returns_empty_string_when_no_sections(self):
        result = build_selective_security_overview_section("AC-1", {})
        assert result == ""

    @pytest.mark.unit
    def test_returns_formatted_header(self):
        sections = parse_security_overview_sections(SAMPLE_SECURITY_OVERVIEW)
        result = build_selective_security_overview_section("AC-1", sections)
        assert "SERVICE SECURITY OVERVIEW" in result

    @pytest.mark.unit
    def test_missing_section_key_handled_gracefully(self):
        # Only one section present; missing sections are silently skipped
        sections = {"service_overview": "# Service Overview\nBasic info."}
        result = build_selective_security_overview_section("AC-1", sections)
        # Should still include the service_overview fallback without raising
        assert isinstance(result, str)


class TestValidateSecurityOverviewStructure:
    """validate_security_overview_structure checks that all required sections exist."""

    @pytest.mark.unit
    def test_valid_structure_returns_true_no_issues(self):
        is_valid, issues = validate_security_overview_structure(SAMPLE_SECURITY_OVERVIEW)
        assert is_valid is True
        assert issues == []

    @pytest.mark.unit
    def test_empty_content_returns_false(self):
        is_valid, issues = validate_security_overview_structure("")
        assert is_valid is False
        assert len(issues) > 0

    @pytest.mark.unit
    def test_missing_sections_reported(self):
        # Only service overview present — three sections missing
        partial = "# Service Overview\nJust this section."
        is_valid, issues = validate_security_overview_structure(partial)
        assert is_valid is False
        missing_issues = [i for i in issues if "Missing section" in i]
        assert len(missing_issues) >= 3

    @pytest.mark.unit
    def test_none_returns_false(self):
        is_valid, issues = validate_security_overview_structure(None)
        assert is_valid is False


# ---------------------------------------------------------------------------
# C. validate_content_quality — pure function
# ---------------------------------------------------------------------------

class TestValidateContentQuality:
    """validate_content_quality checks LLM-generated content fields."""

    @pytest.mark.unit
    def test_valid_content_passes(self):
        is_valid, issues = validate_content_quality(VALID_LLM_CONTENT)
        assert is_valid is True
        assert issues == []

    @pytest.mark.unit
    def test_missing_control_status_fails(self):
        content = {**VALID_LLM_CONTENT, "control-status": ""}
        is_valid, issues = validate_content_quality(content)
        assert is_valid is False
        assert any("control-status" in i for i in issues)

    @pytest.mark.unit
    def test_invalid_control_status_fails(self):
        content = {**VALID_LLM_CONTENT, "control-status": "not a valid status"}
        is_valid, issues = validate_content_quality(content)
        assert is_valid is False
        assert any("Invalid control-status" in i for i in issues)

    @pytest.mark.unit
    def test_short_explanation_fails(self):
        content = {**VALID_LLM_CONTENT, "control-explanation": "short"}
        is_valid, issues = validate_content_quality(content)
        assert is_valid is False
        assert any("explanation" in i.lower() for i in issues)

    @pytest.mark.unit
    def test_configuration_status_without_config_fails(self):
        content = {
            **VALID_LLM_CONTENT,
            "control-status": "applicable but only satisfied through configuration",
            "control-configuration": [],
        }
        is_valid, issues = validate_content_quality(content)
        assert is_valid is False
        assert any("configuration" in i.lower() for i in issues)


# ---------------------------------------------------------------------------
# D. get_relevant_chunks — mocked FAISS/embedder
# ---------------------------------------------------------------------------

class TestGetRelevantChunks:
    """get_relevant_chunks queries FAISS indices and returns deduplicated chunks."""

    _CHUNK = {"source_file": "auth.py", "content": "def check_auth(): pass"}

    @pytest.mark.unit
    @patch("maposcal.generator.control_mapper.local_embedder")
    @patch("maposcal.generator.control_mapper.faiss_index")
    @patch("maposcal.generator.control_mapper.meta_store")
    @patch("pathlib.Path.exists", return_value=True)
    def test_happy_path_returns_chunks(
        self, _mock_exists, mock_meta_store, mock_faiss_index, mock_local_embedder
    ):
        mock_local_embedder.embed_one.return_value = [0.1, 0.2, 0.3]
        mock_faiss_index.load_index.return_value = MagicMock()
        mock_faiss_index.search_index.return_value = ([0], [0.9])
        # load_metadata is called twice: once for chunk meta (list), once for summary
        # meta (dict). The summary meta must be a dict to avoid .items() error.
        mock_meta_store.load_metadata.side_effect = [
            [self._CHUNK],  # chunk meta.json → list format
            {},             # summary_meta.json → empty dict (no summaries)
        ]
        mock_meta_store.get_chunk_by_index.return_value = self._CHUNK

        chunks = get_relevant_chunks("access control", "/fake/output")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    @pytest.mark.unit
    @patch("maposcal.generator.control_mapper.local_embedder")
    @patch("pathlib.Path.exists", return_value=False)
    def test_missing_required_index_raises(self, _mock_exists, mock_local_embedder):
        # embed_one is called before Path.exists check, so it must be mocked too
        mock_local_embedder.embed_one.return_value = [0.1, 0.2, 0.3]
        with pytest.raises(FileNotFoundError):
            get_relevant_chunks("access control", "/nonexistent/output")

    @pytest.mark.unit
    @patch("maposcal.generator.control_mapper.local_embedder")
    @patch("maposcal.generator.control_mapper.faiss_index")
    @patch("maposcal.generator.control_mapper.meta_store")
    @patch("pathlib.Path.exists", return_value=True)
    def test_deduplication_by_source_file(
        self, _mock_exists, mock_meta_store, mock_faiss_index, mock_local_embedder
    ):
        mock_local_embedder.embed_one.return_value = [0.1, 0.2, 0.3]
        mock_faiss_index.load_index.return_value = MagicMock()
        # Return the same index twice to simulate duplicates from the main index
        mock_faiss_index.search_index.return_value = ([0, 0], [0.9, 0.9])
        mock_meta_store.load_metadata.side_effect = [
            [self._CHUNK],  # chunk meta.json → list format
            {},             # summary_meta.json → empty dict
        ]
        mock_meta_store.get_chunk_by_index.return_value = self._CHUNK

        chunks = get_relevant_chunks("access control", "/fake/output")
        source_files = [c["source_file"] for c in chunks if "source_file" in c]
        # auth.py should appear at most once after deduplication
        assert source_files.count("auth.py") <= 1


# ---------------------------------------------------------------------------
# E. map_control — mocked LLM and chunks
# ---------------------------------------------------------------------------

class TestMapControl:
    """map_control generates OSCAL implemented requirements with retry logic."""

    def _make_llm_mock(self, query_return_value):
        mock_llm_class = MagicMock()
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        mock_llm_instance.query.return_value = query_return_value
        return mock_llm_class, mock_llm_instance

    @pytest.mark.unit
    @patch("pathlib.Path.exists", return_value=False)
    @patch("maposcal.generator.control_mapper.get_relevant_chunks", return_value=[])
    @patch("maposcal.generator.control_mapper.LLMHandler")
    def test_happy_path_returns_valid_structure(
        self, mock_llm_class, _mock_chunks, _mock_exists
    ):
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        mock_llm_instance.query.return_value = json.dumps(VALID_LLM_CONTENT)

        result = map_control(SAMPLE_CONTROL_DICT, "/fake/output")

        assert result["control-id"] == "AC-1"
        assert "uuid" in result
        assert "props" in result
        # Verify LLM content was merged in
        status_prop = next(
            p for p in result["props"] if p["name"] == "control-status"
        )
        assert status_prop["value"] == "applicable and inherently satisfied"

    @pytest.mark.unit
    @patch("pathlib.Path.exists", return_value=False)
    @patch("maposcal.generator.control_mapper.get_relevant_chunks", return_value=[])
    @patch("maposcal.generator.control_mapper.LLMHandler")
    def test_retry_logic_succeeds_on_second_attempt(
        self, mock_llm_class, _mock_chunks, _mock_exists
    ):
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance

        # Attempt 0: invalid content (missing explanation + description)
        invalid_response = json.dumps({
            "control-status": "not-a-valid-status",
            "control-explanation": "x",
            "control-configuration": [],
            "statement-description": "x",
        })
        # Attempt 0 error prompt response (discarded by continue)
        # Attempt 1: valid content
        valid_response = json.dumps(VALID_LLM_CONTENT)

        mock_llm_instance.query.side_effect = [
            invalid_response,   # attempt 0 content prompt
            invalid_response,   # attempt 0 error prompt (discarded)
            valid_response,     # attempt 1 content prompt
        ]

        result = map_control(SAMPLE_CONTROL_DICT, "/fake/output")

        assert result["control-id"] == "AC-1"
        status_prop = next(
            p for p in result["props"] if p["name"] == "control-status"
        )
        assert status_prop["value"] == "applicable and inherently satisfied"

    @pytest.mark.unit
    @patch("pathlib.Path.exists", return_value=False)
    @patch("maposcal.generator.control_mapper.get_relevant_chunks", return_value=[])
    @patch("maposcal.generator.control_mapper.LLMHandler")
    def test_all_retries_exhausted_returns_template(
        self, mock_llm_class, _mock_chunks, _mock_exists
    ):
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance

        # All responses are invalid so all retries are consumed
        always_invalid = json.dumps({
            "control-status": "bad-status",
            "control-explanation": "x",
            "control-configuration": [],
            "statement-description": "x",
        })
        mock_llm_instance.query.return_value = always_invalid

        result = map_control(SAMPLE_CONTROL_DICT, "/fake/output")

        # Falls back to the structural template — must still be a valid dict
        # with the control-id and required structural keys
        assert isinstance(result, dict)
        assert result["control-id"] == "AC-1"
        assert "props" in result

    @pytest.mark.unit
    @patch("pathlib.Path.exists", return_value=False)
    @patch("maposcal.generator.control_mapper.get_relevant_chunks", return_value=[])
    @patch("maposcal.generator.control_mapper.LLMHandler")
    def test_custom_llm_config_used(self, mock_llm_class, _mock_chunks, _mock_exists):
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        mock_llm_instance.query.return_value = json.dumps(VALID_LLM_CONTENT)

        llm_config = {"provider": "openai", "model": "gpt-4o", "temperature": 0.0}
        result = map_control(SAMPLE_CONTROL_DICT, "/fake/output", llm_config=llm_config)

        mock_llm_class.assert_called_once_with(provider="openai", model="gpt-4o")
        assert result["control-id"] == "AC-1"
