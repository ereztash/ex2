"""
Tests for Base64 encoder module.

Critical component - must ensure data integrity during encoding/decoding.
"""

import pytest
from src.encoder import Base64Encoder


class TestBase64Encoder:
    """Test suite for Base64 encoder."""

    def test_encode_simple_blueprint(self):
        """Test encoding a simple blueprint."""
        blueprint = {
            "name": "Test Scenario",
            "flow": [],
            "metadata": {"scenario": {}}
        }

        encoded = Base64Encoder.encode(blueprint)

        # Should be a string
        assert isinstance(encoded, str)
        # Should be Base64 (only contains valid Base64 characters)
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
                   for c in encoded)

    def test_decode_simple_blueprint(self):
        """Test decoding a Base64-encoded blueprint."""
        blueprint = {
            "name": "Test Scenario",
            "flow": [],
            "metadata": {"scenario": {}}
        }

        encoded = Base64Encoder.encode(blueprint)
        decoded = Base64Encoder.decode(encoded)

        assert decoded == blueprint

    def test_round_trip_preserves_data(self):
        """Test that encode→decode preserves data integrity."""
        blueprint = {
            "name": "Complex Scenario",
            "flow": [
                {
                    "id": 1,
                    "module": "google-forms:watchResponses",
                    "version": 1,
                    "parameters": {"__IMTCONN__": 123456},
                    "mapper": {},
                    "metadata": {"designer": {"x": 0, "y": 0}}
                }
            ],
            "metadata": {
                "version": 1,
                "scenario": {
                    "roundtrips": 1,
                    "maxErrors": 3,
                    "autoCommit": False,
                    "sequential": False
                }
            }
        }

        # Encode and decode
        encoded = Base64Encoder.encode(blueprint)
        decoded = Base64Encoder.decode(encoded)

        # Should be identical
        assert decoded == blueprint

    def test_validate_encoding(self):
        """Test the validation method."""
        blueprint = {
            "name": "Test",
            "flow": [],
            "metadata": {"scenario": {}}
        }

        # Should validate successfully
        assert Base64Encoder.validate_encoding(blueprint) is True

    def test_unicode_handling(self):
        """Test that Unicode characters are handled correctly."""
        blueprint = {
            "name": "תרחיש בדיקה",  # Hebrew
            "description": "Тест сценарий",  # Russian
            "flow": [],
            "metadata": {"scenario": {}}
        }

        encoded = Base64Encoder.encode(blueprint)
        decoded = Base64Encoder.decode(encoded)

        assert decoded == blueprint
        assert decoded["name"] == "תרחיש בדיקה"
