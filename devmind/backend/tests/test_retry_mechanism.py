"""Unit tests for the 429 rate-limit retry mechanism across Stages 3, 4, and 5."""

import pytest
from unittest.mock import AsyncMock, patch
from pipeline.fixer import fix_code
from pipeline.tester import generate_tests
from pipeline.documenter import generate_docs
from utils.groq_client import is_rate_limit_error, RATE_LIMIT_USER_MESSAGE


def test_is_rate_limit_error():
    class CustomErr(Exception):
        pass

    assert is_rate_limit_error(Exception("429 Resource Exhausted"))
    assert is_rate_limit_error(Exception("HTTP 429 Too Many Requests"))
    assert is_rate_limit_error(Exception("RESOURCE_EXHAUSTED: quota exceeded"))
    assert is_rate_limit_error(Exception("Rate limit reached"))
    
    custom = CustomErr("Server error")
    custom.status_code = 429
    assert is_rate_limit_error(custom)
    
    assert not is_rate_limit_error(Exception("SyntaxError: invalid syntax"))
    assert not is_rate_limit_error(Exception("500 Internal Server Error"))


@pytest.mark.asyncio
async def test_fixer_retry_on_429_success():
    call_count = 0

    async def mock_generate(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("429 Resource Exhausted")
        return {"root_cause": "Fixed", "fixed_code": "x = 1", "explanation": "Done"}

    with patch("pipeline.fixer.generate_groq_json", side_effect=mock_generate), \
         patch("pipeline.fixer.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        res = await fix_code("x = 0")
        assert call_count == 2
        mock_sleep.assert_awaited_once_with(15)
        assert res.fixed_code == "x = 1"
        assert res.error is None


@pytest.mark.asyncio
async def test_fixer_retry_on_429_exhausted():
    async def mock_generate(*args, **kwargs):
        raise Exception("429 Resource Exhausted")

    with patch("pipeline.fixer.generate_groq_json", side_effect=mock_generate), \
         patch("pipeline.fixer.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        res = await fix_code("x = 0")
        mock_sleep.assert_awaited_once_with(15)
        assert res.error == RATE_LIMIT_USER_MESSAGE
        assert res.root_cause == RATE_LIMIT_USER_MESSAGE


@pytest.mark.asyncio
async def test_tester_retry_on_429():
    async def mock_generate(*args, **kwargs):
        raise Exception("RESOURCE_EXHAUSTED")

    with patch("pipeline.tester.generate_groq_json", side_effect=mock_generate), \
         patch("pipeline.tester.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        res = await generate_tests("def add(): pass", "python")
        mock_sleep.assert_awaited_once_with(15)
        assert res.error == RATE_LIMIT_USER_MESSAGE


@pytest.mark.asyncio
async def test_documenter_retry_on_429():
    async def mock_generate(*args, **kwargs):
        raise Exception("Rate limit exceeded 429")

    with patch("pipeline.documenter.generate_groq_json", side_effect=mock_generate), \
         patch("pipeline.documenter.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        res = await generate_docs("def add(): pass", "python")
        mock_sleep.assert_awaited_once_with(15)
        assert res.error == RATE_LIMIT_USER_MESSAGE
