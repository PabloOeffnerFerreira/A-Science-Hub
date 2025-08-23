# tools/misc/ai_assistant.py
from __future__ import annotations
import sys
import os
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit,
    QListWidget, QListWidgetItem, QWidget, QSplitter, QFrame, QToolButton, QMenu,
    QFileDialog, QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtGui import QTextOption, QFont, QAction, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer

from PyQt6.QtCore import pyqtSignal

class _ModelLoader(QThread):
    models_ready = pyqtSignal(list)
    def run(self):
        try:
            from core.ai.models import list_ollama_models
            models = list_ollama_models()
        except Exception:
            models = []
        # always emit something so UI can unblock
        self.models_ready.emit(models or [])


# --- ASH integration: resolve storage dirs even if core/data/paths is missing ---
def _ensure_dir(p: str) -> str:
    os.makedirs(p, exist_ok=True)
    return p

def _default_storage_root() -> str:
    # Prefer ASH storage dir if available; else local.
    try:
        from core.data.paths import STORAGE_DIR  # type: ignore
        root = os.path.join(STORAGE_DIR, "ai")
    except Exception:
        root = os.path.join("storage", "ai")
    return _ensure_dir(root)

STORAGE_ROOT = _default_storage_root()
CHATS_DIR = _ensure_dir(os.path.join(STORAGE_ROOT, "chats"))
LOGS_DIR = _ensure_dir(os.path.join(STORAGE_ROOT, "logs"))
ATTACH_DIR = _ensure_dir(os.path.join(STORAGE_ROOT, "attachments"))

# --- AI backend helpers ---
from core.ai.models import list_ollama_models, pull_model_blocking, model_tooltip_map
from core.ai.prompts import system_prompt_for_mode, MODES
from core.ai.client import ChatRequest, ChatMessage, ChatStreamer
from core.ai.chat_store import ChatStore
from core.ai.logger import AIEventLogger
from core.ai.tokenizer import estimate_tokens

# ---------------- UI widgets: chat bubbles ----------------
class Bubble(QWidget):
    def __init__(self, text: str, role: str):
        super().__init__()
        self.role = role
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setTextFormat(Qt.TextFormat.PlainText)

        # explicit colors to avoid palette/theme surprises
        if role == "assistant":
            label_css = "color:#eaeaea; font-size:13px;"
            frame_css = "background:#1f1f1f; border-radius:10px; padding:8px;"
        else:
            label_css = "color:white; font-size:13px;"
            frame_css = "background:#2b5cff; border-radius:10px; padding:8px;"

        self.label.setStyleSheet(f"QLabel{{{label_css}}}")

        frame = QFrame()
        f_lay = QVBoxLayout(frame)
        f_lay.setContentsMargins(10, 8, 10, 8)
        frame.setStyleSheet(f"QFrame{{{frame_css}}}")
        f_lay.addWidget(self.label)
        lay.addWidget(frame)

    def set_text(self, text: str):
        self.label.setText(text)

    def append_text(self, more: str):
        if more:
            self.label.setText(self.label.text() + more)



class BubbleItem(QListWidgetItem):
    def __init__(self, role: str, text: str = ""):
        super().__init__()
        self.role = role
        self.text = text

# ---------------- Tool class ----------------
@dataclass
class SessionState:
    session_id: str
    model: str
    mode_key: str
    messages: List[ChatMessage] = field(default_factory=list)

