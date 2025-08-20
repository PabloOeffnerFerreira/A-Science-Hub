from pathlib import Path
import json
from typing import Dict, Any
from core.data.paths import SETTINGS_PATH

_DEFAULTS: Dict[str, Any] = {"region": "EU", "quantity_mode": "quantity"}

def load_settings() -> Dict[str, Any]:
    p = Path(SETTINGS_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    else:
        data = {}
    return {**_DEFAULTS, **data}

def save_settings(data: Dict[str, Any]) -> None:
    p = Path(SETTINGS_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    merged = {**_DEFAULTS, **data}
    p.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

def get_setting(key: str, default: Any = None) -> Any:
    return load_settings().get(key, default)

def set_setting(key: str, value: Any) -> None:
    data = load_settings()
    data[key] = value
    save_settings(data)
