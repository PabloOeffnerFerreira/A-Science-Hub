import os, sys, platform, time, shutil
from datetime import datetime, timezone
try:
    import winreg
except:
    winreg = None
try:
    import psutil
except:
    psutil = None

def _uptime_seconds():
    if psutil and hasattr(psutil, "boot_time"):
        return int(time.time() - psutil.boot_time())
    return None

def _total_memory_bytes():
    if psutil and hasattr(psutil, "virtual_memory"):
        return int(psutil.virtual_memory().total)
    return None

def _cpu_load_percent():
    if psutil and hasattr(psutil, "cpu_percent"):
        return float(psutil.cpu_percent(interval=0.0))
    return None

def _disk_total_free_bytes(path):
    d = shutil.disk_usage(path)
    return int(d.total), int(d.free)

def _process_memory_bytes():
    if psutil and hasattr(psutil, "Process"):
        try:
            return int(psutil.Process(os.getpid()).memory_info().rss)
        except:
            return None
    return None

def human_bytes(n):
    if n is None:
        return "N/A"
    u = ["B","KB","MB","GB","TB","PB"]
    i = 0
    f = float(n)
    while f >= 1024 and i < len(u)-1:
        f /= 1024.0
        i += 1
    s = f"{f:.2f}".rstrip("0").rstrip(".")
    return f"{s} {u[i]}"

def human_duration(sec):
    if sec is None:
        return "N/A"
    sec = int(sec)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d: parts.append(f"{d}d")
    if d or h: parts.append(f"{h}h")
    if d or h or m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)

def _windows_name():
    if winreg is None:
        return f"{platform.system()} {platform.release()}"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as k:
            product = winreg.QueryValueEx(k, "ProductName")[0]
            display = None
            try:
                display = winreg.QueryValueEx(k, "DisplayVersion")[0]
            except FileNotFoundError:
                pass
            build = winreg.QueryValueEx(k, "CurrentBuildNumber")[0]
            edition = winreg.QueryValueEx(k, "EditionID")[0]
        name = product
        if display:
            name += f" {display}"
        return f"{name} (build {build}, {edition})"
    except:
        build = getattr(sys.getwindowsversion(), "build", None)
        rel = platform.release()
        if build and int(build) >= 22000:
            rel = "11"
        return f"Windows {rel} (build {build})"

def _os_string():
    if platform.system() == "Windows":
        return _windows_name()
    return f"{platform.system()} {platform.release()}"

def get_system_snapshot():
    total_disk, free_disk = _disk_total_free_bytes(os.getcwd())
    return {
        "os": _os_string(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor() or platform.machine(),
        "cpu_count": os.cpu_count() or 1,
        "cpu_load_percent": _cpu_load_percent(),
        "ram_total_bytes": _total_memory_bytes(),
        "disk_total_bytes": total_disk,
        "disk_free_bytes": free_disk,
        "uptime_seconds": _uptime_seconds(),
        "uptime_human": human_duration(_uptime_seconds()),
        "process_mem_bytes": _process_memory_bytes(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }
