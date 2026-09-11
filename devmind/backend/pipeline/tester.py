"""Stage 4 — Unit Test Suite Generation using Gemini 2.5 Flash."""

import logging
from typing import Optional
from pipeline.schemas import TestResult
from utils.gemini_client import generate_gemini_json

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
    """Executes Stage 4: Generates unit tests via google-genai using gemini-2.5-flash."""
    prompt = build_tester_prompt(fixed_code, language)
    try:
        data = await generate_gemini_json(
            contents=prompt,
            system_instruction=TESTER_SYSTEM_PROMPT,
            model="gemini-3.6-flash",
            temperature=0.2,
        )
        return TestResult(
            framework=data.get("framework", "standard"),
            tests=data.get("tests", "# No tests generated."),
        )
    except Exception as exc:
        logger.error("Stage 4 Tester failed via google-genai: %s", exc)
        return TestResult(
            framework="unknown",
            tests="# Test generation could not complete due to an error.",
            error=str(exc),
        )
