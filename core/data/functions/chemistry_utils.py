
from __future__ import annotations
import json, re, math
from pathlib import Path
from collections import defaultdict

# -------- Element data loader (unchanged interface) --------
def load_element_data():
    try:
        from core.data.paths import PTABLE_JSON_PATH as PTPATH
    except Exception:
        PTPATH = None
    if PTPATH and Path(PTPATH).exists():
        path = Path(PTPATH)
    else:
        candidates = [
            Path("data/databases/PeriodicTableJSON.json"),
            Path("data/databases/elements.json"),
            Path("databases/PeriodicTableJSON.json"),
            Path("PeriodicTableJSON.json"),
        ]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            raise FileNotFoundError("Periodic table JSON not found. Define core.data.paths.PTABLE_JSON_PATH or place the file in data/databases.")
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "elements" in data:
        mapping = {el.get("symbol"): el for el in data["elements"] if el.get("symbol")}
    else:
        mapping = data
    # normalize commonly used keys
    for sym, el in list(mapping.items()):
        if el is None: 
            continue
        if "number" not in el and "AtomicNumber" in el:
            el["number"] = el.get("AtomicNumber")
        if "atomic_mass" not in el and "AtomicMass" in el:
            el["atomic_mass"] = el.get("AtomicMass")
        if "melt" not in el and "MeltingPoint" in el:
            el["melt"] = el.get("MeltingPoint")
        if "boil" not in el and "BoilingPoint" in el:
            el["boil"] = el.get("BoilingPoint")
    return mapping

# -------- Category Colour Map --------

CATEGORY_COLOUR_MAP = {
    "alkali metal": "#FF6666",
    "alkaline earth metal": "#FFDEAD",
    "transition metal": "#FFB347",
    "post-transition metal": "#FFD700",
    "metalloid": "#ADFF2F",
    "polyatomic nonmetal": "#90EE90",
    "diatomic nonmetal": "#98FB98",
    "nonmetal": "#90EE90",          # generic fallback
    "halogen": "#87CEFA",
    "noble gas": "#D8BFD8",
    "lanthanide": "#FF69B4",
    "actinide": "#BA55D3",
}
# -------- Robust atomic mass extraction --------
_mass_cleanup_re = re.compile(r"[^0-9.eE+-]")

def atomic_mass_u(el: dict) -> float | None:
    # Try isotope's "atomic_mass" if a single stable isotope exists
    iso_list = el.get("isotopes") or []
    if isinstance(iso_list, list) and len(iso_list) == 1:
        val = iso_list[0].get("atomic_mass")
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                return float(_mass_cleanup_re.sub("", val))
            except Exception:
                pass
    # Fallback to element-level mass
    val = el.get("atomic_mass") or el.get("AtomicMass")
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(_mass_cleanup_re.sub("", val))
        except Exception:
            return None
    return None

# -------- Formula parsing (supports · hydrates) --------
_TOKEN = re.compile(r'([A-Z][a-z]?|\(|\)|\d+)')

def parse_formula(formula: str) -> dict[str, int]:
    tokens = _TOKEN.findall(formula)
    stack: list[dict[str, int]] = [defaultdict(int)]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == '(':
            stack.append(defaultdict(int)); i += 1
        elif tok == ')':
            if len(stack) == 1:
                raise ValueError("Unmatched ')'")
            group = stack.pop(); i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i]); i += 1
            for el, cnt in group.items():
                stack[-1][el] += cnt * mult
        elif re.match(r'[A-Z][a-z]?$', tok):
            el = tok; i += 1
            cnt = 1
            if i < len(tokens) and tokens[i].isdigit():
                cnt = int(tokens[i]); i += 1
            stack[-1][el] += cnt
        else:
            raise ValueError(f"Unexpected token: {tok}")
    if len(stack) != 1:
        raise ValueError("Unmatched parentheses")
    return dict(stack[0])

def parse_hydrate(formula: str) -> dict[str, int]:
    total: dict[str, int] = defaultdict(int)
    for part in formula.split('·'):
        m = re.match(r'^(\d+)(.*)$', part)
        mult = int(m.group(1)) if m else 1
        sub = m.group(2) if m else part
        counts = parse_formula(sub)
        for el, cnt in counts.items():
            total[el] += cnt * mult
    return dict(total)

# -------- Reaction balancing without sympy --------
def _reaction_matrix(reactants, products):
    element_set = set()
    all_formulas = reactants + products
    parsed = [parse_formula(f) for f in all_formulas]
    for d in parsed:
        element_set.update(d.keys())
    elements = sorted(element_set)
    rows = []
    for el in elements:
        row = []
        for d in parsed[:len(reactants)]:
            row.append(d.get(el, 0))
        for d in parsed[len(reactants):]:
            row.append(-d.get(el, 0))
        rows.append(row)
    return rows

