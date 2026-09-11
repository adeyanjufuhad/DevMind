"""Stage 4 — Unit Test Suite Generation using Groq."""

import asyncio
import logging
from typing import Optional
from pipeline.schemas import TestResult
from utils.groq_client import (
    RATE_LIMIT_USER_MESSAGE,
    generate_groq_json,
    is_rate_limit_error,
)

logger = logging.getLogger("devmind.tester")

TESTER_SYSTEM_PROMPT = """You are DevMind's Principal QA & Test Automation Engineer.
Your task is to write comprehensive, idiomatic unit tests for the provided corrected code.

Guidelines:
- Choose the standard testing framework (e.g. pytest for Python, Jest for JS/TS, testing package for Go).
- Include happy path, boundary checks, and error/edge case tests.
- Write clear test function names with assertions.

You must respond in JSON format with these exact keys:
- "framework": The framework used (e.g. "pytest", "jest").
- "tests": Complete, executable unit test code with imports and assertions.
"""


def build_tester_prompt(fixed_code: str, language: Optional[str] = None) -> str:
    """Constructs prompt for test suite generation."""
    lang_line = f"Language: {language}" if language else "Detect from code"
    return f"""Generate comprehensive unit tests for this corrected code:

### Details
{lang_line}

### Corrected Code
```
{fixed_code}
```

Respond strictly with a JSON object containing "framework" and "tests".
"""


async def generate_tests(
    fixed_code: str, language: Optional[str] = None
) -> TestResult:
    """Executes Stage 4: Generates unit tests via Groq using llama-3.3-70b-versatile."""
    prompt = build_tester_prompt(fixed_code, language)
    for attempt in range(2):
        try:
            data = await generate_groq_json(
                prompt=prompt,
                system_prompt=TESTER_SYSTEM_PROMPT,
                model="llama-3.3-70b-versatile",
                temperature=0.2,
            )
            return TestResult(
                framework=data.get("framework", "standard"),
                tests=data.get("tests", "# No tests generated."),
            )
        except Exception as exc:
            if attempt == 0 and is_rate_limit_error(exc):
                logger.warning("Stage 4 Tester hit 429 rate limit. Retrying in 15 seconds...")
                await asyncio.sleep(15)
                continue

            logger.error("Stage 4 Tester failed via Groq: %s", exc)
            is_rl = is_rate_limit_error(exc)
            err_msg = RATE_LIMIT_USER_MESSAGE if is_rl else str(exc)
            return TestResult(
                framework="unknown",
                tests=f"# {err_msg}",
                error=err_msg,
            )
    return TestResult(
        framework="unknown",
        tests=f"# {RATE_LIMIT_USER_MESSAGE}",
        error=RATE_LIMIT_USER_MESSAGE,
    )
