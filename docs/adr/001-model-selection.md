# ADR 001: Multi-Model Pipeline Architecture (Gemini 2.5 Flash + HuggingFace Free Tier)

## Status
**Accepted**

## Context
DevMind requires a multi-stage analysis pipeline that diagnoses bugs, corrects code, generates unit tests, and adds documentation.

The Gemini API now uses `AQ.` prefix authentication keys instead of legacy `AIza` keys. The `AQ.` keys only work through the official `google-genai` SDK (`from google import genai`), not through raw REST/HTTP requests or deprecated packages (`google.generativeai`).

We evaluated frontier and specialized models:
1. **Google Gemini 2.5 Flash**: Google AI Studio provides high throughput, 1M+ token context window, low latency, and free tier accessibility via the official `google-genai` SDK using `gemini-2.5-flash`.
2. **HuggingFace Inference API Free Tier**: Provides specialized lightweight models (`microsoft/codebert-base` and `bigcode/starcoder2-15b`) for low-latency syntactic analysis and language detection.

## Decision
We adopt a **heterogeneous, 5-stage multi-model pipeline using the official `google-genai` SDK**:

1. **HuggingFace Free Tier Inference API for Preliminary Stages**:
   - **Stage 1 (Classification)**: `microsoft/codebert-base`. Rapidly classifies problem type (syntax error, logic error, performance, security flaw) and detects programming language.
   - **Stage 2 (Code Understanding)**: `bigcode/starcoder2-15b`. Synthesizes intent summary and extracts AST symbols.

2. **Google Gemini 2.5 Flash (via official `google-genai` SDK) for Reasoning Stages**:
   - **Stage 3 (Bug Fix & Explanation)**: Takes original code + Stages 1 & 2 outputs. Identifies root cause, writes production-ready fix, and provides a junior-friendly walkthrough.
   - **Stage 4 (Unit Test Generation)**: Generates idiomatic test suites (`pytest`, `jest`, etc.).
   - **Stage 5 (Documentation & Annotation)**: Generates standard docstrings and inline commentary.

3. **Authentication & Secret Management**:
   - `client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))`
   - Supports both `AQ.` prefix keys and standard keys.
   - Model: `gemini-2.5-flash`.

4. **Resilience & Fallback Strategy**:
   - HuggingFace calls enforce a strict **15-second timeout**.
   - If HuggingFace fails or times out, Stages 1 and 2 degrade gracefully and pass null context to Gemini 2.5 Flash.
   - Gemini 2.5 Flash operates with direct zero-shot inference, ensuring the pipeline never fails catastrophically.

## Consequences

### Positive
- **Full Compatibility with AQ. Keys**: Uses the official `google-genai` SDK instead of direct REST calls.
- **Fastest Inference Speeds**: `gemini-2.5-flash` delivers lower latency and higher generation fidelity.
- **Zero Deprecation Warnings**: Migrated off legacy `google.generativeai`.
