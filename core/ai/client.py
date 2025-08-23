from __future__ import annotations
import os, json
from dataclasses import dataclass
from typing import List, Optional, Generator

CHAT_URL = os.environ.get("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
GEN_URL  = os.environ.get("OLLAMA_GEN_URL",  "http://localhost:11434/api/generate")

@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str

@dataclass
class ChatRequest:
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    top_p: float = 1.0
    top_k: int = 0
    max_tokens: int = 2048
    seed: Optional[int] = None
    stop: Optional[List[str]] = None

def _payload_chat(req: ChatRequest) -> dict:
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    p = {
        "model": req.model,
        "messages": msgs,
        "stream": True,
        "options": {
            "temperature": req.temperature,
            "top_p": req.top_p,
            "top_k": req.top_k,
            "num_predict": req.max_tokens,
        },
    }
    if req.seed is not None:
        p["options"]["seed"] = int(req.seed)
    if req.stop:
        p["options"]["stop"] = req.stop
    return p

def _build_prompt(messages: List[ChatMessage]) -> str:
    """Build a simple chat-style prompt for /api/generate fallback."""
    lines = []
    for m in messages:
        if m.role == "system":
            lines.append(f"[System]\n{m.content}\n")
        elif m.role == "user":
            lines.append(f"[User]\n{m.content}\n")
        else:
            lines.append(f"[Assistant]\n{m.content}\n")
    lines.append("[Assistant]\n")  # model should continue here
    return "\n".join(lines)

def _payload_generate(req: ChatRequest) -> dict:
    p = {
        "model": req.model,
        "prompt": _build_prompt(req.messages),
        "stream": True,
        "options": {
            "temperature": req.temperature,
            "top_p": req.top_p,
            "top_k": req.top_k,
            "num_predict": req.max_tokens,
        },
    }
    if req.seed is not None:
        p["options"]["seed"] = int(req.seed)
    if req.stop:
        p["options"]["stop"] = req.stop
    return p

class ChatStreamer:
    """Thread-safe streaming via requests; compatible with old/new Ollama servers."""
    @staticmethod
    def stream(req: ChatRequest) -> Generator[Optional[str], None, None]:
        import requests
        # 1) Try /api/chat (newer servers)
        payload = _payload_chat(req)
        got_any = False
        try:
            with requests.post(CHAT_URL, json=payload, stream=True, timeout=180) as r:
                r.raise_for_status()
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    # New chat API: {"message":{"role":"assistant","content":"..."}}
                    chunk = (data.get("message", {}) or {}).get("content", "")
                    # Some older variants stream {"response":"..."}
                    if not chunk:
                        chunk = data.get("response", "")
                    if chunk:
                        got_any = True
                        yield chunk
        except Exception:
            # fall through to generate
            pass

        # 2) Fallback: if no content arrived, try /api/generate (older servers)
        if not got_any:
            gen_payload = _payload_generate(req)
            import requests
            with requests.post(GEN_URL, json=gen_payload, stream=True, timeout=180) as r:
                r.raise_for_status()
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    # /api/generate streams {"response":"...","done":false}
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk