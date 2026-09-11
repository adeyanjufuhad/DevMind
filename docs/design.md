# Design Document: DevMind Multi-Model AI Pipeline

**Author**: DevMind Core Engineering  
**Status**: Approved  
**Standards**: `karak-architecture` & `karak-engineering`

---

## 1. Overview & Problem Statement

DevMind is an automated, multi-model developer companion that unifies code diagnosis into a single-click, 5-stage sequential AI pipeline. By pipelining lightweight, specialized code representations (HuggingFace CodeBERT and StarCoder2) into a fast, generous free-tier reasoning model (**Google Gemini 1.5 Flash** via Google AI Studio API with no billing required), DevMind streams an end-to-end diagnosis: error classification, intent summarization, root cause diagnosis, repaired code, unit tests, and production documentation.

---

## 2. Goals and Non-Goals

### Goals
- **5-Stage Output**:
  1. Language identification and problem classification (syntax, logic, performance, security).
  2. Syntactic and semantic intent summary with extracted elements.
  3. Root cause breakdown, corrected code, and junior-friendly explanation (Gemini 1.5 Flash).
  4. Idiomatic unit tests adapted to the language/framework (Gemini 1.5 Flash).
  5. Fully documented code with docstrings and inline commentary (Gemini 1.5 Flash).
- **Free Tier Accessibility**: Powered completely by free-tier endpoints requiring zero billing setup (`google-generativeai` with `GEMINI_API_KEY` and HuggingFace free inference).
- **Real-Time Streaming UX**: Server-Sent Events (SSE) with compact stage chips.
- **Graceful Fault-Tolerance**: 15s timeout on HuggingFace calls; Gemini direct inference fallback.
- **Strict Modularity**: All source files strictly $\le 150$ lines.

---

## 3. Detailed Pipeline Stage Design

### Stage 1: Classification (`classifier.py`)
- **Model**: `microsoft/codebert-base` (via HuggingFace Inference API).
- **Output**: `{ language, error_type, confidence }`.

### Stage 2: Code Understanding (`summarizer.py`)
- **Model**: `bigcode/starcoder2-15b` (via HuggingFace Inference API).
- **Output**: `{ summary, key_elements }`.

### Stage 3: Bug Fix & Explanation (`fixer.py`)
- **Model**: `gemini-1.5-flash` (via `google-generativeai`).
- **Context**: Original code + Stage 1 & 2 metadata.
- **Output**: `{ root_cause, fixed_code, explanation }`.

### Stage 4: Test Generation (`tester.py`)
- **Model**: `gemini-1.5-flash` (via `google-generativeai`).
- **Input**: Fixed code from Stage 3.
- **Output**: `{ framework, tests }`.

### Stage 5: Documentation (`documenter.py`)
- **Model**: `gemini-1.5-flash` (via `google-generativeai`).
- **Input**: Fixed code from Stage 3.
- **Output**: `{ documented_code }`.

---

## 4. Quality & File Size Standards (`karak-engineering`)

Every module strictly conforms to $\le 150$ lines per file, async execution, typed Pydantic models, and single-responsibility components.
