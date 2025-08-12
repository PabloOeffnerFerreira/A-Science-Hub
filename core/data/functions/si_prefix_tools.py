from core.data.units.conversion_data import conversion_data
from core.data.units.si_prefixes import si_prefixes

def collect_si_units():
    ordered = []
    seen = set()
    for _, data in conversion_data.items():
        for u in data.get("SI", []):
            if u not in seen:
                ordered.append(u)
                seen.add(u)
    return ordered

def build_unit_factors():
    factors = {}
    for _, data in conversion_data.items():
        units = data.get("units", {})
        for u in data.get("SI", []):
            if u in units:
                factors[u] = units[u]
    return factors

def compute_combined_and_base(value, in_prefix, in_unit, out_prefix):
    try:
        v = float(value)
    except ValueError:
        return None, None

    fin = float(si_prefixes.get(in_prefix, 1.0))
    fout = float(si_prefixes.get(out_prefix, 1.0))
    ufac = float(build_unit_factors().get(in_unit, 1.0))

    base_val = v * fin * ufac
    out_val = base_val / fout
    return out_val, base_val
