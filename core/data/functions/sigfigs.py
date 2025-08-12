from decimal import Decimal, getcontext, ROUND_HALF_UP

def normalize_numeric_string(s: str) -> str:
    return (s or "").strip().replace("+", "")

def count_sigfigs(s: str) -> int:
    t = normalize_numeric_string(s)
    if not t:
        return 0
    if "e" in t or "E" in t:
        t = t.split("e")[0].split("E")[0]
    if t.startswith("-"):
        t = t[1:]
    if t.startswith("."):
        t = "0" + t
    if "." in t:
        left, right = t.split(".", 1)
        left = left.lstrip("0")
        digits = (left + right).lstrip("0")
        return len(digits)
    t = t.lstrip("0")
    if not t:
        return 0
    t = t.rstrip("0")
    return len(t)

def round_sigfigs(s: str, n: int) -> str:
    try:
        d = Decimal(normalize_numeric_string(s))
    except Exception:
        return ""
    if d == 0:
        return "0"
    getcontext().rounding = ROUND_HALF_UP
    return format(d, f".{n}g")