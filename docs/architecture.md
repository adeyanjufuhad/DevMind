# DevMind Architecture Specification (C4 Model)

This document provides the architectural blueprint for **DevMind**, an AI-powered developer companion, designed according to the **C4 model** (Context, Container, and Component levels) and synthesized with `karak-architecture` standards.

---

## 1. System Context Diagram (Level 1)

The System Context diagram details how software developers interact with DevMind and its external upstream AI providers.

```mermaid
C4Context
    title System Context Diagram for DevMind

    Person(developer, "Software Developer", "A developer seeking automated root cause analysis, code fixes, tests, and documentation.")
    System(devmind, "DevMind System", "Multi-model AI pipeline that ingests broken/suboptimal code and returns an end-to-end diagnosis, fix, test suite, and annotated documentation.")
    
    System_Ext(hf_api, "HuggingFace Inference API", "Hosts CodeBERT (classification) and StarCoder2-15B (code summarization). Free tier.")
    System_Ext(gemini_api, "Google AI Studio API", "Hosts Gemini 1.5 Flash for bug fixing, test generation, and documentation. Free tier.")

    Rel(developer, devmind, "Submits code snippet and language hint via Web UI; receives streaming results", "HTTPS / SSE")
    Rel(devmind, hf_api, "Dispatches classification & code summarization requests (15s timeout)", "HTTPS / REST")
    Rel(devmind, gemini_api, "Dispatches bug fixing, test suite generation, and documentation prompts", "HTTPS / REST")
```

### Context Entities
- **Software Developer**: Interacts with the browser frontend to input broken code, monitor the 5-stage pipeline, and review generated solutions.
- **DevMind**: Central processing platform orchestrating the AI pipeline and streaming real-time stage updates.
- **HuggingFace Inference API (Free Tier)**: Serves specialized lightweight models (`microsoft/codebert-base` and `bigcode/starcoder2-15b`) for low-latency syntactic analysis.
- **Google AI Studio API (Free Tier)**: Serves `gemini-1.5-flash` via `google-generativeai` with no billing required for contextual debugging, test synthesis, and doc generation.

---

## 2. Container Diagram (Level 2)

```mermaid
C4Container
    title Container Diagram for DevMind

    Person(developer, "Software Developer", "End-user coding in IDE or browser")

    Container_Boundary(devmind_app, "DevMind Platform") {
        Container(spa, "Single-Page Application", "React, Tailwind CSS, Vite", "Provides a clean developer-tool UI, compact pipeline status strip, minimal underline tabs, and persistent attribution.")
        Container(api, "Backend API Service", "FastAPI, Python 3.11+", "Fully asynchronous application orchestrating the 5-stage pipeline and streaming Server-Sent Events (SSE).")
    }

    System_Ext(hf, "HuggingFace API", "External Inference API")
    System_Ext(gemini, "Google AI Studio API", "External Gemini 1.5 Flash API")

    Rel(developer, spa, "Enters code, views live pipeline & solutions", "HTTPS")
    Rel(spa, api, "POST /analyze (code, language)", "HTTPS / SSE Streaming")
    Rel(api, hf, "Stage 1 (CodeBERT) & Stage 2 (StarCoder2)", "REST / JSON (httpx async)")
    Rel(api, gemini, "Stage 3 (Fixer), Stage 4 (Tester), Stage 5 (Documenter)", "REST / JSON (google-generativeai)")
```

---

## 3. Component Diagram (Level 3 - Backend Service)

```mermaid
C4Component
    title Component Diagram for DevMind Backend

    Container_Boundary(api_boundary, "FastAPI Backend Service") {
        Component(main, "API Controller", "main.py", "Handles incoming HTTP requests, CORS, and coordinates SSE streaming lifecycle.")
        Component(orchestrator, "Pipeline Orchestrator", "pipeline/orchestrator.py", "Executes Stages 1 through 5 sequentially, yielding real-time SSE events with error isolation.")
        
        Component(c_stage1, "Classifier (Stage 1)", "pipeline/classifier.py", "Detects language and categorizes problem type (syntax, logic, performance, security).")
        Component(c_stage2, "Summarizer (Stage 2)", "pipeline/summarizer.py", "Generates semantic intent summary and extracts AST/control flow elements.")
        Component(c_stage3, "Fixer (Stage 3)", "pipeline/fixer.py", "Synthesizes root cause analysis, corrected code, and junior-friendly explanation using Gemini.")
        Component(c_stage4, "Tester (Stage 4)", "pipeline/tester.py", "Synthesizes framework-appropriate unit tests using Gemini.")
        Component(c_stage5, "Documenter (Stage 5)", "pipeline/documenter.py", "Synthesizes production-grade docstrings and inline annotations using Gemini.")

        Component(hf_client, "HuggingFace Client", "utils/hf_client.py", "Async HTTP wrapper with 15s timeout, authorization headers, and error capture.")
        Component(gemini_client, "Gemini Client", "utils/gemini_client.py", "Async wrapper around google-generativeai for gemini-1.5-flash.")
    }

    Rel(main, orchestrator, "Delegates analysis task", "Python Async Generator")
    Rel(orchestrator, c_stage1, "Invokes Stage 1", "Async Call")
    Rel(orchestrator, c_stage2, "Invokes Stage 2", "Async Call")
    Rel(orchestrator, c_stage3, "Invokes Stage 3", "Async Call")
    Rel(orchestrator, c_stage4, "Invokes Stage 4", "Async Call")
    Rel(orchestrator, c_stage5, "Invokes Stage 5", "Async Call")

    Rel(c_stage1, hf_client, "Queries microsoft/codebert-base", "Async HTTP")
    Rel(c_stage2, hf_client, "Queries bigcode/starcoder2-15b", "Async HTTP")
    Rel(c_stage3, gemini_client, "Prompts Gemini 1.5 Flash", "Async API")
    Rel(c_stage4, gemini_client, "Prompts Gemini 1.5 Flash", "Async API")
    Rel(c_stage5, gemini_client, "Prompts Gemini 1.5 Flash", "Async API")
```
