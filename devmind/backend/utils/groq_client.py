"""Shared Groq API client helper using the official groq SDK.

Supports Llama 3.3 70B Versatile for Stages 3, 4, and 5 (Fixer, Tester, Documenter).
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, Optional
from groq import Groq

logger = logging.getLogger("devmind.groq_client")

PRIMARY_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
FALLBACK_MODEL = "groq/compound"
RATE_LIMIT_USER_MESSAGE = "Rate limit reached, please try again in a few minutes"


def get_groq_client(api_key: Optional[str] = None) -> Groq:
    """Initializes official Groq client with GROQ_API_KEY."""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key or not key.strip():
        raise ValueError(
            "GROQ_API_KEY is not configured in environment variables. "
            "Stages 3, 4, and 5 require a Groq API key."
        )
    return Groq(api_key=key.strip())


def is_rate_limit_error(exc: Exception) -> bool:
    """Checks if an exception represents an HTTP 429 rate limit or quota exhaustion."""
    err_str = str(exc).lower()
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    return (
        code == 429
        or "429" in err_str
        or "rate_limit" in err_str
        or "rate limit" in err_str
        or "ratelimit" in err_str
        or "resource_exhausted" in err_str
        or "quota exceeded" in err_str
        or "tokens per minute" in err_str
        or "requests per minute" in err_str
    )


async def generate_groq_completion(
    prompt: str,
    system_prompt: str = "",
    model: str = PRIMARY_MODEL,
    temperature: float = 0.2,
) -> str:
    """Generates text completion via Groq using non-blocking thread-pool."""
    client = get_groq_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    def _call(target_model: str):
        resp = client.chat.completions.create(
            model=target_model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    try:
        return await asyncio.to_thread(_call, model)
    except Exception as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            logger.warning("Model %s not found on tier. Falling back to %s", model, FALLBACK_MODEL)
            return await asyncio.to_thread(_call, FALLBACK_MODEL)
        raise


async def generate_groq_json(
    prompt: str,
    system_prompt: str = "",
    model: str = PRIMARY_MODEL,
    temperature: float = 0.1,
) -> Dict[str, Any]:
    """Generates structured JSON from Groq chat completion."""
    json_sys = (
        f"{system_prompt}\n\n"
        "CRITICAL: Respond ONLY with a valid JSON object. "
        "Do not include markdown code block ticks, commentary, or text outside the JSON."
    ).strip()

    raw_text = await generate_groq_completion(
        prompt=prompt,
        system_prompt=json_sys,
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
        raise ValueError(f"Groq output could not be parsed as JSON: {err}") from err
