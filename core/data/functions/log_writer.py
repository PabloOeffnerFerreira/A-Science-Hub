import os, json, time

def write_log(out_dir, payload):
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"log_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path

def read_logs(out_dir):
    """Load all JSON logs in newest-first order."""
    if not os.path.exists(out_dir):
        return []
    logs = []
    for file in os.listdir(out_dir):
        if file.endswith(".json"):
            with open(os.path.join(out_dir, file), "r", encoding="utf-8") as f:
                try:
                    logs.append(json.load(f))
                except json.JSONDecodeError:
                    pass
    return sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)