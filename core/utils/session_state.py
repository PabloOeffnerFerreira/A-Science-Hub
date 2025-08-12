import os, json
from datetime import datetime, timezone

SETTINGS_PATH = os.path.join("core","data","databases","intdatabases","settings.json")

def initialize_session():
    data = {}
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH,"r",encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}
    if not data.get("session_start"):
        data["session_start"] = datetime.now(timezone.utc).isoformat()
    with open(SETTINGS_PATH,"w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
