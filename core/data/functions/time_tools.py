from math import floor

def hms_to_hours(h: float, m: float = 0.0, s: float = 0.0) -> float:
    return float(h) + float(m)/60.0 + float(s)/3600.0

def hours_to_hms(hours: float) -> tuple[int, int, float]:
    h = int(floor(hours))
    rem = (hours - h) * 60.0
    m = int(floor(rem))
    s = (rem - m) * 60.0
    return h, m, s

def minutes_to_hours(minutes: float) -> float:
    return float(minutes) / 60.0

def hours_to_minutes(hours: float) -> float:
    return float(hours) * 60.0

def seconds_to_hours(seconds: float) -> float:
    return float(seconds) / 3600.0

def hours_to_seconds(hours: float) -> float:
    return float(hours) * 3600.0

def parse_time_string(s: str) -> tuple[float, float, float] | None:
    t = (s or "").strip().lower().replace(",", ".")
    if not t:
        return None
    for sep in ["h", "m", "s", ":"]:
        if sep in t:
            break
    if ":" in t:
        parts = [p for p in t.split(":") if p != ""]
        if len(parts) == 1:
            return float(parts[0]), 0.0, 0.0
        if len(parts) == 2:
            return float(parts[0]), float(parts[1]), 0.0
        return float(parts[0]), float(parts[1]), float(parts[2])
    h = m = s2 = 0.0
    num = ""
    unit = ""
    acc = []
    for ch in t:
        if ch.isdigit() or ch in ".-+":
            if unit:
                acc.append((num, unit)); num = ""; unit = ""
            num += ch
        else:
            unit += ch
    if num or unit:
        acc.append((num, unit))
    for n,u in acc:
        u = u.strip()
        if not n:
            continue
        v = float(n)
        if u.startswith("h"):
            h = v
        elif u.startswith("m"):
            m = v
        elif u.startswith("s"):
            s2 = v
    return h, m, s2

def format_hms(h: int, m: int, s: float, mode: str = "compact") -> str:
    if mode == "colon":
        return f"{h:02d}:{m:02d}:{int(round(s)):02d}"
    if abs(s) < 1e-9:
        return f"{h} h {m} m"
    return f"{h} h {m} m {s:.2f} s"
