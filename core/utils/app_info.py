import json, os
from core.data.paths import SETTINGS_PATH
from core.data.info import APP_NAME, VERSION, BUILD, STAGE

def _load_settings():
    try:
        with open(SETTINGS_PATH,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def get_app_snapshot():
    s = _load_settings()
    return {
        "app_title": APP_NAME,
        "language": s.get("language","en"),
        "region": s.get("region","EU"),
        "theme": s.get("theme","default"),
        "session_start": s.get("session_start"),
        "build": BUILD,
        "version": VERSION,
        "stage": STAGE,
    }