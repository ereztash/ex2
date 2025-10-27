"""
Scenario Planner: Stage 2 of the Cognitive Pipeline

This module generates an Abstract Syntax Tree (AST) representation of the automation flow.
It translates structured intent into a logical execution plan.

Architecture Role: Intent JSON → AST (Plan Document)
"""

import json
import os
from typing import Dict, List
from openai import OpenAI


class ScenarioPlanner:
    """
    Creates abstract scenario plans from structured intents.

    The planner determines:
    - Module sequence and dependencies
    - Control flow structures (routers, filters)
    - Data mapping strategy
    - Error handling placement
    """

    def __init__(self, openai_key: str = None):
        """
        Initialize the scenario planner.

        Args:
            openai_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        api_key = openai_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4"

    def create_plan(self, intent: Dict) -> Dict:
        """
        Generate an abstract scenario plan from structured intent.

        Args:
            intent: Structured intent object from IntentParser

        Returns:
            dict: Abstract plan with keys:
                - modules: [{id, type, purpose, config}, ...]
                - flow: {edges, dependencies}
                - metadata: {sequential, max_errors, roundtrips}

        Example:
            >>> planner = ScenarioPlanner()
            >>> plan = planner.create_plan(intent)
            >>> print(plan["modules"])
            [
                {"id": 1, "type": "trigger", "module": "google-forms:watchResponses"},
                {"id": 2, "type": "action", "module": "gmail:sendEmail"},
                ...
            ]
        """
        system_prompt = self._load_plan_prompt()

        # Convert intent to JSON string for the prompt
        intent_json = json.dumps(intent, indent=2)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a scenario plan for this intent:\n\n{intent_json}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2  # Lower temperature for more deterministic planning
        )

        plan = json.loads(response.choices[0].message.content)
        return plan

    def _load_plan_prompt(self) -> str:
        """
        Load the planning system prompt.

        Returns:
            str: System prompt for scenario planning
        """
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "plan_prompt.txt"
        )

        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()

        # Fallback to embedded prompt
        return """You are an expert Make.com scenario architect.

Your task is to create a detailed execution plan (AST) for a Make.com automation scenario.

Given a structured intent, you must design the module sequence, data flow, and control logic.

Return a JSON object with this structure:

{
  "modules": [
    {
      "id": 1,
      "type": "trigger|action|router|filter|error_handler",
      "module": "exact-make-module-name",
      "purpose": "what this module does",
      "config": {
        "parameters": {},
        "connections_needed": ["app1", "app2"]
      },
      "position": {"x": 0, "y": 0}
    }
  ],
  "flow": {
    "edges": [
      {"from": 1, "to": 2, "data_mapping": {"field1": "{{1.field1}}"}}
    ],
    "dependencies": [[1, 2], [2, 3]]
  },
  "error_handling": {
    "modules_with_retry": [2, 3],
    "break_config": {"attempts": 3, "interval": 60}
  },
  "metadata": {
    "sequential": false,
    "max_errors": 3,
    "roundtrips": 1,
    "auto_commit": false
  }
}

Design Principles:
1. First module (id: 1) must be a trigger or webhook
2. Assign unique sequential IDs to each module
3. Position modules in a readable left-to-right flow (x += 150 for each)
4. For conditional logic, use builtin:BasicRouter with routes
5. For data validation, use filters with conditions
6. For API calls, add error handling with Break modules
7. Map data between modules using {{moduleId.fieldName}} syntax

Common Make.com modules:
- Triggers: google-forms:watchResponses, google-sheets:watchUpdatedCells, http:webhookEvent
- Actions: gmail:sendEmail, google-sheets:addRow, slack:sendMessage
- Control: builtin:BasicRouter, util:SetVariable2
- Error: Break (with retry logic)

Think step-by-step about the automation flow before generating the plan."""
