# core/ai/tokenizer.py
from __future__ import annotations

def estimate_tokens(messages: list[tuple[str, str]]):
    """
    Best-effort token estimate. Returns int or None if unavailable.
    `messages` = [(role, content), ...]
    """
    try:
        import tiktoken
        # Use a generic encoding
        enc = tiktoken.get_encoding("cl100k_base")
        total = 0
        for role, msg in messages:
            total += len(enc.encode(role)) + len(enc.encode(msg)) + 4
        return total
    except Exception:
        # fallback heuristic: ~4 chars per token
        try:
            chars = sum(len(r) + len(m) + 4 for r, m in messages)
            return max(1, chars // 4)
        except Exception:
            return None
