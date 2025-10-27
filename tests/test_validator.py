"""
Tests for blueprint schema validator.

These tests ensure the validator correctly enforces Make.com Schema 2.1.
"""

import pytest
from src.schema_validator import BlueprintValidator, ValidationError


class TestBlueprintValidator:
    """Test suite for blueprint validator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = BlueprintValidator()

    def test_valid_minimal_blueprint(self):
        """Test validation of a minimal valid blueprint."""
        blueprint = {
            "name": "Test Scenario",
            "flow": [
                {
                    "id": 1,
                    "module": "google-forms:watchResponses",
                    "version": 1,
                    "metadata": {"designer": {"x": 0, "y": 0}}
                }
            ],
            "metadata": {
                "scenario": {
                    "roundtrips": 1,
                    "maxErrors": 3,
                    "autoCommit": False,
                    "sequential": False
                }
            }
        }

        # Should not raise
        assert self.validator.validate(blueprint) is True

    def test_missing_name_fails(self):
        """Test that missing 'name' field fails validation."""
        blueprint = {
            "flow": [
                {
                    "id": 1,
                    "module": "test",
                    "version": 1,
                    "metadata": {"designer": {"x": 0, "y": 0}}
                }
            ],
            "metadata": {"scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": False,
                "sequential": False
            }}
        }

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate(blueprint)

        assert "name" in str(exc_info.value).lower()

    def test_missing_flow_fails(self):
        """Test that missing 'flow' field fails validation."""
        blueprint = {
            "name": "Test",
            "metadata": {"scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": False,
                "sequential": False
            }}
        }

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate(blueprint)

        assert "flow" in str(exc_info.value).lower()

    def test_empty_flow_fails(self):
        """Test that empty flow array fails validation."""
        blueprint = {
            "name": "Test",
            "flow": [],
            "metadata": {"scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": False,
                "sequential": False
            }}
        }

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate(blueprint)

        assert "empty" in str(exc_info.value).lower()

    def test_module_missing_id_fails(self):
        """Test that module without 'id' fails validation."""
        blueprint = {
            "name": "Test",
            "flow": [
                {
                    "module": "test",
                    "version": 1,
                    "metadata": {"designer": {"x": 0, "y": 0}}
                }
            ],
            "metadata": {"scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": False,
                "sequential": False
            }}
        }

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate(blueprint)

        assert "id" in str(exc_info.value).lower()

    def test_module_missing_designer_fails(self):
        """Test that module without metadata.designer fails validation."""
        blueprint = {
            "name": "Test",
            "flow": [
                {
                    "id": 1,
                    "module": "test",
                    "version": 1,
                    "metadata": {}
                }
            ],
            "metadata": {"scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": False,
                "sequential": False
            }}
        }

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate(blueprint)

        assert "designer" in str(exc_info.value).lower()

    def test_duplicate_module_ids_fails(self):
        """Test that duplicate module IDs fail validation."""
        blueprint = {
            "name": "Test",
            "flow": [
                {
                    "id": 1,
                    "module": "test1",
                    "version": 1,
                    "metadata": {"designer": {"x": 0, "y": 0}}
                },
                {
                    "id": 1,  # Duplicate!
                    "module": "test2",
                    "version": 1,
                    "metadata": {"designer": {"x": 150, "y": 0}}
                }
            ],
            "metadata": {"scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": False,
                "sequential": False
            }}
        }

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate(blueprint)

        assert "duplicate" in str(exc_info.value).lower()

    def test_missing_scenario_metadata_fails(self):
        """Test that missing metadata.scenario fails validation."""
        blueprint = {
            "name": "Test",
            "flow": [
                {
                    "id": 1,
                    "module": "test",
                    "version": 1,
                    "metadata": {"designer": {"x": 0, "y": 0}}
                }
            ],
            "metadata": {}
        }

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate(blueprint)

        assert "scenario" in str(exc_info.value).lower()
