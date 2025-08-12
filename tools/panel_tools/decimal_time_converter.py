from core.data.functions import time_tools

def to_decimal(hours: str, minutes: str, seconds: str) -> str | None:
    try:
        h = float((hours or "0").replace(",", "."))
        m = float((minutes or "0").replace(",", "."))
        s = float((seconds or "0").replace(",", "."))
    except ValueError:
        return None
    return f"{time_tools.hms_to_hours(h, m, s):.8f}"

def from_decimal(dec_hours: str) -> tuple[str, str, str] | None:
    try:
        x = float((dec_hours or "0").replace(",", "."))
    except ValueError:
        return None
    h, m, s = time_tools.hours_to_hms(x)
    return str(h), str(m), f"{s:.2f}"
