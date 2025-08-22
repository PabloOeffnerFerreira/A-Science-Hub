from core.utils.system_info import get_system_snapshot, human_bytes
from core.utils.app_info import get_app_snapshot
from core.utils.usage_stats import get_last_tool_opened
from datetime import datetime

def _format_session_start(s):
    if not s:
        return "N/A"
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d %b %Y, %H:%M")

    except:
        return s

def get_welcome_stats():
    sysinfo = get_system_snapshot()
    appinfo = get_app_snapshot()
    last_tool = get_last_tool_opened()
    return {
        "App": {
            "Title": appinfo["app_title"],
            "Version": appinfo["version"],
            "Build": appinfo["build"],
            "Language": appinfo["language"],
            "Region": appinfo["region"],
            "Theme": appinfo["theme"],
            "Stage": appinfo["stage"],
            "Session start": _format_session_start(appinfo["session_start"]),
            "Last tool opened": last_tool or "N/A"
        },
        "System": {
            "OS": sysinfo["os"],
            "Python": sysinfo["python"],
            "CPU count": sysinfo["cpu_count"],
            "CPU load %": f'{sysinfo["cpu_load_percent"]:.1f}%' if sysinfo["cpu_load_percent"] is not None else "N/A",
            "RAM total": human_bytes(sysinfo["ram_total_bytes"]),
            "Disk total (C:)": human_bytes(sysinfo["disk_total_bytes"]),
            "Disk free (C:)": human_bytes(sysinfo["disk_free_bytes"]),
            "Uptime": sysinfo["uptime_human"],
            "Process memory": human_bytes(sysinfo["process_mem_bytes"])
        }
    }
