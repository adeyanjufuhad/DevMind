"""Shared Google Gemini API client helper using the official google-genai SDK.

Supports AQ. prefix authentication keys via genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
targeting gemini-2.5-flash for Stages 3, 4, and 5 (Fixer, Tester, Documenter).
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, Optional
from google import genai
from google.genai import types

logger = logging.getLogger("devmind.gemini_client")

PRIMARY_MODEL = "gemini-3.6-flash"
RATE_LIMIT_USER_MESSAGE = "Rate limit reached, please try again in a few minutes"


def is_rate_limit_error(exc: Exception) -> bool:
    """Checks if an exception represents an HTTP 429 rate limit or quota exhaustion."""
    err_str = str(exc).lower()
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return (
        code == 429
        or "429" in err_str
        or "resource_exhausted" in err_str
        or "quota exceeded" in err_str
        or "rate limit" in err_str
        or "ratelimit" in err_str
    )


def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """Initializes official google-genai Client with AQ. or standard key."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or not key.strip():
        raise ValueError(
            "GEMINI_API_KEY is not configured in environment variables. "
            "Stages 3, 4, and 5 require a Gemini API key (AQ. keys supported via google-genai SDK)."
        )
    return genai.Client(api_key=key.strip())


async def generate_gemini_content(
    contents: str,
    system_instruction: str = "",
    model: str = PRIMARY_MODEL,
    temperature: float = 0.2,
) -> str:
    """Asynchronously generates text from gemini-2.5-flash via google-genai SDK."""
    client = get_gemini_client()
    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction if system_instruction else None,
    )

    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
        return response.text or ""
    except Exception:
        # Fallback to thread-pool synchronous execution
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=contents,
            config=config,
        )
        return response.text or ""


async def generate_gemini_json(
    contents: str,
    system_instruction: str = "",
    model: str = PRIMARY_MODEL,
    temperature: float = 0.1,
) -> Dict[str, Any]:
    """Generates structured JSON from gemini-2.5-flash via google-genai SDK."""
    json_sys = (
        f"{system_instruction}\n\n"
        "CRITICAL: Respond ONLY with a valid JSON object. "
        "Do not include markdown code block ticks, commentary, or text outside the JSON."
    ).strip()

    raw_text = await generate_gemini_content(
        contents=contents,
        system_instruction=json_sys,
        model=model,
        temperature=temperature,
    )
    clean = raw_text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)

    try:
        return json.loads(clean.strip())
    except json.JSONDecodeError as err:
        logger.warning("Failed standard JSON parse; attempting regex extraction: %s", err)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Gemini output could not be parsed as JSON: {err}") from err
