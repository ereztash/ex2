"""
Make.com API Client: The Morphic Bridge

This module implements the integration with Make.com's API endpoints.

Critical discoveries:
1. Base64 encoding is REQUIRED (Section 4.2)
2. folderId is REQUIRED despite not being documented (Section 4.1, Table 4.1)
3. Error handling with exponential backoff (Section 5.2, Table 5.1)

Reference: Section 4 of the architecture spec
"""

import os
import time
import requests
from typing import Dict, Optional


class MakeAPIClient:
    """
    Client for Make.com API v2.

    Handles:
    - Scenario creation with Base64-encoded blueprints
    - Error handling with retry logic
    - Rate limiting with exponential backoff
    """

    BASE_URL = "https://eu1.make.com/api/v2"

    def __init__(self, api_token: str = None, region: str = "eu1"):
        """
        Initialize Make.com API client.

        Args:
            api_token: Make.com API token (defaults to MAKE_API_TOKEN env var)
            region: Make.com region (eu1, eu2, us1, us2)
        """
        self.api_token = api_token or os.getenv("MAKE_API_TOKEN")
        if not self.api_token:
            raise ValueError("Make.com API token required")

        self.base_url = f"https://{region}.make.com/api/v2"
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

    def create_scenario(
        self,
        blueprint: str,
        team_id: int,
        folder_id: Optional[int] = None,
        name: Optional[str] = None,
        scheduling: Optional[Dict] = None
    ) -> int:
        """
        Create a new scenario from a Base64-encoded blueprint.

        This creates an "unlinked" scenario - user must manually connect
        __IMTCONN__ placeholders in Make.com UI (HIL requirement).

        Args:
            blueprint: Base64-encoded blueprint string
            team_id: Make.com team ID (required)
            folder_id: Folder ID (required despite docs saying optional)
            name: Scenario name (optional)
            scheduling: Scheduling config (defaults to indefinitely)

        Returns:
            int: ID of created scenario

        Raises:
            MakeAPIError: On API errors (with retry for 429/5xx)

        Example:
            >>> client = MakeAPIClient(api_token="...")
            >>> scenario_id = client.create_scenario(
            ...     blueprint="eyJ...",
            ...     team_id=123,
            ...     folder_id=456
            ... )
            >>> print(f"Created scenario: {scenario_id}")
        """
        endpoint = f"{self.base_url}/scenarios"

        payload = {
            "blueprint": blueprint,
            "teamId": team_id,
            "scheduling": scheduling or {"type": "indefinitely"}
        }

        # folderId is REQUIRED (community finding, Table 4.1)
        if folder_id is not None:
            payload["folderId"] = folder_id

        if name:
            payload["name"] = name

        # Retry logic with exponential backoff (Table 5.1)
        max_retries = 3
        base_delay = 2  # seconds

        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )

                # Handle different error codes per Table 5.1
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    scenario_id = data.get("scenario", {}).get("id")
                    if scenario_id:
                        return scenario_id
                    raise MakeAPIError("Response missing scenario ID")

                elif response.status_code == 400:
                    # Bad Request - don't retry
                    raise MakeAPIError(
                        f"Invalid request: {response.text}",
                        status_code=400,
                        response=response.json() if response.text else None
                    )

                elif response.status_code == 401:
                    # Unauthorized - don't retry
                    raise MakeAPIError(
                        "Authentication failed - check API token",
                        status_code=401
                    )

                elif response.status_code == 429:
                    # Rate limit - retry with backoff
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise MakeAPIError(
                        "Rate limit exceeded",
                        status_code=429
                    )

                elif response.status_code >= 500:
                    # Server error - retry with backoff
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise MakeAPIError(
                        f"Server error: {response.text}",
                        status_code=response.status_code
                    )

                else:
                    raise MakeAPIError(
                        f"Unexpected error: {response.status_code} - {response.text}",
                        status_code=response.status_code
                    )

            except requests.RequestException as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise MakeAPIError(f"Request failed: {str(e)}")

        raise MakeAPIError("Max retries exceeded")

    def get_scenario_blueprint(self, scenario_id: int) -> Dict:
        """
        Retrieve the blueprint of an existing scenario.

        Useful for learning from successful scenarios (Section 7.3 feedback loop).

        Args:
            scenario_id: ID of the scenario

        Returns:
            dict: Blueprint JSON object
        """
        endpoint = f"{self.base_url}/scenarios/{scenario_id}/blueprint"

        response = requests.get(
            endpoint,
            headers=self.headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise MakeAPIError(
                f"Failed to get blueprint: {response.status_code}",
                status_code=response.status_code
            )


class MakeAPIError(Exception):
    """
    Exception raised for Make.com API errors.

    Attributes:
        message: Error description
        status_code: HTTP status code
        response: Raw API response (if available)
    """

    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message
