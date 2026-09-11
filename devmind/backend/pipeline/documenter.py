"""Stage 5 — Documentation & Inline Annotation using Groq."""

import asyncio
import logging
from typing import Optional
from pipeline.schemas import DocResult
from utils.groq_client import (
    RATE_LIMIT_USER_MESSAGE,
    generate_groq_json,
    is_rate_limit_error,
)

logger = logging.getLogger("devmind.documenter")

DOCUMENTER_SYSTEM_PROMPT = """You are DevMind's Lead Technical Writer and Code Standards Engineer.
Your task is to enrich the provided corrected code with high quality, standard documentation.

Guidelines:
- Add idiomatic docstrings for functions/classes (e.g. Google format for Python, JSDoc for JS/TS).
- Add clear, succinct inline comments for non-trivial logic blocks.
- Add type annotations/hints if applicable to the language.
- Preserve the exact logic and functionality of the code.

You must respond in JSON format with this exact key:
- "documented_code": The complete source code with docstrings and inline comments.
"""


def build_documenter_prompt(fixed_code: str, language: Optional[str] = None) -> str:
    """Constructs prompt for documentation and inline commentary."""
    lang_line = f"Language: {language}" if language else "Detect from code"
    return f"""Add comprehensive docstrings and inline comments to this code:

### Details
{lang_line}

### Code to Document
```
{fixed_code}
```

Respond strictly with a JSON object containing "documented_code".
"""


async def generate_docs(
    fixed_code: str, language: Optional[str] = None
) -> DocResult:
    """Executes Stage 5: Adds docstrings and inline comments using Groq."""
    prompt = build_documenter_prompt(fixed_code, language)
    for attempt in range(2):
        try:
            data = await generate_groq_json(
                prompt=prompt,
                system_prompt=DOCUMENTER_SYSTEM_PROMPT,
                model="llama-3.3-70b-versatile",
                temperature=0.2,
            )
            return DocResult(
                documented_code=data.get("documented_code", fixed_code)
            )
        except Exception as exc:
            if attempt == 0 and is_rate_limit_error(exc):
                logger.warning("Stage 5 Documenter hit 429 rate limit. Retrying in 15 seconds...")
                await asyncio.sleep(15)
                continue

            logger.error("Stage 5 Documenter failed via Groq: %s", exc)
            is_rl = is_rate_limit_error(exc)
            err_msg = RATE_LIMIT_USER_MESSAGE if is_rl else str(exc)
            return DocResult(
                documented_code=fixed_code,
                error=err_msg,
            )
    return DocResult(
        documented_code=fixed_code,
        error=RATE_LIMIT_USER_MESSAGE,
    )
