from __future__ import annotations
from typing import Generator, Optional, Tuple
import json
import re

# uses your existing client + retriever + prompts modules
from core.ai.client import ChatMessage, ChatRequest, ChatStreamer
from core.ai.ash_assistant.ash_prompts import system_for
from core.ai.ash_assistant.ash_retrieve import retrieve

# ---- small helpers ---------------------------------------------------------

def _mode_from_query(q: str) -> str:
    t = q.lower()
    if any(w in t for w in ("where ", "open ", "start", "shortcut", "settings", "navigate", "show me")):
        return "nav"
    if any(w in t for w in ("explain", "why", "how", "bug", "error", "help")):
        return "explain"
    return "default"

def _context(snips: list[dict]) -> str:
    """Render retrieval snippets into a compact context block."""
    return "\n\n".join(
        f"[{i}] {s['id']} • {s['title']}\n{s['snippet']}"
        for i, s in enumerate(snips, 1)
    )
# --- Back-compat helpers (for tools/misc/ash_assistant.py) -------------------

def extract_action_json(full_text: str):
    """
    Return the parsed action dict if the last non-empty line (or a trailing ```json block```)
    is a JSON object; otherwise None.
    """
    text, act = split_text_and_action(full_text)
    return act

def strip_action_from_text(full_text: str) -> str:
    """
    Return only the natural-language answer, with any trailing action JSON removed.
    """
    text, _ = split_text_and_action(full_text)
    return text

# Accepts either a bare JSON last line or the JSON wrapped in a code fence.
_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*\})\s*```", re.DOTALL)

def _maybe_extract_action_blob(s: str) -> Optional[str]:
    """Return a JSON blob if the response contains one, else None."""
    # 1) prefer an explicit ```json ... ``` block
    m = _JSON_BLOCK_RE.search(s)
    if m:
        return m.group(1).strip()

    # 2) otherwise try the last non-empty line as JSON
    lines = [ln for ln in s.splitlines() if ln.strip()]
    if not lines:
        return None
    last = lines[-1].strip()
    if last.startswith("{") and last.endswith("}"):
        return last
    return None

def split_text_and_action(s: str) -> Tuple[str, Optional[dict]]:
    """Split assistant output into (text_without_action, action_dict|None)."""
    blob = _maybe_extract_action_blob(s)
    if not blob:
        return s, None
    try:
        action = json.loads(blob)
    except Exception:
        return s, None

    # remove the blob from the text
    text = s.replace(blob, "").strip()
    # also remove any enclosing code fence if present
    text = _JSON_BLOCK_RE.sub("", text).strip()
    return text, action

# ---- main API --------------------------------------------------------------

DEFAULT_MODEL = "dolphin3:8b"  # set whatever Ollama model you actually run

def ash_answer_stream(
    user_query: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
) -> Generator[str, None, None]:
    """
    Stream a final answer (and possibly an action JSON in the last line).
    The UI can use `split_text_and_action` to separate them.
    """
    # 1) retrieve KB
    snips = retrieve(user_query, k=6)
    ctx = _context(snips)
    mode = _mode_from_query(user_query)

    # 2) build messages
    system = system_for(mode)  # <— FIX: only pass the kind
    user_content = (
        f"QUESTION:\n{user_query}\n\n"
        f"CONTEXT (use ONLY this):\n{ctx if ctx else '(no matching context)'}\n\n"
        "REQUIREMENTS:\n"
        "- If the answer is not in the CONTEXT, reply: \"I don't have that in ASH yet.\"\n"
        "- Do NOT invent ids or facts.\n"
        "- Answer concisely in plain text first.\n"
        "- Only if an in-app action is clearly needed AND its exact id appears in CONTEXT, "
        "output ONE JSON object on the LAST line."
    )

    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=user_content),
    ]

    # 3) stream from your Ollama client
    req = ChatRequest(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    for chunk in ChatStreamer.stream(req):
        yield chunk
