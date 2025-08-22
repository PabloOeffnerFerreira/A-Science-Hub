from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

STORAGE_DIR = BASE_DIR / "storage"
LOGS_DIR = STORAGE_DIR / "logs"
IMAGES_DIR = STORAGE_DIR / "images"
RESULTS_DIR = STORAGE_DIR / "results"
FORMULAS_DIR = STORAGE_DIR / "formulas"
FAVOURITES_DIR = STORAGE_DIR / "favourites"

UI_DIR = BASE_DIR / "UI"
ASSETS_DIR = UI_DIR / "assets"
PIN_ICON_PATH = ASSETS_DIR / "pin.png"
PIN_EMPTY_ICON_PATH = ASSETS_DIR / "pin_empty.png"

CORE_DIR = BASE_DIR / "core"
DATA_DIR = CORE_DIR / "data"
DATABASES_DIR = DATA_DIR / "databases"
INTDATABASES_DIR = DATABASES_DIR / "intdatabases"

TOOLS_DIR = BASE_DIR / "tools"

SETTINGS_PATH = INTDATABASES_DIR / "settings.json"
SETTINGS_DIR = SETTINGS_PATH.parent

WM_FILE = SETTINGS_DIR / "wm.json"

QUANTITIES_JSON_PATH = DATABASES_DIR / "quantities.json"
LOG_FILE = LOGS_DIR / "logs.json"
PTABLE_JSON_PATH = DATABASES_DIR / "ptable.json"

MINERALS_CSV = DATABASES_DIR / "minerals.csv"
GEO_FAVS_PATH = FAVOURITES_DIR / "geo_favs.json"