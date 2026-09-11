"""Resilience and fallback tests for DevMind pipeline stages."""

import pytest
from pipeline.classifier import (
    classify_code,
    detect_language_heuristic,
    classify_error_heuristic,
)
from pipeline.summarizer import (
    summarize_code,
    extract_key_elements_heuristic,
)
from pipeline.orchestrator import format_sse


def test_language_detection_heuristics():
    assert detect_language_heuristic("def calculate(x):\n    return x * 2") == "python"
    assert detect_language_heuristic("const total = 42;\nconsole.log(total);") == "javascript"
    assert detect_language_heuristic("async function fetchUser() {\n  return database.get();\n}") == "javascript"
    assert detect_language_heuristic("import React from 'react';\nconst App = () => null;") == "javascript"
    assert detect_language_heuristic("const val: number = 42;") == "typescript"
    assert detect_language_heuristic("fn main() {\n    let mut x = 5;\n}") == "rust"
    assert detect_language_heuristic("package main\nfunc main() {}") == "go"


def test_error_classification_heuristics():
    assert classify_error_heuristic("query = 'SELECT * FROM users WHERE ' + userInput") == "security flaw"
    assert classify_error_heuristic("for i in range(1000000):\n    items.append(i)") == "performance"
    assert classify_error_heuristic("def invalid_syntax(\n    return 42") == "syntax error"


@pytest.mark.asyncio
async def test_stage1_fallback_resilience():
    code = "def divide(a, b):\n    return a / b"
    result = await classify_code(code)
    assert result.language == "python"
    assert result.error_type in ["logic error", "syntax error", "performance", "security flaw"]
    assert result.is_fallback is True or result.confidence > 0


@pytest.mark.asyncio
async def test_stage2_fallback_resilience():
    code = "async def fetch_user(uid):\n    data = await db.get(uid)\n    return data"
    result = await summarize_code(code, "python")
    assert "fetch_user" in " ".join(result.key_elements)
    assert "concurrency" in " ".join(result.key_elements)
    assert len(result.summary) > 0


def test_sse_event_formatter():
    raw_sse = format_sse("stage_update", {"stage": 1, "status": "running"})
    assert raw_sse.startswith("event: stage_update\n")
    assert '"stage": 1' in raw_sse
    assert raw_sse.endswith("\n\n")
