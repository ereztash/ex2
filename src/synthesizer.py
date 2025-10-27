"""
Blueprint Synthesizer: Stage 3 of the Cognitive Pipeline

This is the CODE GENERATOR of the MakeGPT compiler.
It translates abstract plans (AST) into valid blueprint.json compliant with Make.com Schema 2.1.

Architecture Role: AST → blueprint.json (DSL)

Critical Requirements:
- Absolute schema compliance (Table 2.1 from spec)
- Base64-ready output
- __IMTCONN__ placeholders for HIL linking
"""

import json
import os
from typing import Dict
from openai import OpenAI


class BlueprintSynthesizer:
    """
    Generates valid Make.com blueprint.json from abstract scenario plans.

    This is the most critical component - it must produce schema-compliant
    output 99% of the time to meet reliability requirements.

    The synthesizer enforces:
    - Proper JSON structure per Table 2.1
    - Required fields (id, module, version, metadata.designer)
    - Valid data mapping syntax ({{moduleId.field}})
    - Correct filter/router structures
    """

    def __init__(self, openai_key: str = None):
        """
        Initialize the blueprint synthesizer.

        Args:
            openai_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        api_key = openai_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4"

    def synthesize(self, plan: Dict) -> Dict:
        """
        Generate a valid blueprint.json from an abstract plan.

        This is a DETERMINISTIC TRANSLATION process. The creative work
        happens in the planner; this stage enforces strict schema compliance.

        Args:
            plan: Abstract scenario plan from ScenarioPlanner

        Returns:
            dict: Valid blueprint.json object ready for Base64 encoding

        Raises:
            SynthesisError: If LLM produces invalid blueprint
        """
        system_prompt = self._load_synthesis_prompt()
        schema = self._load_schema_spec()

        # Prepare the synthesis request
        plan_json = json.dumps(plan, indent=2)

        prompt = f"""Generate a valid Make.com blueprint.json from this plan:

{plan_json}

CRITICAL REQUIREMENTS:
1. Follow the schema specification EXACTLY
2. Use __IMTCONN__ placeholders for all connections (user will link manually)
3. Use __IMTHOOK__ placeholders for webhooks
4. Validate ALL required fields before outputting
5. Ensure metadata.designer coordinates are present for each module

Schema Specification:
{schema}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Very low temperature for deterministic output
        )

        blueprint = json.loads(response.choices[0].message.content)

        # Self-validation (ATAOV± loop)
        self._validate_output(blueprint)

        return blueprint

    def _validate_output(self, blueprint: Dict) -> None:
        """
        Internal validation of synthesized blueprint.

        This implements the in-prompt validation logic (ATAOV±).

        Args:
            blueprint: Generated blueprint

        Raises:
            ValueError: If blueprint is invalid
        """
        # Check root structure
        if "name" not in blueprint:
            raise ValueError("Blueprint missing required 'name' field")

        if "flow" not in blueprint or not isinstance(blueprint["flow"], list):
            raise ValueError("Blueprint missing required 'flow' array")

        if "metadata" not in blueprint or "scenario" not in blueprint.get("metadata", {}):
            raise ValueError("Blueprint missing required 'metadata.scenario' object")

        # Check each module
        for module in blueprint["flow"]:
            if "id" not in module:
                raise ValueError(f"Module missing required 'id': {module}")

            if "module" not in module:
                raise ValueError(f"Module {module.get('id')} missing required 'module' field")

            if "version" not in module:
                raise ValueError(f"Module {module.get('id')} missing required 'version' field")

            if "metadata" not in module or "designer" not in module.get("metadata", {}):
                raise ValueError(f"Module {module.get('id')} missing required 'metadata.designer'")

    def _load_synthesis_prompt(self) -> str:
        """Load the synthesis system prompt."""
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "synthesize_prompt.txt"
        )

        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()

        return """You are a Make.com blueprint.json compiler.

Your ONLY job is to translate abstract scenario plans into VALID blueprint.json files.

You are NOT creative - you are DETERMINISTIC. Follow the schema EXACTLY.

Rules:
1. Every module MUST have: id (int), module (str), version (int), metadata.designer (obj with x, y)
2. Root MUST have: name (str), flow (array), metadata.scenario (obj)
3. metadata.scenario MUST have: roundtrips, maxErrors, autoCommit, sequential (all required)
4. Use __IMTCONN__ placeholders for connections (e.g., "__IMTCONN__": 123456)
5. Use __IMTHOOK__ for webhooks
6. Data mappings use {{moduleId.field}} syntax
7. Filters need: name, conditions (array of arrays with a, b, o)
8. Routers need: routes (array of objects with flow arrays)

Output ONLY valid JSON. No explanations. No comments.

Validate your output before returning it."""

    def _load_schema_spec(self) -> str:
        """
        Load the formal schema specification (Table 2.1).

        Returns:
            str: Schema specification for the prompt
        """
        return """
=== MAKE.COM BLUEPRINT SCHEMA 2.1 ===

ROOT LEVEL:
- name: string (required) - scenario name
- flow: array[object] (required) - module array
- metadata.scenario: object (required)
  - roundtrips: integer (required, usually 1)
  - maxErrors: integer (required, usually 3)
  - autoCommit: boolean (required)
  - sequential: boolean (required, true for serial execution)
  - confidential: boolean (optional)
  - dataloss: boolean (optional)
  - dlq: boolean (optional)

MODULE LEVEL (each object in flow array):
- id: integer (required, unique)
- module: string (required, e.g., "google-forms:watchResponses")
- version: integer (required, usually 1)
- parameters: object (module-dependent, contains __IMTCONN__ or __IMTHOOK__)
- mapper: object (optional, defines data mapping from previous modules)
- metadata.designer: object (required)
  - x: integer (required)
  - y: integer (required)
- filter: object (optional, for conditional execution)
  - name: string
  - conditions: array[array[object]]
    - Each condition: {a: value1, b: value2, o: "operator"}
- routes: array[object] (required for Router modules)
  - Each route: {flow: [...]}

EXAMPLE STRUCTURE:
{
  "name": "My Scenario",
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
      "autoCommit": false,
      "sequential": false,
      "confidential": false,
      "dataloss": false,
      "dlq": false
    }
  }
}
"""


class SynthesisError(Exception):
    """Raised when blueprint synthesis fails validation."""
    pass
