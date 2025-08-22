from __future__ import annotations
import csv, json, math, os
from typing import List, Dict, Any, Iterable, Optional

# --- Safe config from core.data.paths ---
MINERALS_CSV: Optional[str] = None          # path to your minerals CSV file
GEO_FAVS_PATH: Optional[str] = None         # path to favourites JSON file (a FILE, not a directory)

try:
    # Only import what actually exists in your paths module
    from core.data.paths import MINERALS_CSV as _MINERALS_CSV  # e.g. "…/databases/intdatabases/minerals.csv"
    MINERALS_CSV = _MINERALS_CSV
except Exception:
    pass

try:
    from core.data.paths import GEO_FAVS_PATH as _GEO_FAVS_PATH  # e.g. "…/databases/intdatabases/mineral_favs.json"
    GEO_FAVS_PATH = _GEO_FAVS_PATH
except Exception:
    pass


def _open_csv(path: str):
    """Open CSV with auto delimiter fallback (',' then ';')."""
    try:
        f = open(path, "r", encoding="utf-8")
        return csv.DictReader(f)  # default comma
    except Exception:
        raise

def load_minerals(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = csv_path or MINERALS_CSV
    rows: List[Dict[str, Any]] = []
    if not path or not os.path.exists(path):
        return rows

    # Try comma first; if the header collapses to 1 column, retry with semicolon.
    with open(path, "r", encoding="utf-8") as f:
        sample = f.read(4096)
        f.seek(0)
        sniff = csv.Sniffer()
        try:
            dialect = sniff.sniff(sample, delimiters=",;")
        except Exception:
            dialect = csv.excel  # default comma
        reader = csv.DictReader(f, dialect=dialect)

        for row in reader:
            # Normalise some numeric fields
            for k in ("Hardness", "HardnessMin", "HardnessMax", "SpecificGravity", "SG", "Density"):
                if k in row and row[k] not in (None, "", "NA", "N/A"):
                    try:
                        row[k] = float(str(row[k]).replace(",", "."))
                    except Exception:
                        pass
            rows.append(row)
    return rows


def save_json(obj: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_favs(path: Optional[str] = None) -> set:
    p = path or GEO_FAVS_PATH
    if not p or not os.path.exists(p):
        return set()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data if isinstance(data, list) else [])
    except Exception:
        return set()


def save_favs(favs: Iterable[str], path: Optional[str] = None) -> None:
    p = path or GEO_FAVS_PATH
    if not p:
        return
    save_json(list(favs), p)


def half_life_decay(N0: float, t: float, half_life: float) -> float:
    if half_life <= 0:
        raise ValueError("Half-life must be > 0")
    return N0 * (0.5 ** (t / half_life))


def estimate_age_from_remaining(remaining_frac: float, half_life: float) -> float:
    if not (0 < remaining_frac <= 1):
        raise ValueError("remaining_frac must be in (0,1]")
    if half_life <= 0:
        raise ValueError("half_life must be > 0")
    # remaining_frac = 0.5 ** (t / half_life) -> t = half_life * log2(1/remaining_frac)
    return half_life * (math.log(1.0 / remaining_frac, 2))
