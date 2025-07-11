"""
Tests for the profile_control_extractor module.

This module tests the ProfileControlExtractor class functionality for
extracting control parameters from OSCAL catalogs and profiles.
"""

import pytest
import json
import tempfile
from pathlib import Path
from maposcal.generator.profile_control_extractor import ProfileControlExtractor


class TestProfileControlExtractor:
    """Test the ProfileControlExtractor class."""

    @pytest.fixture
    def sample_catalog(self):
        """Create a sample OSCAL catalog for testing."""
        return {
            "catalog": {
                "controls": [
                    {
                        "id": "ac-1",
                        "title": "Access Control Policy",
                        "parts": [
                            {
                                "name": "statement",
                                "prose": "The organization develops, disseminates, and reviews/updates access control policies.",
                            }
                        ],
                        "params": [
                            {
                                "id": "ac-1_prm_1",
                                "label": "Timeframe",
                                "guidelines": [
                                    {
                                        "prose": "The organization immediately develops, disseminates, and reviews/updates access control policies."
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "id": "sc-8",
                        "title": "Transmission Confidentiality and Integrity",
                        "parts": [
                            {
                                "name": "statement",
                                "prose": "The information system protects the confidentiality and integrity of transmitted information.",
                            }
                        ],
                    },
                ],
                "groups": [
                    {
                        "id": "ac",
                        "title": "Access Control",
                        "controls": [
                            {
                                "id": "ac-2",
                                "title": "Account Management",
                                "parts": [
                                    {
                                        "name": "statement",
                                        "prose": "The organization manages information system accounts.",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        }

    @pytest.fixture
    def sample_profile(self):
        """Create a sample OSCAL profile for testing."""
        return {
            "profile": {
                "modify": {
                    "set-parameters": [
                        {
                            "param-id": "ac-1_prm_1",
                            "constraints": [{"description": "immediately"}],
                        }
                    ]
                }
            }
        }

    def test_profile_control_extractor_initialization(
        self, sample_catalog, sample_profile
    ):
        """Test ProfileControlExtractor initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))

            assert extractor.catalog == sample_catalog
            assert extractor.profile == sample_profile
            assert "ac-1" in extractor.catalog_controls
            assert "sc-8" in extractor.catalog_controls
            assert "ac-2" in extractor.catalog_controls
            assert "ac-1_prm_1" in extractor.profile_params

    def test_extract_control_parameters_basic(self, sample_catalog, sample_profile):
        """Test basic control parameter extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert result["id"] == "ac-1"
            assert result["title"] == "Access Control Policy"
            assert len(result["statement"]) == 1
            assert (
                "develops, disseminates, and reviews/updates" in result["statement"][0]
            )
            assert len(result["params"]) == 1
            assert result["params"][0]["id"] == "ac-1_prm_1"
            assert result["params"][0]["label"] == "Timeframe"
            assert len(result["params"][0]["resolved-values"]) == 1
            assert result["params"][0]["resolved-values"][0] == "immediately"
            assert len(result["params"][0]["prose"]) == 1
            assert "immediately develops" in result["params"][0]["prose"][0]

    def test_extract_control_parameters_no_params(self, sample_catalog, sample_profile):
        """Test control parameter extraction for control without parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("sc-8")

            assert result["id"] == "sc-8"
            assert result["title"] == "Transmission Confidentiality and Integrity"
            assert len(result["statement"]) == 1
            assert (
                "protects the confidentiality and integrity" in result["statement"][0]
            )
            assert len(result["params"]) == 0

    def test_extract_control_parameters_nested_statement(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction with nested statement parts."""
        # Modify catalog to have nested statement parts
        nested_catalog = sample_catalog.copy()
        nested_catalog["catalog"]["controls"][0]["parts"][0] = {
            "name": "statement",
            "parts": [
                {
                    "name": "item",
                    "prose": "The organization develops access control policies.",
                },
                {
                    "name": "item",
                    "prose": "The organization disseminates access control policies.",
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(nested_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert len(result["statement"]) == 2
            assert "develops access control policies" in result["statement"][0]
            assert "disseminates access control policies" in result["statement"][1]

    def test_extract_control_parameters_mixed_statement(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction with mixed flat and nested statement parts."""
        # Modify catalog to have both flat and nested statement parts
        mixed_catalog = sample_catalog.copy()
        mixed_catalog["catalog"]["controls"][0]["parts"][0] = {
            "name": "statement",
            "prose": "The organization develops access control policies.",
            "parts": [
                {
                    "name": "item",
                    "prose": "The organization disseminates access control policies.",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(mixed_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert len(result["statement"]) == 2
            assert "develops access control policies" in result["statement"][0]
            assert "disseminates access control policies" in result["statement"][1]

    def test_extract_control_parameters_grouped_control(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction for controls in groups."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-2")

            assert result["id"] == "ac-2"
            assert result["title"] == "Account Management"
            assert len(result["statement"]) == 1
            assert "manages information system accounts" in result["statement"][0]

    def test_extract_control_parameters_nonexistent_control(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction for non-existent control."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("nonexistent-control")

            assert result is None

    def test_extract_control_parameters_no_statement(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction for control without statement."""
        # Modify catalog to remove statement from control
        no_statement_catalog = sample_catalog.copy()
        no_statement_catalog["catalog"]["controls"][0]["parts"] = []

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(no_statement_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert result["id"] == "ac-1"
            assert result["title"] == "Access Control Policy"
            assert len(result["statement"]) == 0

    def test_extract_control_parameters_multiple_resolved_values(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction with multiple resolved values."""
        # Modify profile to have multiple resolved values
        multi_value_profile = sample_profile.copy()
        multi_value_profile["profile"]["modify"]["set-parameters"][0]["values"] = [
            "immediately",
            "within 30 days",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(multi_value_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert (
                len(result["params"][0]["resolved-values"]) == 3
            )  # 1 from constraints + 2 from values
            assert "immediately" in result["params"][0]["resolved-values"]
            assert "within 30 days" in result["params"][0]["resolved-values"]

    def test_extract_control_parameters_value_field(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction with value field in profile."""
        # Modify profile to use value field instead of constraints
        value_profile = sample_profile.copy()
        value_profile["profile"]["modify"]["set-parameters"][0] = {
            "param-id": "ac-1_prm_1",
            "value": "immediately",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(value_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert len(result["params"][0]["resolved-values"]) == 1
            assert result["params"][0]["resolved-values"][0] == "immediately"

    def test_extract_control_parameters_param_with_prose(
        self, sample_catalog, sample_profile
    ):
        """Test control parameter extraction for parameter with prose field."""
        # Modify catalog to add prose to parameter
        prose_catalog = sample_catalog.copy()
        prose_catalog["catalog"]["controls"][0]["params"][0]["prose"] = (
            "Default prose value"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(prose_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(sample_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert (
                len(result["params"][0]["prose"]) == 2
            )  # 1 from guidelines + 1 from prose
            assert "Default prose value" in result["params"][0]["prose"]

    def test_extract_control_parameters_no_profile_params(self, sample_catalog):
        """Test control parameter extraction with profile that has no parameters."""
        empty_profile = {"profile": {"modify": {"set-parameters": []}}}

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(sample_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(empty_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert result["id"] == "ac-1"
            assert len(result["params"]) == 1
            assert len(result["params"][0]["resolved-values"]) == 0  # No profile values
            assert len(result["params"][0]["prose"]) == 1  # Only catalog prose

    def test_extract_control_parameters_empty_catalog(self):
        """Test control parameter extraction with empty catalog."""
        empty_catalog = {"catalog": {"controls": [], "groups": []}}

        empty_profile = {"profile": {"modify": {"set-parameters": []}}}

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(empty_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(empty_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert result is None

    def test_extract_control_parameters_malformed_catalog(self):
        """Test control parameter extraction with malformed catalog."""
        malformed_catalog = {
            "catalog": {
                "controls": [
                    {
                        "id": "ac-1",
                        "title": "Access Control Policy",
                        # Missing parts and params
                    }
                ]
            }
        }

        empty_profile = {"profile": {"modify": {"set-parameters": []}}}

        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            with open(catalog_path, "w") as f:
                json.dump(malformed_catalog, f)
            with open(profile_path, "w") as f:
                json.dump(empty_profile, f)

            extractor = ProfileControlExtractor(str(catalog_path), str(profile_path))
            result = extractor.extract_control_parameters("ac-1")

            assert result["id"] == "ac-1"
            assert result["title"] == "Access Control Policy"
            assert len(result["statement"]) == 0
            assert len(result["params"]) == 0


class TestProfileControlExtractorErrorHandling:
    """Test error handling in ProfileControlExtractor."""

    def test_profile_control_extractor_missing_catalog_file(self):
        """Test ProfileControlExtractor with missing catalog file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "nonexistent_catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            # Create only profile file
            with open(profile_path, "w") as f:
                json.dump({"profile": {"modify": {"set-parameters": []}}}, f)

            with pytest.raises(FileNotFoundError):
                ProfileControlExtractor(str(catalog_path), str(profile_path))

    def test_profile_control_extractor_missing_profile_file(self):
        """Test ProfileControlExtractor with missing profile file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "nonexistent_profile.json"

            # Create only catalog file
            with open(catalog_path, "w") as f:
                json.dump({"catalog": {"controls": []}}, f)

            with pytest.raises(FileNotFoundError):
                ProfileControlExtractor(str(catalog_path), str(profile_path))

    def test_profile_control_extractor_invalid_json_catalog(self):
        """Test ProfileControlExtractor with invalid JSON in catalog file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            # Write invalid JSON
            with open(catalog_path, "w") as f:
                f.write("{ invalid json }")
            with open(profile_path, "w") as f:
                json.dump({"profile": {"modify": {"set-parameters": []}}}, f)

            with pytest.raises(json.JSONDecodeError):
                ProfileControlExtractor(str(catalog_path), str(profile_path))

    def test_profile_control_extractor_invalid_json_profile(self):
        """Test ProfileControlExtractor with invalid JSON in profile file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            profile_path = Path(temp_dir) / "profile.json"

            # Write invalid JSON
            with open(catalog_path, "w") as f:
                json.dump({"catalog": {"controls": []}}, f)
            with open(profile_path, "w") as f:
                f.write("{ invalid json }")

            with pytest.raises(json.JSONDecodeError):
                ProfileControlExtractor(str(catalog_path), str(profile_path))
