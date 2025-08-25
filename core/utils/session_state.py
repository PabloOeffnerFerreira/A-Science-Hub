import os, json
from datetime import datetime, timezone
from core.data.paths import SETTINGS_PATH

def initialize_session():
    data = {}
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}
    if not data.get("session_start"):
        data["session_start"] = datetime.now(timezone.utc).isoformat()

    os.makedirs(SETTINGS_PATH.parent, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)