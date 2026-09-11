"""Pydantic data contracts for DevMind 5-stage pipeline."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Input payload for code analysis."""
    code: str = Field(..., min_length=1, description="Source code snippet to analyze")
    language: Optional[str] = Field(None, description="Optional programming language hint")


class ClassificationResult(BaseModel):
    """Stage 1 output: Language and error category."""
    language: str
    error_type: str  # syntax error | logic error | performance | security flaw
    confidence: float = 1.0
    is_fallback: bool = False


class SummaryResult(BaseModel):
    """Stage 2 output: Code intent summary and semantic elements."""
    summary: str
    key_elements: List[str] = Field(default_factory=list)
    is_fallback: bool = False


class FixResult(BaseModel):
    """Stage 3 output: Root cause, repaired code, and junior explanation."""
    root_cause: str
    fixed_code: str
    explanation: str
    error: Optional[str] = None


class TestResult(BaseModel):
    """Stage 4 output: Generated unit test suite."""
    __test__ = False
    tests: str
    framework: Optional[str] = None
    error: Optional[str] = None


class DocResult(BaseModel):
    """Stage 5 output: Code with docstrings, annotations, and comments."""
    documented_code: str
    error: Optional[str] = None


class PipelineDoneResult(BaseModel):
    """Final aggregated payload returned upon completion."""
    classification: Optional[ClassificationResult] = None
    summary: Optional[SummaryResult] = None
    fix: Optional[FixResult] = None
    tests: Optional[TestResult] = None
    docs: Optional[DocResult] = None


class SSEEventPayload(BaseModel):
    """Payload format for streaming Server-Sent Events."""
    event: str
    data: Dict[str, Any]
