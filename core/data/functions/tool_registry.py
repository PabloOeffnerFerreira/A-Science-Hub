from pathlib import Path
from core.data.paths import TOOLS_DIR

EXCLUDED_DIRS = {"panel_tools", "__pycache__"}
EXCLUDED_FILES = {"__init__.py"}
ACRONYMS = {"UI", "GPU", "CPU", "DNA", "RNA", "ASH"}
DISPLAY_NAME_OVERRIDES = {"mol_ass": "Molecular Assembler"}

def humanize_tool_key(key: str) -> str:
    if key in DISPLAY_NAME_OVERRIDES:
        return DISPLAY_NAME_OVERRIDES[key]
    s = key.replace("-", "_")
    parts = [p for p in s.split("_") if p]
    words = []
    for p in parts:
        up = p.upper()
        if up in ACRONYMS:
            words.append(up)
        else:
            words.append(p.capitalize())
    return " ".join(words)

def discover_categories_and_tools():
    base = Path(TOOLS_DIR)
    categories = []
    mapping = {}
    if not base.exists():
        return categories, mapping
    for cat in sorted(x for x in base.iterdir() if x.is_dir() and x.name not in EXCLUDED_DIRS and not x.name.startswith(".")):
        categories.append(cat.name)
        tools = []
        for f in cat.glob("*.py"):
            if f.name in EXCLUDED_FILES or f.stem.startswith("_"):
                continue
            tools.append({"key": f.stem, "label": humanize_tool_key(f.stem)})
        tools.sort(key=lambda x: x["label"])
        mapping[cat.name] = tools
    return categories, mapping
