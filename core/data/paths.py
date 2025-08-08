import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # root ASH/
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")
IMAGES_DIR = os.path.join(STORAGE_DIR, "images")
RESULTS_DIR = os.path.join(STORAGE_DIR, "results")
FORMULAS_DIR = os.path.join(STORAGE_DIR, "formulas")
FAVOURITES_DIR = os.path.join(STORAGE_DIR, "favourites")
PIN_ICON_PATH = os.path.join("UI", "assets", "pin.png")
PIN_EMPTY_ICON_PATH = os.path.join("UI", "assets", "pin_empty.png")
UI_DIR = os.path.join(BASE_DIR, "UI")
ASSETS_DIR = os.path.join(UI_DIR, "assets")