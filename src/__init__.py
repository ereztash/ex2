"""
MakeGPT: Intent-Driven Scenario Synthesizer for Make.com

This package provides an AI-powered compiler that translates natural language
user intentions into executable Make.com scenarios.

Architecture:
    User Intent → IntentParser → Planner → Synthesizer → Blueprint → Make.com API

Components:
    - IntentParser: Analyzes natural language and extracts structured intent
    - Planner: Creates an abstract scenario plan (AST)
    - Synthesizer: Generates valid blueprint.json from the plan
    - Encoder: Base64 encoding for API transmission
    - MakeAPI: Interface to Make.com API endpoints
    - SchemaValidator: Validates blueprints against Make.com schema
"""

from .intent_parser import IntentParser
from .planner import ScenarioPlanner
from .synthesizer import BlueprintSynthesizer
from .encoder import Base64Encoder
from .make_api import MakeAPIClient
from .schema_validator import BlueprintValidator

__version__ = "0.1.0"
__author__ = "MakeGPT Team"

__all__ = [
    "IntentParser",
    "ScenarioPlanner",
    "BlueprintSynthesizer",
    "Base64Encoder",
    "MakeAPIClient",
    "BlueprintValidator",
]


class MakeGPT:
    """
    Main compiler class that orchestrates the entire pipeline.

    This class implements the Human-in-the-Loop (HIL) architecture,
    producing unlinked blueprints that require manual connection linking.

    Example:
        >>> compiler = MakeGPT(openai_key="sk-...", make_token="...")
        >>> blueprint = compiler.compile("Send email when form submitted")
        >>> scenario_id = compiler.deploy(blueprint, team_id=123, folder_id=456)
    """

    def __init__(self, openai_key: str = None, make_token: str = None):
        """
        Initialize the MakeGPT compiler.

        Args:
            openai_key: OpenAI API key for LLM operations
            make_token: Make.com API token for deployment
        """
        self.intent_parser = IntentParser(openai_key=openai_key)
        self.planner = ScenarioPlanner(openai_key=openai_key)
        self.synthesizer = BlueprintSynthesizer(openai_key=openai_key)
        self.encoder = Base64Encoder()
        self.validator = BlueprintValidator()
        self.api_client = MakeAPIClient(api_token=make_token)

    def compile(self, user_intent: str) -> dict:
        """
        Compile natural language intent into a Make.com blueprint.

        This is the core compilation pipeline: Intent → Plan → Synthesis

        Args:
            user_intent: Natural language description of desired automation

        Returns:
            dict: Valid blueprint.json object

        Raises:
            ValidationError: If generated blueprint is invalid
        """
        # Stage 1: Parse intent
        intent = self.intent_parser.parse(user_intent)

        # Stage 2: Generate plan (AST)
        plan = self.planner.create_plan(intent)

        # Stage 3: Synthesize blueprint
        blueprint = self.synthesizer.synthesize(plan)

        # Validate before returning
        self.validator.validate(blueprint)

        return blueprint

    def deploy(self, blueprint: dict, team_id: int, folder_id: int = None,
               scenario_name: str = None) -> int:
        """
        Deploy a blueprint to Make.com (creates unlinked scenario).

        Note: This creates an "unlinked" scenario. User must manually
        connect __IMTCONN__ placeholders in Make.com UI (HIL requirement).

        Args:
            blueprint: Valid blueprint.json object
            team_id: Make.com team ID
            folder_id: Target folder ID (optional)
            scenario_name: Custom name (optional, uses blueprint name if not provided)

        Returns:
            int: ID of created scenario
        """
        # Encode blueprint as Base64 (critical for API transmission)
        blueprint_b64 = self.encoder.encode(blueprint)

        # Deploy via API
        scenario_id = self.api_client.create_scenario(
            blueprint=blueprint_b64,
            team_id=team_id,
            folder_id=folder_id,
            name=scenario_name or blueprint.get("name", "MakeGPT Scenario")
        )

        return scenario_id
