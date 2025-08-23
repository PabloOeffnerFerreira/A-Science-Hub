# core/ai/chat_store.py
from __future__ import annotations
import os, json, uuid
from typing import List, Tuple, Optional
from .client import ChatMessage

class ChatStore:
    def __init__(self, chats_dir: str):
        self.dir = chats_dir
        os.makedirs(self.dir, exist_ok=True)

    def new_session_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def _path(self, session_id: str) -> str:
        return os.path.join(self.dir, f"{session_id}.jsonl")

    def start_transcript(self, session_id: str):
        p = self._path(session_id)
        with open(p, "w", encoding="utf-8") as f:
            pass

    def append_turn(self, session_id: str, role: str, content: str):
        p = self._path(session_id)
        if not os.path.exists(p):
            self.start_transcript(session_id)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps({"role": role, "content": content}, ensure_ascii=False) + "\n")

    def load_transcript(self, path: str) -> Tuple[Optional[str], List[ChatMessage]]:
        sid = os.path.splitext(os.path.basename(path))[0]
        msgs: List[ChatMessage] = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    j = json.loads(line.strip() or "{}")
                    role = j.get("role"); content = j.get("content")
                    if role and content is not None:
                        msgs.append(ChatMessage(role=role, content=content))
            return sid, msgs
        except Exception:
            return sid, []

    def list_recent(self, limit: int = 12) -> list[str]:
        files = [f for f in os.listdir(self.dir) if f.endswith(".jsonl")]
        files.sort(key=lambda n: os.path.getmtime(os.path.join(self.dir, n)), reverse=True)
        return files[:limit]
