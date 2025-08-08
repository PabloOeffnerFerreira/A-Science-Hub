import os
import json
import time
from PyQt6.QtCore import QObject, pyqtSignal
from core.data.paths import LOGS_DIR
from core.data.functions.log_signals import log_bus

LOG_FILE = os.path.join(LOGS_DIR, "logs.json")

class LogController(QObject):
    logs_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        os.makedirs(LOGS_DIR, exist_ok=True)

    def _load_logs(self):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_logs(self, logs):
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def add_log_entry(self, tool_name, action, data=None, tags=None, pinned=False):
        logs = self._load_logs()
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tool": tool_name,
            "action": action,
            "data": data,
            "tags": tags or [],
            "pinned": pinned
        }
        logs.insert(0, entry)
        self._save_logs(logs)
        log_bus.log_added.emit()
        return entry

    def load_logs(self):
        logs = self._load_logs()
        self.logs_updated.emit(logs)

    def delete_log(self, index):
        logs = self._load_logs()
        if 0 <= index < len(logs):
            del logs[index]
            self._save_logs(logs)
        self.load_logs()  # ensure UI refresh

    def clear_logs(self, ignore_pinned=True):
        logs = self._load_logs()
        if ignore_pinned:
            logs = [log for log in logs if log.get("pinned")]
        else:
            logs = []
        self._save_logs(logs)
        self.load_logs()

    def set_pin_state(self, index, state):
        logs = self._load_logs()
        if 0 <= index < len(logs):
            logs[index]["pinned"] = state
            self._save_logs(logs)
        self.load_logs()  # ensure UI refresh
