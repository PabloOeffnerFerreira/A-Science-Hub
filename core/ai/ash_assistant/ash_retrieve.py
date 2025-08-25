from __future__ import annotations
from pathlib import Path
import json
import re
from typing import Any, Dict, List

# KB lives next to this module in ./kb
KB_DIR = Path(__file__).resolve().parent / "kb"

# ---------- utils ------------------------------------------------------------

_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")

def _flatten_text(x: Any) -> str:
    """Recursively flatten strings/lists/dicts/numbers into a single text blob."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, (int, float, bool)):
        return str(x)
    if isinstance(x, dict):
        return " ".join(_flatten_text(v) for v in x.values())
    if isinstance(x, (list, tuple, set)):
        return " ".join(_flatten_text(v) for v in x)
    return str(x)

def _normalize_doc(raw: Dict[str, Any], path: Path) -> Dict[str, Any]:
    """Bring arbitrary JSON to a stable schema."""
    doc_id = raw.get("id") or path.stem
    ns = raw.get("ns") or path.parent.name
    title = raw.get("title") or raw.get("name") or doc_id.replace("_", " ")
    view = raw.get("view") or {}
    body_src = raw.get("body", raw.get("text", raw))
    body = _flatten_text(body_src)
    return {"id": doc_id, "ns": ns, "title": title, "view": view, "body": body}

def _load_kb() -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    if not KB_DIR.exists():
        return docs
    for p in KB_DIR.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    docs.append(_normalize_doc(item, p))
        elif isinstance(data, dict):
            docs.append(_normalize_doc(data, p))
    return docs

_DOCS_CACHE: List[Dict[str, Any]] | None = None

def _docs() -> List[Dict[str, Any]]:
    global _DOCS_CACHE
    if _DOCS_CACHE is None:
        _DOCS_CACHE = _load_kb()
    return _DOCS_CACHE

# ---------- retrieval --------------------------------------------------------

def retrieve(query: str, k: int = 6, namespaces: List[str] | None = None) -> List[Dict[str, Any]]:
    """
    Lightweight lexical retriever.
    Returns list of {id, ns, title, view, body, snippet}.
    """
    docs = _docs()
    if namespaces:
        docs = [d for d in docs if d.get("ns") in namespaces]

    q = query.lower().strip()
    terms = [t for t in _WORD_RE.findall(q) if len(t) > 1]
    if not terms:
        terms = q.split()

    def score(d: Dict[str, Any]) -> float:
        title = d.get("title", "")
        text = (title + " " + d.get("body", "")).lower()

        s = 0.0
        # exact phrase boost
        if q and q in text:
            s += 2.5
        # title boosts
        tl = title.lower()
        s += sum(1.5 for t in terms if t in tl)
        # body term hits
        s += sum(1.0 for t in terms if t in text)
        # tiny length normalization
        s += min(len(title) / 100.0, 1.0) * 0.2
        return s

    ranked = sorted(docs, key=score, reverse=True)
    out: List[Dict[str, Any]] = []
    for d in ranked[:k]:
        body = d.get("body", "")
        if not body:
            snip = ""
        else:
            idx = 0
            for t in terms:
                p = body.lower().find(t)
                if p != -1:
                    idx = p
                    break
            start = max(0, idx - 120)
            end = min(len(body), start + 300)
            snip = body[start:end].strip()
        out.append({**d, "snippet": snip})
    return out
