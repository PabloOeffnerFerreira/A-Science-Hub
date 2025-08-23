# core/ai/logger.py
from __future__ import annotations
import os, json, time
from typing import Any

class AIEventLogger:
    def __init__(self, logs_dir: str, max_bytes: int = 20_000_000):
        self.dir = logs_dir
        self.max = max_bytes
        os.makedirs(self.dir, exist_ok=True)
        self.path = self._current_path()

    def _current_path(self) -> str:
        # choose last index or start at 0001
        idx = 1
        while os.path.exists(self._fmt(idx)) and os.path.getsize(self._fmt(idx)) >= self.max:
            idx += 1
        return self._fmt(idx)

    def _fmt(self, idx: int) -> str:
        return os.path.join(self.dir, f"ai_events_{idx:04d}.jsonl")

    def log(self, typ: str, **kv: Any):
        try:
            if os.path.exists(self.path) and os.path.getsize(self.path) >= self.max:
                self.path = self._current_path()
            rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())}
            rec["type"] = typ
            rec.update(kv)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            # never raise into UI
            pass
