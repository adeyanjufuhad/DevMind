<p align="center">
  <img src="docs/assets/logo.png" width="160" alt="DevMind Logo" />
</p>

<h1 align="center">DevMind — AI-Powered Developer Companion</h1>

<p align="center">
  <strong>An autonomous 5-stage multi-model AI pipeline that debugs, fixes, tests, and documents code in real time.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black" alt="React 18" />
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/Gemini-3.6--Flash-4285F4?style=flat&logo=google&logoColor=white" alt="Gemini 3.6 Flash" />
  <img src="https://img.shields.io/badge/HuggingFace-Inference_API-FFD21E?style=flat&logo=huggingface&logoColor=black" alt="HuggingFace" />
  <img src="https://img.shields.io/badge/Streaming-SSE-2563EB?style=flat" alt="Server-Sent Events" />
</p>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
  - [The 5-Stage Multi-Model Pipeline](#the-5-stage-multi-model-pipeline)
  - [Pipeline Flow Diagram](#pipeline-flow-diagram)
  - [Resilience & Fallback Strategy](#resilience--fallback-strategy)
- [Codebase Structure](#-codebase-structure)
- [Architectural Design Records (C4 & ADRs)](#-architectural-design-records-c4--adrs)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#1-backend-setup)
  - [Frontend Setup](#2-frontend-setup)
  - [Environment Variables Configuration](#3-environment-variables-configuration)
- [UI & Developer Experience](#-ui--developer-experience)
- [Automated Testing & Quality Standards](#-automated-testing--quality-standards)
- [API Reference](#-api-reference)
- [Attribution](#-attribution)

---

## 💡 Overview

Software engineers spend up to 50% of their working hours troubleshooting cryptic errors, refactoring defective logic, writing boilerplate test suites, and documenting legacy code.

**DevMind** unifies this workflow into a single-click, automated developer companion:
1. **Root Cause Analysis**: Isolates the exact line and reason why the code fails.
2. **Production-Ready Fix**: Applies the correction directly to the snippet.
3. **Automated Unit Tests**: Synthesizes comprehensive, framework-specific tests (`pytest`, `jest`, `gotest`, `cargo test`).
4. **Annotated Documentation**: Adds production-grade docstrings, type hints, and inline comments.
5. **Junior-Friendly Walkthrough**: Explains the diagnosis in clear, intuitive language.

---

## 🏗️ System Architecture

DevMind is designed with a **stateless, zero-retention architecture**. User code is never stored in a database or persisted to disk, guaranteeing maximum IP security and privacy.

```
┌─────────────────────────────────────────────────────────────┐
│                      Developer Browser                      │
│   (React 18 + Tailwind CSS + JetBrains Mono + highlight.js) │
└──────────────────────────────┬──────────────────────────────┘
                               │ POST /analyze (JSON payload)
                               │ Server-Sent Events (SSE Stream)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                DevMind FastAPI Backend (Async)              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Stage 1: CodeBERT (HuggingFace Inference API)           │ │
│ │   Language Detection & Error Classification Taxonomy   │ │
│ └────────────────────────────┬────────────────────────────┘ │
│                              ▼                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Stage 2: StarCoder2-15B (HuggingFace Inference API)     │ │
│ │   Code Intent Summarization & AST Symbol Extraction     │ │
│ └────────────────────────────┬────────────────────────────┘ │
│                              ▼                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Stage 3: Gemini 3.6 Flash (google-genai SDK)            │ │
│ │   Root Cause Diagnosis + Corrected Code + Junior Walk   │ │
│ └────────────────────────────┬────────────────────────────┘ │
│                              ▼                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Stage 4: Gemini 3.6 Flash (google-genai SDK)            │ │
│ │   Framework-Specific Unit Test Suite Synthesis          │ │
│ └────────────────────────────┬────────────────────────────┘ │
│                              ▼                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Stage 5: Gemini 3.6 Flash (google-genai SDK)            │ │
│ │   Production Docstrings, Type Hints & Inline Comments   │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### The 5-Stage Multi-Model Pipeline

| Stage | Model | Provider / SDK | Responsibilities | Output Contract |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | `microsoft/codebert-base` | HuggingFace Inference API | Identifies language if unspecified; classifies defect into syntax, logic, performance, or security flaw. | `{ "language": str, "error_type": str, "confidence": float }` |
| **Stage 2** | `bigcode/starcoder2-15b` | HuggingFace Inference API | Summarizes developer intent; extracts functions, classes, loops, and concurrency patterns. | `{ "summary": str, "key_elements": [str] }` |
| **Stage 3** | `gemini-3.6-flash` | Google AI Studio (`google-genai`) | Synthesizes root cause analysis, generates full repaired code, and provides junior-developer walkthrough. | `{ "root_cause": str, "fixed_code": str, "explanation": str }` |
| **Stage 4** | `gemini-3.6-flash` | Google AI Studio (`google-genai`) | Generates executable test suite with assertions and edge cases matching language conventions. | `{ "framework": str, "tests": str }` |
| **Stage 5** | `gemini-3.6-flash` | Google AI Studio (`google-genai`) | Enriches fixed code with standard docstrings, type annotations, and inline commentary. | `{ "documented_code": str }` |

### Resilience & Fallback Strategy

- **15-Second HuggingFace Timeout**: All HuggingFace Inference API queries are wrapped with strict 15.0s timeouts. If HuggingFace experiences cold starts (503), rate limits (429), or timeouts, Stages 1 and 2 degrade gracefully to robust heuristic analysis.
- **Gemini Direct Zero-Shot Fallback**: If secondary model context is missing or partial, Gemini 3.6 Flash proceeds with autonomous zero-shot inference so the user workflow is never blocked.
- **Official `google-genai` SDK**: Native support for the newest Google AI Studio `AQ.` prefix authentication keys (which fail when used via raw REST calls).

---

## 📂 Codebase Structure

```
DevMind/
├── docs/                                  # Architectural Design & C4 Models
│   ├── architecture.md                    # C4 Model (Context, Container, Component levels)
│   ├── design.md                          # Google-style system design document
│   ├── adr/                               # Architecture Decision Records
│   │   ├── 001-model-selection.md         # ADR: Gemini 3.6 Flash + HuggingFace free tier
│   │   └── 002-stateless-pipeline.md      # ADR: Stateless zero-retention architecture
│   └── assets/
│       └── logo.png                       # High-resolution DevMind brand logo
│
├── devmind/
│   ├── backend/                           # Python FastAPI Asynchronous Service
│   │   ├── main.py                        # FastAPI entry point, CORS, /health, /analyze SSE
│   │   ├── requirements.txt               # Backend Python dependencies
│   │   ├── .env.example                   # Environment variable template
│   │   ├── pipeline/                      # 5-Stage Pipeline Workers (all <= 150 lines)
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py                 # Pydantic v2 data models for all stages & events
│   │   │   ├── classifier.py              # Stage 1: CodeBERT & syntax scoring
│   │   │   ├── summarizer.py              # Stage 2: StarCoder2 intent & AST extractor
│   │   │   ├── fixer.py                   # Stage 3: Gemini 3.6 Flash bug diagnosis & fix
│   │   │   ├── tester.py                  # Stage 4: Gemini 3.6 Flash test suite generator
│   │   │   ├── documenter.py              # Stage 5: Gemini 3.6 Flash documentation
│   │   │   └── orchestrator.py            # Async generator emitting SSE events (1-5 + done)
│   │   ├── utils/                         # External AI SDK Client Wrappers
│   │   │   ├── __init__.py
│   │   │   ├── gemini_client.py           # Official google-genai client (AQ. keys supported)
│   │   │   ├── hf_client.py               # HuggingFace async HTTP client (15s timeout)
│   │   │   └── anthropic_client.py        # Anthropic Claude client wrapper
│   │   └── tests/                         # Automated Pytest Suite
│   │       ├── __init__.py
│   │       ├── test_schemas.py            # Pydantic schema validation & serialization tests
│   │       └── test_pipeline_fallback.py  # Language heuristics & fallback resilience tests
│   │
│   └── frontend/                          # React 18 + Tailwind CSS Web Application
│       ├── index.html                     # HTML shell, favicon, highlight.js CDN
│       ├── vite.config.js                 # Vite build & development server config
│       ├── tailwind.config.js             # Tailwind design tokens & font configs
│       ├── postcss.config.js              # PostCSS plugins
│       ├── package.json                   # Frontend npm dependencies
│       ├── public/
│       │   └── logo.png                   # Favicon & branding asset
│       └── src/
│           ├── main.jsx                   # React root mount
│           ├── index.css                  # Base styles, scrollbars, Inter font
│           ├── App.jsx                    # Desktop two-panel layout & main view
│           ├── usePipeline.js             # Custom hook consuming SSE stream via ReadableStream
│           └── components/
│               ├── CodeEditor.jsx         # White editor with line numbers & highlight.js
│               ├── ResultsTabs.jsx        # Minimal underline tabs (Analysis, Fix, Tests, Docs)
│               ├── PipelineProgress.jsx   # Compact 5-stage pill status strip
│               ├── LanguageSelector.jsx   # Language hint dropdown
│               ├── HowItWorks.jsx         # Collapsible 7-step guide with SVG pipeline flow
│               ├── PoweredByBadge.jsx     # Floating persistent attribution badge
│               └── snippets.js            # Sample bug snippets (recursion, async, SQLi)
│
├── .gitignore                             # Git ignore rules for Python, Node, & secrets
└── README.md                              # Project documentation
```

---

## 🏛️ Architectural Design Records (C4 & ADRs)

DevMind was architected using **`karak-architecture`** principles:

- [**`docs/architecture.md`**](docs/architecture.md): Contains the complete C4 model:
  - **Level 1 (System Context)**: System boundaries between Developer, DevMind, HuggingFace Inference API, and Google AI Studio.
  - **Level 2 (Container)**: Interaction between the React SPA, FastAPI backend, and upstream AI models.
  - **Level 3 (Component)**: Internal module composition of the FastAPI service.
  - **SSE Protocol Specification**: Full payload format for `stage_update`, `stage_complete`, and `done` events.
- [**`docs/adr/001-model-selection.md`**](docs/adr/001-model-selection.md): Rationale for adopting Gemini 3.6 Flash via the official `google-genai` SDK and HuggingFace free-tier models.
- [**`docs/adr/002-stateless-pipeline.md`**](docs/adr/002-stateless-pipeline.md): Rationale for a zero-retention stateless architecture to protect proprietary code privacy.
- [**`docs/design.md`**](docs/design.md): Google-style design document covering Goals & Non-Goals, detailed stage contracts, and fault tolerance matrices.

---

## 🚀 Getting Started

### Prerequisites

- **Python**: `3.11` or higher
- **Node.js**: `18.0` or higher (with `npm`)
- **Google AI Studio API Key**: [Get a free Gemini API key](https://aistudio.google.com/) (supports `AQ.` prefix keys)
- **HuggingFace User Access Token (Optional)**: [Get a free HF Token](https://huggingface.co/settings/tokens)

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd devmind/backend

# (Optional) Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `devmind/backend/.env`:
```env
# Required for Stages 3, 4, and 5 (Gemini 3.6 Flash via official google-genai SDK)
GEMINI_API_KEY=your_gemini_api_key_here

# Required for Stages 1 and 2 (HuggingFace Inference API Free tier)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Server host and port
HOST=0.0.0.0
PORT=8000
```

Start the backend server:
```bash
python main.py
# Backend runs at http://localhost:8000
```

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd devmind/frontend

# Install npm dependencies
npm install

# Start development server
npm run dev
# Frontend runs at http://localhost:5173
```

---

## 🎨 UI & Developer Experience

The interface is built to evoke the dense, productive feel of developer tools like Vercel and Railway:

- **Desktop Two-Panel Split**: Left panel houses the code input; Right panel houses the compact pipeline status strip and results tabs. Both panels are equally weighted and always visible.
- **Dynamic Syntax Highlighting**:
  - *Before running*: Crisp white `<textarea>` canvas with line numbers in `#8B949E`.
  - *After Stage 1 completes*: Automatically re-renders using `highlight.js` with the detected language and GitHub token colors.
  - *Seamless editing*: Click anywhere on the code or click **Edit** in the toolbar to return to input mode.
- **Typography**: `JetBrains Mono` for code surfaces and stage pills; `Inter` for UI labels and text.
- **Design Tokens**: Base `#F9FAFB`, Surface `#FFFFFF`, Border `#E5E7EB`, Accent `#2563EB`.

---

## 🧪 Automated Testing & Quality Standards

DevMind strictly enforces **`karak-engineering`** standards:
- **Modularity**: No single source code file exceeds **150 lines**.
- **Asynchronous Execution**: All FastAPI endpoints, generator streams, and client calls are non-blocking.
- **100% Test Coverage on Fallbacks & Schemas**:

Run backend tests:
```bash
cd devmind/backend
python -m pytest tests/
```

Build frontend for production:
```bash
cd devmind/frontend
npm run build
```

---

## 📡 API Reference

### `POST /analyze`
Initiates the 5-stage analysis pipeline and streams live updates using Server-Sent Events (`text/event-stream`).

#### Request Body:
```json
{
  "code": "def fib(n):\n    if n == 1:\n        return 1\n    return fib(n-1) + fib(n-2)",
  "language": null
}
```

#### Streamed SSE Events:
```http
event: stage_update
data: {"stage": 1, "label": "Classifying language & error...", "status": "running"}

event: stage_complete
data: {"stage": 1, "result": {"language": "python", "error_type": "logic error", "confidence": 0.92}}

event: stage_update
data: {"stage": 2, "label": "Summarizing code intent...", "status": "running"}

event: stage_complete
data: {"stage": 2, "result": {"summary": "Recursively computes Fibonacci numbers...", "key_elements": ["fib()", "recursion"]}}

event: stage_update
data: {"stage": 3, "label": "Diagnosing bug & generating fix...", "status": "running"}

event: stage_complete
data: {"stage": 3, "result": {"root_cause": "Missing base case for n <= 0...", "fixed_code": "...", "explanation": "..."}}

event: stage_update
data: {"stage": 4, "label": "Generating unit tests...", "status": "running"}

event: stage_complete
data: {"stage": 4, "result": {"framework": "pytest", "tests": "..."}}

event: stage_update
data: {"stage": 5, "label": "Generating documentation...", "status": "running"}

event: stage_complete
data: {"stage": 5, "result": {"documented_code": "..."}}

event: done
data: {"full_result": { ... }}
```

---

## 🤝 Attribution

DevMind was architected and built with assistance from **`karak-claude-plugin`**:
- [karak-claude-plugin GitHub Repository](https://github.com/karak/karak-claude-plugin)
- Utilizing `karak-architecture` (C4 models, ADRs) and `karak-engineering` (modular code reviews, strict quality thresholds).

---

<p align="center">
  <sub>DevMind · Built with Google Gemini, HuggingFace, and karak-claude-plugin · MIT License</sub>
</p>