class Tool(QDialog):
    TITLE = "AI Assistant"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.resize(980, 720)
        self._assistant_widget = None
        self._assistant_item = None

        # state
        self.models: List[str] = []
        self.tooltip_map: Dict[str, str] = {}
        self.logger = AIEventLogger(LOGS_DIR)
        self.store = ChatStore(CHATS_DIR)
        self.session = SessionState(
            session_id=self.store.new_session_id(),
            model="",
            mode_key="casual",
            messages=[]
        )
        self._current_ai_item: Optional[QListWidgetItem] = None
        self._streamer_thread: Optional[_StreamerThread] = None
        self._streaming = False

        self._build_ui()
        self._load_models()
        self._new_session(self.model_pick.currentText(), self.mode_pick.currentData())
        self._log_session_start()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)

        # Top bar
        top = QHBoxLayout()
        self.model_pick = QComboBox()
        self.model_pick.setMinimumWidth(220)

        self.mode_pick = QComboBox()
        for key, title in MODES.items():
            self.mode_pick.addItem(title, userData=key)
        self.mode_pick.setCurrentIndex(self.mode_pick.findData("casual"))

        self.token_lbl = QLabel("tokens: —")

        self.btn_new = QPushButton("New")
        self.btn_save = QPushButton("Export")
        self.btn_load = QPushButton("Load")
        self.btn_recent = QToolButton()
        self.btn_recent.setText("Recent")
        self.btn_recent.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.recent_menu = QMenu(self.btn_recent)
        self.btn_recent.setMenu(self.recent_menu)

        top.addWidget(QLabel("Model:")); top.addWidget(self.model_pick)
        top.addSpacing(10)
        top.addWidget(QLabel("Mode:")); top.addWidget(self.mode_pick)
        top.addStretch(1)
        top.addWidget(self.token_lbl)
        top.addSpacing(16)
        top.addWidget(self.btn_new); top.addWidget(self.btn_save)
        top.addWidget(self.btn_load); top.addWidget(self.btn_recent)
        root.addLayout(top)

        # Splitter: chat (left) / drawer (right)
        split = QSplitter()
        split.setOrientation(Qt.Orientation.Horizontal)
        # Chat list
        left = QWidget(); l_lay = QVBoxLayout(left); l_lay.setContentsMargins(0,0,0,0)
        self.chat = QListWidget()
        self.chat.setAlternatingRowColors(False)
        self.chat.setUniformItemSizes(False)
        self.chat.setStyleSheet("""
            QListWidget { background: #121212; color:#ddd; border:1px solid #222; }
        """)
        l_lay.addWidget(self.chat)
        split.addWidget(left)
        # Drawer: advanced params
        right = QWidget(); r_lay = QVBoxLayout(right)
        r_lay.setContentsMargins(12, 8, 12, 8)
        right.setMinimumWidth(260)

        adv = QGroupBox("Advanced parameters")
        form = QFormLayout(adv)
        self.temp = QDoubleSpinBox(); self.temp.setRange(0.0, 2.0); self.temp.setSingleStep(0.1); self.temp.setValue(0.7)
        self.top_p = QDoubleSpinBox(); self.top_p.setRange(0.0, 1.0); self.top_p.setSingleStep(0.05); self.top_p.setValue(1.0)
        self.top_k = QSpinBox(); self.top_k.setRange(0, 200); self.top_k.setValue(0)
        self.max_tok = QSpinBox(); self.max_tok.setRange(16, 32768); self.max_tok.setValue(2048)
        self.seed = QSpinBox(); self.seed.setRange(-1_000_000_000, 1_000_000_000); self.seed.setValue(0)
        self.stop_seq = QTextEdit(); self.stop_seq.setPlaceholderText("One stop sequence per line"); self.stop_seq.setFixedHeight(60)
        for w in (self.temp, self.top_p): w.setDecimals(2)
        form.addRow("Temperature", self.temp)
        form.addRow("top_p", self.top_p)
        form.addRow("top_k", self.top_k)
        form.addRow("max tokens", self.max_tok)
        form.addRow("seed (0=auto)", self.seed)
        form.addRow("stop seq", self.stop_seq)
        r_lay.addWidget(adv)
        r_lay.addStretch(1)
        split.addWidget(right)
        split.setStretchFactor(0, 4)
        split.setStretchFactor(1, 1)
        root.addWidget(split)

        # Input row
        bottom = QHBoxLayout()
        self.inp = QTextEdit()
        self.inp.setPlaceholderText("Type your question…  (Ctrl+Enter to send)")
        self.inp.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.inp.setFixedHeight(90)
        self.btn_send = QPushButton("Send")
        self.btn_clear = QPushButton("Clear")
        bottom.addWidget(self.inp, 1)
        bottom.addWidget(self.btn_clear)
        bottom.addWidget(self.btn_send)
        root.addLayout(bottom)

        # Status
        self.status = QLabel("")
        self.status.setStyleSheet("color:#a0a0a0; font-size:11px;")
        self.status.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status.setFixedHeight(18)  # << small, slim bar
        root.addWidget(self.status, 0)

        # Signals
        self.btn_send.clicked.connect(self._send)
        self.btn_clear.clicked.connect(self._clear_chat)
        self.btn_save.clicked.connect(self._export_markdown)
        self.btn_load.clicked.connect(self._load_chat_from_file)
        self.btn_new.clicked.connect(self._new_chat_button)
        self.model_pick.currentTextChanged.connect(self._model_changed)
        self.mode_pick.currentIndexChanged.connect(self._mode_changed)
        self.inp.textChanged.connect(self._update_token_count)
        # keyboard: Ctrl+Enter to send
        self.inp.installEventFilter(self)

        self._refresh_recent_menu()

    # Keyboard: Ctrl+Enter to send
    def eventFilter(self, obj, ev):
        from PyQt6.QtCore import QEvent
        if obj is self.inp and ev.type() == QEvent.Type.KeyPress:
            from PyQt6.QtGui import QKeySequence
            if ev.matches(QKeySequence.StandardKey.InsertParagraphSeparator) and ev.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._send()
                return True
        return super().eventFilter(obj, ev)

    # ---------- Model & session ----------
    def _load_models(self):
        # optimistic placeholder so UI doesn't block
        self.models = []
        self.model_pick.clear()
        self.model_pick.addItem("Loading models…")
        self.model_pick.setEnabled(False)

        # start background discovery
        self._mdl_thr = _ModelLoader(self)
        self._mdl_thr.models_ready.connect(self._on_models_loaded)
        self._mdl_thr.start()

        # guard: if nothing arrives in 3 seconds, fall back safely
        def _guard():
            if not self.models and self.model_pick.currentText() == "Loading models…":
                self._on_models_loaded([])  # triggers fallback defaults
        QTimer.singleShot(3000, _guard)

    def _on_models_loaded(self, names: list[str]):
        if not names:
            names = ["qwen2:7b", "mistral:7b", "gemma2:9b", "phi4:14b"]  # safe defaults
        self.models = names
        self.model_pick.setEnabled(True)
        self.model_pick.clear()
        self.tooltip_map = model_tooltip_map()
        for n in names:
            self.model_pick.addItem(n)
            tip = self.tooltip_map.get(n, "")
            if tip:
                idx = self.model_pick.findText(n)
                self.model_pick.setItemData(idx, tip, Qt.ItemDataRole.ToolTipRole)
        self.model_pick.setCurrentIndex(0)
        self.status.setText(f"Models ready ({len(names)})")



    def _new_session(self, model: str, mode_key: str):
        self.session = SessionState(
            session_id=self.store.new_session_id(),
            model=model,
            mode_key=mode_key,
            messages=[]
        )
        # start transcript file for this session
        self.store.start_transcript(self.session.session_id)

        self.chat.clear()
        self.status.setText(f"New session • model={model} • mode={MODES[mode_key]}")
        self._update_token_count()
        self._log_session_start()


    def _log_session_start(self):
        self.logger.log("session_start", model=self.session.model, mode=self.session.mode_key,
                        session_id=self.session.session_id)

    def _log_session_end(self, reason="user_closed"):
        self.logger.log("session_end", reason=reason, session_id=self.session.session_id)

    # ---------- Chat operations ----------
    def _append_bubble(self, role: str, text: str) -> QListWidgetItem:
        w = Bubble(text, role)
        li = QListWidgetItem()
        self.chat.addItem(li)
        self.chat.setItemWidget(li, w)

        # initial sizing so it isn't a tiny strip
        w.adjustSize()
        li.setSizeHint(w.sizeHint())

        # visual shift
        if role == "user":
            w.setStyleSheet(w.styleSheet() + " margin-left:120px;")
        else:
            w.setStyleSheet(w.styleSheet() + " margin-right:120px;")

        self.chat.scrollToBottom()
        return li



    def _update_last_ai_bubble(self, text: str):
        # replace widget content with updated text (streaming)
        row = self.chat.count() - 1
        if row < 0:
            return
        item = self.chat.item(row)
        w = self.chat.itemWidget(item)
        if isinstance(w, Bubble):
            # rebuild label content
            w.layout().itemAt(0).widget().layout().itemAt(0).widget().setText(text)
            self.chat.scrollToBottom()

    def _send(self):
        if self._streaming:
            return

        content = self.inp.toPlainText().strip()
        if not content:
            return

        model = self.model_pick.currentText()
        mode_key = self.mode_pick.currentData()

        # If model not installed, offer to pull
        if model not in self.models:
            ret = QMessageBox.question(
                self,
                "Model not installed",
                f"Model '{model}' is not available. Pull it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ret == QMessageBox.StandardButton.Yes:
                ok, msg = pull_model_blocking(model)
                if not ok:
                    QMessageBox.critical(self, "Pull failed", msg or "Unknown error")
                    return
                self._load_models()
            else:
                return

        # Build full message list
        sys_prompt = system_prompt_for_mode(mode_key)
        messages = []
        if sys_prompt.strip():
            messages.append(ChatMessage(role="system", content=sys_prompt))
        for m in self.session.messages:
            messages.append(m)
        messages.append(ChatMessage(role="user", content=content))

        # Append user bubble
        self._append_bubble("user", content)

        # Append assistant placeholder and keep direct ref
        ai_item = self._append_bubble("assistant", "")
        row = self.chat.count() - 1
        self._assistant_item = self.chat.item(row)
        self._assistant_widget = self.chat.itemWidget(self._assistant_item)

        # Clear input
        self.inp.clear()
        self._update_token_count()

        # Log user event
        self.logger.log("user", text=content, session_id=self.session.session_id)

        # Start streamer thread
        req = ChatRequest(
            model=model,
            messages=messages,
            temperature=self.temp.value(),
            top_p=self.top_p.value(),
            top_k=self.top_k.value(),
            max_tokens=self.max_tok.value(),
            seed=None if self.seed.value() == 0 else self.seed.value(),
            stop=[s for s in self.stop_seq.toPlainText().splitlines() if s.strip()],
        )

        self._streamer_thread = _StreamerThread(req)
        self._streamer_thread.partial.connect(self._on_chunk)
        self._streamer_thread.finished_resp.connect(self._on_complete)
        self._streamer_thread.failed.connect(self._on_failed)

        self._streaming = True
        self.status.setText("Streaming…")

        import time
        self._t_start = time.perf_counter()
        self._out_chars = 0

        self._streamer_thread.start()

    def _on_chunk(self, chunk: str):
        if self._assistant_widget and isinstance(self._assistant_widget, Bubble):
            self._assistant_widget.append_text(chunk)
            # grow the row as text grows
            self._assistant_widget.adjustSize()
            if self._assistant_item:
                self._assistant_item.setSizeHint(self._assistant_widget.sizeHint())
            self.chat.scrollToBottom()
        self.logger.log("ai_stream", chunk=chunk, session_id=self.session.session_id)

    def _on_complete(self, full_text: str):
        self._streaming = False
        if not full_text.strip() and self._assistant_widget:
            full_text = self._assistant_widget.label.text()
        # final size pass
        if self._assistant_widget and self._assistant_item:
            self._assistant_widget.adjustSize()
            self._assistant_item.setSizeHint(self._assistant_widget.sizeHint())

        self.status.setText("Ready.")
        dt_ms = int((time.perf_counter() - getattr(self, "_t_start", time.perf_counter())) * 1000)
        self.logger.log("ai_complete", ms=dt_ms, chars=getattr(self, "_out_chars", 0), session_id=self.session.session_id)

        # commit to session + autosave
        self.session.messages.append(ChatMessage(role="user", content=self._last_user_text()))
        self.session.messages.append(ChatMessage(role="assistant", content=full_text))
        self.store.append_turn(self.session.session_id, "user", self._last_user_text())
        self.store.append_turn(self.session.session_id, "assistant", full_text)

        self._update_token_count()
        self._refresh_recent_menu()

    def _on_failed(self, err: str):
        self._streaming = False
        self.status.setText("Error.")
        self.logger.log("error", where="stream", message=err, session_id=self.session.session_id)
        QMessageBox.critical(self, "AI Error", err)

    def _last_user_text(self) -> str:
        # Find the last user bubble’s text from the list
        for i in range(self.chat.count() - 1, -1, -1):
            item = self.chat.item(i)
            w = self.chat.itemWidget(item)
            if isinstance(w, Bubble) and w.property("role") == "user":
                return w.layout().itemAt(0).widget().layout().itemAt(0).widget().text()
        return ""

    # ---------- Utilities ----------
    def _clear_chat(self):
        if self._streaming:
            return
        self.chat.clear()
        self.session.messages.clear()
        self.store.start_transcript(self.session.session_id)  # reset file
        self._update_token_count()

    def _export_markdown(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export chat", CHATS_DIR, "Markdown (*.md)")
        if not path:
            return
        md = []
        md.append(f"# Chat — session {self.session.session_id}\n")
        md.append(f"_Model: {self.session.model} | Mode: {MODES[self.session.mode_key]}_\n")
        for m in self.session.messages:
            who = "You" if m.role == "user" else ("Assistant" if m.role == "assistant" else "System")
            md.append(f"**{who}:**\n\n{m.content}\n\n---\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
        self.status.setText(f"Exported to {path}")

    def _load_chat_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load transcript", CHATS_DIR, "JSON Lines (*.jsonl)")
        if not path:
            return
        sid, msgs = self.store.load_transcript(path)
        if not msgs:
            QMessageBox.warning(self, "Load failed", "No messages found in file.")
            return
        self._new_session(self.model_pick.currentText(), self.mode_pick.currentData())
        self.session.session_id = sid or self.session.session_id
        self.session.messages = msgs
        # rebuild UI
        self.chat.clear()
        for m in msgs:
            self._append_bubble("assistant" if m.role == "assistant" else ("user" if m.role == "user" else "system"),
                                m.content)
        self._update_token_count()

    def _new_chat_button(self):
        if self._streaming:
            return
        self._new_session(self.model_pick.currentText(), self.mode_pick.currentData())

    def _model_changed(self, name: str):
        self.session.model = name
        self.status.setText(f"Model set: {name}")

    def _mode_changed(self, idx: int):
        key = self.mode_pick.itemData(idx)
        self.session.mode_key = key
        self.status.setText(f"Mode: {MODES[key]}")

    def _update_token_count(self):
        # do a light estimate; ignore if tokenizer not present
        try:
            msgs = []
            sp = system_prompt_for_mode(self.session.mode_key)
            if sp.strip():
                msgs.append(("system", sp))
            for m in self.session.messages:
                msgs.append((m.role, m.content))
            user_text = self.inp.toPlainText().strip()
            if user_text:
                msgs.append(("user", user_text))
            n = estimate_tokens(msgs)
            if n is None:
                self.token_lbl.setText("tokens: —")
            else:
                css = "color:#ddd;"
                if n > 7000:
                    css = "color:#ff4d4d;"
                elif n > 3500:
                    css = "color:#ffb84d;"
                self.token_lbl.setStyleSheet(css)
                self.token_lbl.setText(f"tokens: {n}")
        except Exception:
            self.token_lbl.setText("tokens: —")
    def _refresh_recent_menu(self):
        # rebuild the “Recent” menu from saved transcripts
        self.recent_menu.clear()
        recents = self.store.list_recent(limit=12)
        if not recents:
            act = QAction("(no recent chats)", self)
            act.setEnabled(False)
            self.recent_menu.addAction(act)
            return

        for fname in recents:
            # show the short session id (without .jsonl)
            sid = fname.rsplit(".", 1)[0]
            act = QAction(sid, self)
            full_path = os.path.join(CHATS_DIR, fname)
            # capture full_path by default arg to avoid late-binding in lambdas
            act.triggered.connect(lambda _, p=full_path: self._load_recent(p))
            self.recent_menu.addAction(act)

    def _load_recent(self, path: str):
        sid, msgs = self.store.load_transcript(path)
        if not msgs:
            QMessageBox.warning(self, "Load failed", "No messages found in file.")
            return
        # start a fresh UI session but reuse loaded sid/messages
        self._new_session(self.model_pick.currentText(), self.mode_pick.currentData())
        if sid:
            self.session.session_id = sid
        self.session.messages = msgs
        self.chat.clear()
        for m in msgs:
            role = "assistant" if m.role == "assistant" else ("user" if m.role == "user" else "system")
            self._append_bubble(role, m.content)
        self.status.setText(f"Loaded session {self.session.session_id}")
        self._update_token_count()

    def closeEvent(self, e):
        try:
            self._log_session_end()
        finally:
            return super().closeEvent(e)

# --------- Thread wrapper around async/stream client ----------
class _StreamerThread(QThread):
    partial = pyqtSignal(str)
    finished_resp = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, req: ChatRequest):
        super().__init__()
        self.req = req

    def run(self):
        try:
            chunks = []
            for chunk in ChatStreamer.stream(self.req):
                if chunk is None:
                    continue
                self.partial.emit(chunk)
                chunks.append(chunk)
            self.finished_resp.emit("".join(chunks))
        except Exception as e:
            self.failed.emit(str(e))
