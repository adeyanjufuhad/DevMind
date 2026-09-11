"""Stage 3 — Bug Diagnosis, Code Repair & Junior Explanation using Groq."""

import asyncio
import logging
from typing import Optional
from pipeline.schemas import ClassificationResult, FixResult, SummaryResult
from utils.groq_client import (
    RATE_LIMIT_USER_MESSAGE,
    generate_groq_json,
    is_rate_limit_error,
)

logger = logging.getLogger("devmind.fixer")

FIXER_SYSTEM_PROMPT = """You are DevMind's Senior Staff Debugging Engineer.
Your task is to analyze problematic code, identify the root cause of the defect,
generate a clean and correct production fix, and explain the problem clearly so a
junior developer can understand and learn from it.

You must respond in JSON format with these exact keys:
- "root_cause": Clear explanation of what is wrong and why it fails.
- "fixed_code": The complete corrected source code (ready to run).
- "explanation": A friendly, intuitive walkthrough of the fix for a junior dev.
"""


def build_fixer_prompt(
    code: str,
    classification: Optional[ClassificationResult] = None,
    summary: Optional[SummaryResult] = None,
) -> str:
    """Constructs contextual prompt with Stage 1 & 2 metadata if available."""
    context_lines = []
    if classification:
        context_lines.append(f"Detected Language: {classification.language}")
        context_lines.append(f"Error Category: {classification.error_type}")
    if summary:
        context_lines.append(f"Code Intent Summary: {summary.summary}")
        if summary.key_elements:
            context_lines.append(f"Key Elements: {', '.join(summary.key_elements)}")

    context_block = "\n".join(context_lines) if context_lines else "None provided"

    return f"""Please diagnose and fix this code:

### Pipeline Context
{context_block}

### Original Code
```
{code}
```

Return your diagnosis, fixed code, and explanation in JSON.
"""


async def fix_code(
    code: str,
    classification: Optional[ClassificationResult] = None,
    summary: Optional[SummaryResult] = None,
) -> FixResult:
    """Executes Stage 3: Diagnoses the bug and generates a fix using Groq."""
    prompt = build_fixer_prompt(code, classification, summary)
    for attempt in range(2):
        try:
            data = await generate_groq_json(
                prompt=prompt,
                system_prompt=FIXER_SYSTEM_PROMPT,
                model="llama-3.3-70b-versatile",
                temperature=0.2,
            )
            return FixResult(
                root_cause=data.get("root_cause", "Root cause identified."),
                fixed_code=data.get("fixed_code", code),
                explanation=data.get("explanation", "Fix applied successfully."),
            )
        except Exception as exc:
            if attempt == 0 and is_rate_limit_error(exc):
                logger.warning("Stage 3 Fixer hit 429 rate limit. Retrying in 15 seconds...")
                await asyncio.sleep(15)
                continue

            logger.error("Stage 3 Fixer failed via Groq: %s", exc)
            is_rl = is_rate_limit_error(exc)
            err_msg = RATE_LIMIT_USER_MESSAGE if is_rl else str(exc)
            return FixResult(
                root_cause=RATE_LIMIT_USER_MESSAGE if is_rl else "Analysis could not complete due to an error.",
                fixed_code=code,
                explanation=RATE_LIMIT_USER_MESSAGE if is_rl else "An error occurred while contacting Groq API.",
                error=err_msg,
            )
    return FixResult(
        root_cause=RATE_LIMIT_USER_MESSAGE,
        fixed_code=code,
        explanation=RATE_LIMIT_USER_MESSAGE,
        error=RATE_LIMIT_USER_MESSAGE,
    )
