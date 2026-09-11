"""DevMind FastAPI Application — Entry point for SSE code analysis."""

import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pipeline.orchestrator import run_pipeline_stream
from pipeline.schemas import AnalyzeRequest
from utils.hf_client import hf_client

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("devmind.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown logger."""
    gemini_ready = bool(os.environ.get("GEMINI_API_KEY"))
    anthropic_ready = bool(os.environ.get("ANTHROPIC_API_KEY"))
    hf_ready = hf_client.is_configured()
    logger.info("Starting DevMind Backend Service...")
    logger.info("Gemini API Key configured (Primary): %s", gemini_ready)
    logger.info("Anthropic API Key configured (Optional): %s", anthropic_ready)
    logger.info("HuggingFace API Key configured: %s", hf_ready)
    yield
    logger.info("Shutting down DevMind Backend Service...")


app = FastAPI(
    title="DevMind API",
    description="Multi-Model AI Pipeline for Developer Code Intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend development servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Returns service health status and upstream credential availability."""
    return {
        "status": "healthy",
        "service": "DevMind Backend",
        "models": {
            "gemini": bool(os.environ.get("GEMINI_API_KEY")),
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "huggingface": hf_client.is_configured(),
        },
    }


@app.post("/analyze")
async def analyze_code_endpoint(request: AnalyzeRequest):
    """Streams 5-stage pipeline events as Server-Sent Events (SSE)."""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    return StreamingResponse(
        run_pipeline_stream(
            code=request.code,
            language_hint=request.language,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
