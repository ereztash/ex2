"""
Base64 Encoder: Critical Bridge Component

This module implements the Base64 encoding protocol discovered through
community research (zezutom's solution).

This is ESSENTIAL for reliable API transmission - it bypasses all JSON
escaping issues that plague direct JSON string transmission.

Reference: Section 4.2 of the architecture spec
"""

import base64
import json
from typing import Dict, Union


class Base64Encoder:
    """
    Encodes blueprint.json for Make.com API transmission.

    The Make.com API expects the blueprint parameter as a string.
    Direct JSON escaping is error-prone and causes "Invalid JSON" errors.

    Solution (from community): Encode the entire JSON as Base64.
    Make.com's API accepts and correctly decodes Base64-encoded blueprints.

    This is not documented officially but is the de facto working protocol.
    """

    @staticmethod
    def encode(blueprint: Union[Dict, str]) -> str:
        """
        Encode a blueprint as Base64 string.

        Args:
            blueprint: Blueprint dict or JSON string

        Returns:
            str: Base64-encoded blueprint ready for API transmission

        Example:
            >>> encoder = Base64Encoder()
            >>> blueprint = {"name": "Test", "flow": []}
            >>> encoded = encoder.encode(blueprint)
            >>> print(encoded)
            'eyJuYW1lIjogIlRlc3QiLCAiZmxvdyI6IFtdfQ=='
        """
        # Convert dict to JSON string if needed
        if isinstance(blueprint, dict):
            json_str = json.dumps(blueprint, ensure_ascii=False)
        else:
            json_str = blueprint

        # Encode to bytes then to Base64
        json_bytes = json_str.encode('utf-8')
        base64_bytes = base64.b64encode(json_bytes)
        base64_str = base64_bytes.decode('ascii')

        return base64_str

    @staticmethod
    def decode(base64_str: str) -> Dict:
        """
        Decode a Base64-encoded blueprint back to dict.

        This is useful for testing and debugging.

        Args:
            base64_str: Base64-encoded blueprint string

        Returns:
            dict: Decoded blueprint object
        """
        # Decode from Base64 to bytes
        base64_bytes = base64_str.encode('ascii')
        json_bytes = base64.b64decode(base64_bytes)

        # Convert bytes to string then parse JSON
        json_str = json_bytes.decode('utf-8')
        blueprint = json.loads(json_str)

        return blueprint

    @staticmethod
    def validate_encoding(blueprint: Dict) -> bool:
        """
        Validate that a blueprint can be encoded and decoded correctly.

        This is a round-trip test to ensure data integrity.

        Args:
            blueprint: Blueprint to validate

        Returns:
            bool: True if encoding/decoding preserves data
        """
        try:
            # Encode
            encoded = Base64Encoder.encode(blueprint)

            # Decode
            decoded = Base64Encoder.decode(encoded)

            # Compare
            return blueprint == decoded

        except Exception:
            return False
