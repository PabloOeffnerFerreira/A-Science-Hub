from core.data.units.conversion_data import conversion_data
from core.data.units.si_prefixes import si_prefixes

_PREFIX_ORDER = ["Y","Z","E","P","T","G","M","k","h","da","","d","c","m","μ","n","p","f","a","z","y"]

def ordered_prefixes():
    return [p for p in _PREFIX_ORDER if p in si_prefixes]

def si_bases_for_category(category: str):
    d = conversion_data.get(category, {})
    s = d.get("SI") or d.get("si") or d.get("si_units") or d.get("SI_UNITS") or []
    return set(s)

def units_for_category(category: str):
    d = conversion_data.get(category, {})
    u = d.get("units", {})
    return list(u.keys())

def supports_si(category: str, base_unit: str) -> bool:
    return base_unit in si_bases_for_category(category)

def parse_number(s: str):
    t = (s or "").strip().replace(",", ".")
    try:
        return float(t)
    except:
        return None

def apply_prefix(value, prefix):
    """Apply an SI prefix factor to a value."""
    if not prefix:
        return value
    factor = si_prefixes.get(prefix, None)
    if factor is None:
        return value
    return value * factor

def compose_label(prefix: str, base_unit: str) -> str:
    return f"{prefix}{base_unit}" if prefix and base_unit else base_unit

def convert(value: float, from_unit: str, to_unit: str, category: str) -> float:
    if category == "Temperature":
        fu, tu = from_unit.strip(), to_unit.strip()
        if fu == "K": K = value
        elif fu == "C": K = value + 273.15
        elif fu == "F": K = (value - 32.0) * (5.0/9.0) + 273.15
        else: raise ValueError("bad temp unit")
        if tu == "K": return K
        elif tu == "C": return K - 273.15
        elif tu == "F": return (K - 273.15) * (9.0/5.0) + 32.0
        else: raise ValueError("bad temp unit")
    d = conversion_data.get(category, {})
    u = d.get("units", {})
    if from_unit not in u or to_unit not in u:
        raise ValueError("unit not in category")
    base = value * u[from_unit]
    return base / u[to_unit]
