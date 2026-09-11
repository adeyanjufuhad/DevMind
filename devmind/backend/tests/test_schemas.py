"""Unit tests for DevMind Pydantic schemas and serialization contracts."""

import pytest
from pipeline.schemas import (
    AnalyzeRequest,
    ClassificationResult,
    SummaryResult,
    FixResult,
    TestResult,
    DocResult,
    PipelineDoneResult,
)


def test_analyze_request_valid():
    req = AnalyzeRequest(code="print('hello')", language="python")
    assert req.code == "print('hello')"
    assert req.language == "python"


def test_analyze_request_empty_rejected():
    with pytest.raises(Exception):
        AnalyzeRequest(code="")


def test_classification_result_defaults():
    res = ClassificationResult(language="python", error_type="logic error")
    assert res.confidence == 1.0
    assert not res.is_fallback
    assert res.error_type == "logic error"


def test_summary_result_serialization():
    res = SummaryResult(
        summary="A sorting function",
        key_elements=["sort()", "array"],
        is_fallback=False,
    )
    dumped = res.model_dump()
    assert dumped["summary"] == "A sorting function"
    assert "sort()" in dumped["key_elements"]


def test_pipeline_done_aggregation():
    fix = FixResult(
        root_cause="Missing index",
        fixed_code="x = arr[0]",
        explanation="Index fixed",
    )
    tests = TestResult(framework="pytest", tests="def test_x(): assert True")
    docs = DocResult(documented_code="# Comment\nx = arr[0]")

    done = PipelineDoneResult(fix=fix, tests=tests, docs=docs)
    dumped = done.model_dump()

    assert dumped["fix"]["root_cause"] == "Missing index"
    assert dumped["tests"]["framework"] == "pytest"
    assert dumped["docs"]["documented_code"].startswith("# Comment")
