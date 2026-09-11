"""Shared Anthropic Claude API asynchronous client helper.

Wraps the Anthropic Async SDK for Stages 3, 4, and 5 (Fixer, Tester,
Documenter) targeting Claude claude-sonnet-4-6.
"""

import json
import logging
import os
import re
from typing import Any, Dict, Optional
import anthropic

logger = logging.getLogger("devmind.anthropic_client")

PRIMARY_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 4096


class AnthropicClientWrapper:
    """Async wrapper around Anthropic SDK with JSON extraction and validation."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._client: Optional[anthropic.AsyncAnthropic] = None

    def get_client(self) -> anthropic.AsyncAnthropic:
        """Returns initialized AsyncAnthropic client or raises error if key is missing."""
        key = self._api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key or not key.strip():
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured in the environment. "
                "Stages 3, 4, and 5 require an Anthropic API key."
            )
        if self._client is None or self._api_key != key:
            self._client = anthropic.AsyncAnthropic(api_key=key.strip())
        return self._client

    async def generate_text(
        self,
        user_prompt: str,
        system_prompt: str = "",
        model: str = PRIMARY_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = 0.2,
    ) -> str:
        """Generates a text completion from Claude asynchronously."""
        client = self.get_client()
        messages = [{"role": "user", "content": user_prompt}]
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text

    async def generate_json(
        self,
        user_prompt: str,
        system_prompt: str = "",
        model: str = PRIMARY_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Generates structured JSON output from Claude asynchronously."""
        json_system = (
            f"{system_prompt}\n\n"
            "CRITICAL: You MUST respond ONLY with a valid, parseable JSON object. "
            "Do NOT include markdown formatting fences (```json), commentary, or preambles."
        ).strip()
        raw_text = await self.generate_text(
            user_prompt=user_prompt,
            system_prompt=json_system,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        clean = raw_text.strip()
        # Strip potential markdown code block fences if present
        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean)
        try:
            return json.loads(clean.strip())
        except json.JSONDecodeError as err:
            logger.error("Failed to parse JSON response from Claude: %s", raw_text)
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Model output could not be parsed as JSON: {err}") from err


# Global singleton instance for easy import across pipeline stages
claude_client = AnthropicClientWrapper()
