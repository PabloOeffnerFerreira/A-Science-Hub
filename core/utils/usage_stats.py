import json, os, sqlite3
from core.data.paths import SETTINGS_PATH

DB_PATH = os.path.join("core","data","databases","intdatabases","tool_usage_log.sql")

def _fallback_last_tool():
    try:
        with open(SETTINGS_PATH,"r",encoding="utf-8") as f:
            s = json.load(f)
            return s.get("last_tool_opened")
    except:
        return None

def get_last_tool_opened():
    if not os.path.exists(DB_PATH):
        return _fallback_last_tool()
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT tool_name, created_at FROM tool_usage ORDER BY created_at DESC LIMIT 1")
        row = cur.fetchone()
        con.close()
        if row:
            return row[0]
        return _fallback_last_tool()
    except:
        return _fallback_last_tool()

def set_last_tool_opened(name: str):
    try:
        with open(SETTINGS_PATH,"r",encoding="utf-8") as f:
            s = json.load(f)
    except:
        s = {}
    s["last_tool_opened"] = name
    with open(SETTINGS_PATH,"w",encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
