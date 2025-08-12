from decimal import Decimal, InvalidOperation
from core.data.functions.sigfigs import normalize_numeric_string

def parse_number(s: str):
    t = normalize_numeric_string(s).replace(",", ".")
    try:
        return Decimal(t)
    except InvalidOperation:
        return None

def to_scientific(d: Decimal, digits: int | None = None):
    if d.is_zero():
        return "0" if not digits else f"{d:.{digits}E}"
    if digits is None:
        return f"{d.normalize():.6E}"
    return f"{d:.{digits}E}"

def to_decimal_str(d: Decimal, max_places: int = 12):
    q = Decimal(1).scaleb(-max_places)
    s = str(d.quantize(q).normalize())
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s

def convert_both(s: str, digits: int | None = None, max_places: int = 12):
    d = parse_number(s)
    if d is None:
        return None, None
    sci = to_scientific(d, digits)
    dec = to_decimal_str(d, max_places)
    return dec, sci
