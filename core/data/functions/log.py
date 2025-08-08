import os
import json
import time
from core.data.paths import LOGS_DIR
from core.data.functions.log_signals import log_bus

LOG_FILE = os.path.join(LOGS_DIR, "logs.json")

def _load_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _save_logs(logs):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def _generate_action(tool_name, data):
    if data is None:
        return f"Used {tool_name}"
    if isinstance(data, (int, float, str)):
        return f"{tool_name} output: {data}"
    return f"{tool_name} executed"

def add_log_entry(tool_name, action=None, data=None, tags=None, pinned=False):
    logs = _load_logs()
    if not action:
        action = _generate_action(tool_name, data)
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tool": tool_name,
        "action": action,
        "data": data,
        "tags": tags or [],
        "pinned": pinned
    }
    logs.insert(0, entry)
    _save_logs(logs)

    # Emit global update signal
    log_bus.log_added.emit()
    return entry

def get_logs():
    return _load_logs()

def delete_log(index):
    logs = _load_logs()
    if 0 <= index < len(logs):
        del logs[index]
        _save_logs(logs)

def pin_log(index, pinned=True):
    logs = _load_logs()
    if 0 <= index < len(logs):
        logs[index]["pinned"] = pinned
        _save_logs(logs)

def clear_logs(ignore_pinned=True):
    logs = _load_logs()
    if ignore_pinned:
        logs = [log for log in logs if log.get("pinned")]
    else:
        logs = []
    _save_logs(logs)