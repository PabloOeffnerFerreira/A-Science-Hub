from __future__ import annotations
from typing import Generator, Optional
from core.ai.client import ChatMessage, ChatRequest, ChatStreamer
from core.ai.ash_assistant.ash_prompts import system_for
from core.ai.ash_assistant.ash_retrieve import retrieve

def _mode_from_query(q: str) -> str:
    t = q.lower()
    if any(w in t for w in ("where ", "open ", "start", "shortcut", "settings")):
        return "nav"
    if any(w in t for w in ("explain", "bug")):
        return "explain"
    return "default"

def _context(snips: list[dict]) -> str:
    return "\n\n".join(f"[{i}] {s['id']} • {s['title']}\n{s['snippet']}"
                       for i,s in enumerate(snips,1))

def ash_answer_stream(user_query: str,
                      model: str = "dolphin3:8b",
                      temperature: float = 0.3,
                      max_tokens: int = 512) -> Generator[str, None, None]:
    snips = retrieve(user_query, k=4)
    system = system_for(_mode_from_query(user_query))
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user",
                    content=f"Question: {user_query}\n\nContext:\n{_context(snips)}\n\nAnswer:")
    ]
    req = ChatRequest(model=model, messages=messages,
                      temperature=temperature, top_p=0.9, top_k=40, max_tokens=max_tokens)
    for chunk in ChatStreamer.stream(req):
        if chunk: yield chunk

def extract_action_json(text: str) -> Optional[str]:
    for ln in reversed([l.strip() for l in text.splitlines() if l.strip()]):
        if ln.startswith("{") and ln.endswith("}"):
            return ln
    return None
