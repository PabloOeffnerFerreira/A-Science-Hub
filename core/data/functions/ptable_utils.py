
"""
Utilities to access element data (oxidation states, isotopes, symbols) from ptable.json,
with guarded fallbacks to o_states.json if oxidation states are not present.
"""
from __future__ import annotations
import os, json
from typing import Dict, List, Any, Optional

# Try to import project paths, but guard in case constants are absent
try:
    import core.data.paths as paths
except Exception:
    paths = None  # type: ignore

_PTABLE_CACHE: Optional[Dict[str, Any]] = None
_OSTATES_CACHE: Optional[Dict[str, List[int]]] = None

def _resolve_ptable_path() -> str:
    # Preferred: a constant in paths (e.g., PTABLE_JSON_PATH)
    for name in ("PTABLE_JSON_PATH", "PERIODIC_TABLE_PATH", "PTABLE_PATH"):
        if paths and hasattr(paths, name):
            return getattr(paths, name)
    # Common project location
    common = os.path.join("core", "data", "databases", "ptable.json")
    if os.path.exists(common):
        return common
    # Fallback to working dir or sandbox path
    for candidate in ("ptable.json", "/mnt/data/ptable.json"):
        if os.path.exists(candidate):
            return candidate
    return common  # last resort

def _resolve_ostates_path() -> Optional[str]:
    # Preferred constant if defined
    for name in ("O_STATES_PATH", "OSTATES_PATH"):
        if paths and hasattr(paths, name):
            p = getattr(paths, name)
            if os.path.exists(p):
                return p
    # Common location
    common = os.path.join("core", "data", "databases", "o_states.json")
    if os.path.exists(common):
        return common
    # Sandbox fallback
    if os.path.exists("/mnt/data/core/data/databases/o_states.json"):
        return "/mnt/data/core/data/databases/o_states.json"
    return None

def load_ptable() -> Dict[str, Any]:
    global _PTABLE_CACHE
    if _PTABLE_CACHE is not None:
        return _PTABLE_CACHE
    path = _resolve_ptable_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    _PTABLE_CACHE = data
    return data

def _load_ostates() -> Dict[str, List[int]]:
    global _OSTATES_CACHE
    if _OSTATES_CACHE is not None:
        return _OSTATES_CACHE
    path = _resolve_ostates_path()
    data: Dict[str, List[int]] = {}
    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # normalise to list[int]
            for k, v in raw.items():
                if isinstance(v, list):
                    data[k] = sorted({int(x) for x in v})
        except Exception:
            pass
    _OSTATES_CACHE = data
    return data

def list_elements() -> List[str]:
    """Return a sorted list of available element symbols."""
    pt = load_ptable()
    symbols: List[str] = []
    if isinstance(pt, dict):
        # ptable could be {"elements": [...]} or {"H": {...}, "He": {...}, ...}
        if "elements" in pt and isinstance(pt["elements"], list):
            for e in pt["elements"]:
                sym = e.get("symbol") or e.get("Symbol") or e.get("sym")
                if sym:
                    symbols.append(sym)
        else:
            for k in pt.keys():
                if isinstance(k, str) and 1 <= len(k) <= 3:
                    symbols.append(k)
    symbols = sorted(set(symbols), key=lambda s: (len(s), s))
    return symbols

def get_element(symbol: str) -> Dict[str, Any]:
    """Return the raw element dict for a given symbol, or {}."""
    pt = load_ptable()
    if "elements" in pt and isinstance(pt["elements"], list):
        for e in pt["elements"]:
            sym = e.get("symbol") or e.get("Symbol") or e.get("sym")
            if str(sym).capitalize() == symbol.capitalize():
                return e
    # Direct mapping by key
    if symbol in pt and isinstance(pt[symbol], dict):
        return pt[symbol]
    return {}

def get_isotopes(symbol: str) -> List[int]:
    """Return a list of known mass numbers for the element; empty if unknown."""
    e = get_element(symbol)
    # possible keys
    iso = e.get("isotopes") or e.get("Isotopes") or e.get("masses")
    masses: List[int] = []
    if isinstance(iso, list):
        # could be list of ints or dicts with 'mass'/'A'
        for x in iso:
            if isinstance(x, int):
                masses.append(x)
            elif isinstance(x, dict):
                for k in ("A", "mass_number", "massNumber", "mass", "A_number"):
                    if k in x:
                        try:
                            masses.append(int(x[k]))
                            break
                        except Exception:
                            pass
    return sorted({m for m in masses})

def get_default_isotope(symbol: str) -> Optional[int]:
    """
    Try to return the most abundant isotope from ptable.
    If abundances are not provided, return the lowest mass number if available.
    """
    e = get_element(symbol)
    iso = e.get("isotopes") or e.get("Isotopes") or e.get("masses")
    best = None
    best_ab = -1.0
    if isinstance(iso, list):
        for x in iso:
            if isinstance(x, dict):
                a = None
                for k in ("abundance", "abund", "rel_abundance", "relAbundance", "natural"):
                    if k in x:
                        try:
                            a = float(x[k])
                        except Exception:
                            a = None
                        break
                A = None
                for k in ("A", "mass_number", "massNumber", "mass"):
                    if k in x:
                        try:
                            A = int(x[k])
                        except Exception:
                            A = None
                        break
                if A is not None:
                    if a is None:
                        # keep as fallback
                        if best is None:
                            best = A
                    else:
                        if a > best_ab:
                            best_ab = a
                            best = A
    if best is not None:
        return best
    masses = get_isotopes(symbol)
    return masses[0] if masses else None

def get_oxidation_states(symbol: str) -> List[int]:
    """
    Return oxidation states for the symbol.
    Tries multiple keys in ptable; falls back to o_states.json if needed.
    """
    e = get_element(symbol)
    # keys to check in ptable element entry
    for k in ("oxidation_states", "oxidationStates", "ox_states", "oxStates", "states", "common_ions"):
        val = e.get(k)
        if isinstance(val, list) and val:
            try:
                return sorted({int(x) for x in val})
            except Exception:
                pass
        # sometimes 'common_ions' may be like ["+2", "3+", "-1"]
        if isinstance(val, list) and val:
            norm = set()
            for x in val:
                try:
                    s = str(x).strip().replace("+", "")
                    if s.endswith("+"):
                        s = s[:-1]
                    if s.endswith("−") or s.endswith("-"):
                        s = "-" + s[:-1]
                    norm.add(int(s))
                except Exception:
                    continue
            if norm:
                return sorted(norm)
    # fallback
    ost = _load_ostates()
    if symbol in ost:
        return sorted({int(x) for x in ost[symbol]})
    return []
