"""
Intent Parser: Stage 1 of the Cognitive Pipeline

This module implements the lexical/syntactic analysis phase of the MakeGPT compiler.
It converts free-form natural language into structured intent objects.

Architecture Role: Source Code → Intent JSON
"""

import json
import os
from typing import Dict, List, Optional
from openai import OpenAI


class IntentParser:
    """
    Analyzes natural language and extracts structured automation intent.

    The parser identifies:
    - Trigger applications and events
    - Action applications and operations
    - Data flow requirements
    - Business logic conditions
    """

    def __init__(self, openai_key: str = None):
        """
        Initialize the intent parser.

        Args:
            openai_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        api_key = openai_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4"

    def parse(self, user_input: str) -> Dict:
        """
        Parse natural language into structured intent.

        Args:
            user_input: User's automation request in natural language

        Returns:
            dict: Structured intent with keys:
                - trigger: {app, event, description}
                - actions: [{app, operation, description}, ...]
                - logic: {routing, filtering, error_handling}
                - entities: {variables, connections, data_mappings}

        Example:
            >>> parser = IntentParser()
            >>> intent = parser.parse("Send email when new form submitted")
            >>> print(intent)
            {
                "trigger": {"app": "google-forms", "event": "watchResponses"},
                "actions": [{"app": "email", "operation": "send"}],
                ...
            }
        """
        system_prompt = self._load_intent_prompt()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        intent = json.loads(response.choices[0].message.content)
        return intent

    def _load_intent_prompt(self) -> str:
        """
        Load the intent parsing system prompt.

        Returns:
            str: System prompt for intent analysis
        """
        # Try to load from file first
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "intent_prompt.txt"
        )

        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()

        # Fallback to embedded prompt
        return """You are an expert at analyzing automation intents for Make.com.

Your task is to parse the user's natural language request and extract structured information.

Analyze the request and return a JSON object with this exact structure:

{
  "trigger": {
    "app": "application-name",
    "event": "trigger-event",
    "description": "what triggers this automation"
  },
  "actions": [
    {
      "app": "application-name",
      "operation": "action-to-perform",
      "description": "what this action does"
    }
  ],
  "logic": {
    "routing": "conditional routing logic if any",
    "filtering": "filtering conditions if any",
    "error_handling": "error handling requirements",
    "sequential": false
  },
  "entities": {
    "variables": ["list", "of", "data", "fields"],
    "connections": ["apps", "that", "need", "connections"],
    "data_mappings": {"source": "destination"}
  }
}

Common Make.com apps:
- google-forms, google-sheets, google-calendar, gmail
- slack, microsoft-teams
- dropbox, google-drive
- http (for webhooks and API calls)
- builtin:BasicRouter (for conditional routing)

Be specific and technical. Identify exact Make.com module names when possible."""
