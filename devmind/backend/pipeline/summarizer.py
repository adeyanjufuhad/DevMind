"""Stage 2 — Code Understanding & Intent Summarization using StarCoder2."""

import logging
import re
from typing import List
from pipeline.schemas import SummaryResult
from utils.hf_client import hf_client

logger = logging.getLogger("devmind.summarizer")

STARCODER2_MODEL_ID = "bigcode/starcoder2-15b"


def extract_key_elements_heuristic(code: str) -> List[str]:
    """Extracts function identifiers, class names, and control structures."""
    elements: List[str] = []
    # Match function definitions
    funcs = re.findall(r"(?:def|function|func|fn)\s+([a-zA-Z_]\w*)", code)
    elements.extend([f"function: {f}()" for f in funcs[:3]])
    # Match classes
    classes = re.findall(r"(?:class|struct)\s+([a-zA-Z_]\w*)", code)
    elements.extend([f"class: {c}" for c in classes[:2]])
    # Match loops / control flow
    if "for " in code or "while " in code:
        elements.append("loop: iterative flow")
    if "try" in code or "except" in code or "catch" in code:
        elements.append("error-handling: try/catch block")
    if "async " in code or "await " in code:
        elements.append("concurrency: async/await")
    return elements or ["generic control flow"]


def generate_fallback_summary(code: str, language: str) -> SummaryResult:
    """Provides heuristic summary when HuggingFace is unavailable or times out."""
    elements = extract_key_elements_heuristic(code)
    lines = [line.strip() for line in code.split("\n") if line.strip()]
    first_meaningful = lines[0] if lines else "code block"
    summary = (
        f"A {language} snippet containing {len(lines)} lines starting with "
        f"'{first_meaningful[:50]}...', executing structured operations."
    )
    return SummaryResult(summary=summary, key_elements=elements, is_fallback=True)


async def summarize_code(code: str, language: str = "python") -> SummaryResult:
    """Executes Stage 2: summarizes intent and extracts key structural elements."""
    if not hf_client.is_configured():
        logger.info("HF key not set; using Stage 2 heuristic summarizer.")
        return generate_fallback_summary(code, language)

    prompt = (
        f"// Language: {language}\n"
        f"// Instructions: Summarize what this code does in one sentence.\n"
        f"{code[:600]}\n// Summary:"
    )

    try:
        hf_res = await hf_client.query_model(
            model_id=STARCODER2_MODEL_ID,
            inputs=prompt,
            parameters={"max_new_tokens": 60, "temperature": 0.2},
            timeout=15.0,
        )

        if hf_res and isinstance(hf_res, list) and len(hf_res) > 0:
            generated_text = hf_res[0].get("generated_text", "")
            summary_part = generated_text.replace(prompt, "").strip().split("\n")[0]
            if summary_part:
                return SummaryResult(
                    summary=summary_part,
                    key_elements=extract_key_elements_heuristic(code),
                    is_fallback=False,
                )
    except Exception as exc:
        logger.warning("Stage 2 StarCoder2 failed (%s). Falling back gracefully.", exc)

    return generate_fallback_summary(code, language)
