"""Pipeline Orchestrator — Coordinates Stages 1-5 and emits SSE events."""

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional
from pipeline.classifier import classify_code
from pipeline.documenter import generate_docs
from pipeline.fixer import fix_code
from pipeline.schemas import PipelineDoneResult
from pipeline.summarizer import summarize_code
from pipeline.tester import generate_tests

logger = logging.getLogger("devmind.orchestrator")


def format_sse(event: str, data: Dict[str, Any]) -> str:
    """Formats an event name and dictionary into an SSE wire string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def run_pipeline_stream(
    code: str, language_hint: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """Runs the 5-stage DevMind AI pipeline, yielding SSE events for each milestone."""
    full_result = PipelineDoneResult()

    # --- STAGE 1: Classification ---
    yield format_sse("stage_update", {"stage": 1, "label": "Classifying language & error...", "status": "running"})
    try:
        c_res = await classify_code(code, language_hint)
        full_result.classification = c_res
        yield format_sse("stage_complete", {"stage": 1, "result": c_res.model_dump()})
    except Exception as exc:
        logger.warning("Stage 1 execution error: %s", exc)
        yield format_sse("stage_complete", {"stage": 1, "result": {"error": str(exc), "skipped": True}})

    active_lang = full_result.classification.language if full_result.classification else (language_hint or "python")

    # --- STAGE 2: Code Understanding ---
    yield format_sse("stage_update", {"stage": 2, "label": "Summarizing code intent...", "status": "running"})
    try:
        s_res = await summarize_code(code, active_lang)
        full_result.summary = s_res
        yield format_sse("stage_complete", {"stage": 2, "result": s_res.model_dump()})
    except Exception as exc:
        logger.warning("Stage 2 execution error: %s", exc)
        yield format_sse("stage_complete", {"stage": 2, "result": {"error": str(exc), "skipped": True}})

    # --- STAGE 3: Bug Fix & Explanation ---
    yield format_sse("stage_update", {"stage": 3, "label": "Diagnosing bug & generating fix...", "status": "running"})
    f_res = await fix_code(
        code=code,
        classification=full_result.classification,
        summary=full_result.summary,
    )
    full_result.fix = f_res
    yield format_sse("stage_complete", {"stage": 3, "result": f_res.model_dump()})

    fixed_code = f_res.fixed_code if f_res and f_res.fixed_code else code

    # --- STAGE 4: Unit Test Generation ---
    yield format_sse("stage_update", {"stage": 4, "label": "Generating unit tests...", "status": "running"})
    t_res = await generate_tests(fixed_code=fixed_code, language=active_lang)
    full_result.tests = t_res
    yield format_sse("stage_complete", {"stage": 4, "result": t_res.model_dump()})

    # --- STAGE 5: Documentation ---
    yield format_sse("stage_update", {"stage": 5, "label": "Generating documentation & comments...", "status": "running"})
    d_res = await generate_docs(fixed_code=fixed_code, language=active_lang)
    full_result.docs = d_res
    yield format_sse("stage_complete", {"stage": 5, "result": d_res.model_dump()})

    # --- DONE: Full aggregated result ---
    yield format_sse("done", {"full_result": full_result.model_dump()})