def _integer_nullspace(A):
    # Simple rational RREF to find one integer nullspace vector
    from fractions import Fraction
    m = len(A); n = len(A[0]) if m else 0
    M = [[Fraction(x) for x in row] for row in A]
    r = c = 0
    pivots = []
    while r < m and c < n:
        # find pivot row
        pr = None
        for i in range(r, m):
            if M[i][c] != 0:
                pr = i; break
        if pr is None:
            c += 1; continue
        M[r], M[pr] = M[pr], M[r]
        piv = M[r][c]
        M[r] = [x / piv for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                fac = M[i][c]
                M[i] = [a - fac*b for a, b in zip(M[i], M[r])]
        pivots.append((r, c))
        r += 1; c += 1
    pivot_cols = {c for _, c in pivots}
    free = [j for j in range(n) if j not in pivot_cols]
    if not free:
        # no free vars; try trivial vector
        return [0]*n
    j = free[0]
    x = [Fraction(0)]*n
    x[j] = Fraction(1)
    for r, c in reversed(pivots):
        s = sum(M[r][k]*x[k] for k in range(c+1, n))
        x[c] = -s
    # scale to integers
    den_lcm = 1
    for val in x:
        den_lcm = (den_lcm * val.denominator) // math.gcd(den_lcm, val.denominator)
    ints = [int(val * den_lcm) for val in x]
    # normalize sign
    if any(v < 0 for v in ints):
        ints = [-v for v in ints]
    # if all zeros (degenerate), fallback to ones
    if not any(ints):
        ints = [1]*n
    return ints

def parse_reaction(text: str):
    parts = re.split(r'->|=', text)
    if len(parts) != 2:
        raise ValueError("Reaction must contain one '->' or '='")
    left = [s.strip() for s in parts[0].split('+') if s.strip()]
    right = [s.strip() for s in parts[1].split('+') if s.strip()]
    return left, right

def balance_reaction(text: str):
    reactants, products = parse_reaction(text)
    A = _reaction_matrix(reactants, products)
    vec = _integer_nullspace(A)
    # ensure positive and simplify by gcd
    from math import gcd
    g = 0
    for v in vec:
        g = gcd(g, abs(v))
    vec = [v//g if g else v for v in vec]
    if any(v == 0 for v in vec):
        # avoid zeros: set minimum 1 for free vars if degenerate
        vec = [v if v != 0 else 1 for v in vec]
    return vec, reactants, products

def format_balanced(coeffs, reactants, products) -> str:
    def fmt(side, coefs):
        parts = []
        for c, f in zip(coefs, side):
            parts.append(f"{c} {f}" if c != 1 else f)
        return ' + '.join(parts)
    left = fmt(reactants, coeffs[:len(reactants)])
    right = fmt(products, coeffs[len(reactants):])
    return f"{left} -> {right}"

# -------- Temperature helpers --------
import re as _re
def parse_temperature(text: str):
    t = text.strip().lower()
    m = _re.match(r'^([-+]?\d*\.?\d+)\s*([cfk]?)$', t)
    if not m:
        raise ValueError("Invalid temperature format")
    val, unit = m.groups()
    val = float(val)
    unit = unit or 'c'
    return val, unit

def to_kelvin(value: float, unit: str) -> float:
    u = unit.lower()
    if u == 'c':
        return value + 273.15
    if u == 'f':
        return (value - 32) * 5/9 + 273.15
    if u == 'k':
        return value
    raise ValueError("Unknown temperature unit")


PROPERTY_METADATA = {
    "AtomicNumber": {"label": "Atomic Number", "unit": "", "category": "Atomic", "desc": "Number of protons", "numeric": True},
    "AtomicMass": {"label": "Atomic Mass", "unit": "u", "category": "Atomic", "desc": "Average atomic mass (u)", "numeric": True},
    "Electronegativity": {"label": "Electronegativity", "unit": "", "category": "Chemical", "desc": "Pauling electronegativity", "numeric": True},
    "BoilingPoint": {"label": "Boiling Point", "unit": "K", "category": "Physical", "desc": "Boiling point (K)", "numeric": True},
    "MeltingPoint": {"label": "Melting Point", "unit": "K", "category": "Physical", "desc": "Melting point (K)", "numeric": True},
    "Density": {"label": "Density", "unit": "g/cm³", "category": "Physical", "desc": "Density (near RT)", "numeric": True},
    "Type": {"label": "Type", "unit": "", "category": "Chemical", "desc": "Element category/type", "numeric": False},
    "OxidationStates": {"label": "Oxidation States", "unit": "", "category": "Chemical", "desc": "Common oxidation states", "numeric": False},
}
CATEGORIES = sorted(set(p["category"] for p in PROPERTY_METADATA.values()))



# ---- Property aliases and colours ----
_PROP_KEYS = {
    "Atomic number": ["number", "AtomicNumber"],
    "Group": ["group", "Group"],
    "Period": ["period", "Period"],
    "Atomic mass (u)": ["atomic_mass", "AtomicMass"],
    "Density (g/cm³)": ["density", "Density"],
    "Melting point (K)": ["melt", "MeltingPoint"],
    "Boiling point (K)": ["boil", "BoilingPoint"],
    "Electronegativity (Pauling)": ["electronegativity_pauling", "Electronegativity"],
    "Electron affinity (kJ/mol)": ["electron_affinity", "ElectronAffinity"],
    "First ionisation (eV)": ["first_ionization", "FirstIonization"],
    "Molar heat (J/mol·K)": ["molar_heat", "SpecificHeat"],
}

_COLOUR_BY_CATEGORY = {
    "alkali metal": "#FF6666",
    "alkaline earth metal": "#FFDEAD",
    "transition metal": "#FFB347",
    "post-transition metal": "#FFD700",
    "metalloid": "#ADFF2F",
    "polyatomic nonmetal": "#90EE90",
    "diatomic nonmetal": "#98FB98",
    "nonmetal": "#90EE90",
    "halogen": "#87CEFA",
    "noble gas": "#D8BFD8",
    "lanthanide": "#FF69B4",
    "actinide": "#BA55D3",
}

R = 8.31446261815324  # Gas Constant
F = 96485.33212  # Faraday's Constant
