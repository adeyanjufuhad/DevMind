"""Stage 1 — Language Detection & Problem Classification using CodeBERT."""

import logging
import re
from typing import Optional
from pipeline.schemas import ClassificationResult
from utils.hf_client import hf_client

logger = logging.getLogger("devmind.classifier")
CODEBERT_MODEL_ID = "microsoft/codebert-base"


def detect_language_heuristic(code: str) -> str:
    """Accurately detects programming language based on syntax and token patterns."""
    scores = {"javascript": 0, "typescript": 0, "python": 0, "go": 0, "rust": 0, "java": 0, "cpp": 0}

    # Python patterns
    if re.search(r"\bdef\s+\w+\s*\(.*?\)\s*:", code): scores["python"] += 7
    if re.search(r"\belif\b.*?:", code): scores["python"] += 6
    if re.search(r"\bfrom\s+\w+(?:\.\w+)*\s+import\b", code): scores["python"] += 6
    if re.search(r"^\s*import\s+\w+(?:\s*,\s*\w+)*\s*$", code, re.M): scores["python"] += 5
    if re.search(r"\b(?:None|True|False)\b", code): scores["python"] += 4
    if re.search(r"\bself\.\w+", code): scores["python"] += 5
    if re.search(r"\bprint\s*\(", code): scores["python"] += 3
    if re.search(r"\bexcept(?:\s+\w+)?\s*:", code): scores["python"] += 5
    if re.search(r"^\s*#[^!]", code, re.M): scores["python"] += 2
    if re.search(r":\s*$", code, re.M): scores["python"] += 2

    # JavaScript / TypeScript patterns
    if re.search(r"\b(?:const|let|var)\s+\w+", code): scores["javascript"] += 5
    if re.search(r"\b(?:function|async\s+function)\b", code): scores["javascript"] += 5
    if re.search(r"\bconsole\.(?:log|error|warn|info|debug)\b", code): scores["javascript"] += 7
    if re.search(r"=>", code): scores["javascript"] += 4
    if re.search(r"===|!==", code): scores["javascript"] += 5
    if re.search(r"\.then\s*\(|\.catch\s*\(|\bnew\s+Promise\b", code): scores["javascript"] += 6
    if re.search(r"\b(?:document|window|localStorage|sessionStorage)\b", code): scores["javascript"] += 6
    if re.search(r"\bimport\s+.*?from\s+['\"][^'\"]+['\"]", code): scores["javascript"] += 6
    if re.search(r"\bexport\s+(?:default|const|let|function|class)\b", code): scores["javascript"] += 5
    if re.search(r"\brequire\s*\(['\"][^'\"]+['\"]\)", code): scores["javascript"] += 6
    if re.search(r"\b(?:null|undefined)\b", code): scores["javascript"] += 3
    if re.search(r"//|/\*", code): scores["javascript"] += 2
    if re.search(r";\s*$", code, re.M): scores["javascript"] += 2

    # TypeScript specific patterns
    if re.search(r":\s*(?:string|number|boolean|any|void|unknown|never)\b", code): scores["typescript"] += 8
    if re.search(r"\binterface\s+[A-Z]\w*|\btype\s+[A-Z]\w*\s*=", code): scores["typescript"] += 8

    # Rust, Go, Java, C++
    if re.search(r"\bfn\s+\w+\s*\(|\blet\s+mut\s+|\bimpl\b|println!\b", code): scores["rust"] += 8
    if re.search(r"\bpackage\s+\w+|\bfunc\s+(?:\(\w+\s+\*?\w+\)\s+)?\w+\s*\(|fmt\.Print", code): scores["go"] += 8
    if re.search(r"\bpublic\s+(?:static\s+)?(?:void|class|int|String)\b|\bSystem\.out\.", code): scores["java"] += 8
    if re.search(r"#include\s*<|\bstd::(?:cout|cin|vector|string)\b", code): scores["cpp"] += 8

    if scores["typescript"] >= 6:
        return "typescript"

    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return "javascript" if ("{" in code and "}" in code) or "//" in code or ";" in code else "python"


def classify_error_heuristic(code: str) -> str:
    """Lightweight rule-based heuristic for error categorization."""
    lower = code.lower()
    if any(k in lower for k in ["password", "secret", "eval(", "exec(", "query +", "sql", "select * from", "insert into", "drop table"]):
        return "security flaw"
    if any(k in lower for k in ["for ", "while "]) and ("range(" in lower or "i++" in lower):
        if any(k in lower for k in ["append", "sleep", "nested", "timeout"]):
            return "performance"
    open_p, close_p = code.count("("), code.count(")")
    open_b, close_b = code.count("{"), code.count("}")
    if open_p != close_p or open_b != close_b or (re.search(r":\s*$", code, re.M) is None and "def " in code):
        return "syntax error"
    return "logic error"


async def classify_code(code: str, language_hint: Optional[str] = None) -> ClassificationResult:
    """Executes Stage 1: detects language and classifies error type."""
    hint = language_hint.strip().lower() if language_hint else ""
    if hint and hint not in ["auto", "null", "none", "auto-detect", "undefined"]:
        detected_lang = hint
    else:
        detected_lang = detect_language_heuristic(code)

    err_type = classify_error_heuristic(code)
    if not hf_client.is_configured():
        return ClassificationResult(language=detected_lang, error_type=err_type, confidence=0.90, is_fallback=True)

    try:
        hf_res = await hf_client.query_model(
            model_id=CODEBERT_MODEL_ID,
            inputs=f"/* Detect error category for {detected_lang}: */ {code[:300]}",
            timeout=15.0,
        )
        if hf_res and isinstance(hf_res, list) and len(hf_res) > 0:
            score = float(hf_res[0].get("score", 0.92)) if isinstance(hf_res[0], dict) else 0.90
            return ClassificationResult(language=detected_lang, error_type=err_type, confidence=round(score, 2), is_fallback=False)
    except Exception as exc:
        logger.warning("Stage 1 CodeBERT failed (%s).", exc)

    return ClassificationResult(language=detected_lang, error_type=err_type, confidence=0.85, is_fallback=True)
