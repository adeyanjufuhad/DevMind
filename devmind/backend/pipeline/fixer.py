"""Stage 3 — Bug Diagnosis, Code Repair & Junior Explanation using Gemini 2.5 Flash."""

import logging
from typing import Optional
from pipeline.schemas import ClassificationResult, FixResult, SummaryResult
from utils.gemini_client import generate_gemini_json

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
    """Executes Stage 3: Diagnoses the bug and generates a fix using Gemini 2.5 Flash."""
    prompt = build_fixer_prompt(code, classification, summary)
    try:
        data = await generate_gemini_json(
            contents=prompt,
            system_instruction=FIXER_SYSTEM_PROMPT,
            model="gemini-3.6-flash",
            temperature=0.2,
        )
        return FixResult(
            root_cause=data.get("root_cause", "Root cause identified."),
            fixed_code=data.get("fixed_code", code),
            explanation=data.get("explanation", "Fix applied successfully."),
        )
    except Exception as exc:
        logger.error("Stage 3 Fixer failed via google-genai: %s", exc)
        return FixResult(
            root_cause="Analysis could not complete due to an error.",
            fixed_code=code,
            explanation="An error occurred while contacting Gemini API.",
            error=str(exc),
        )
