from __future__ import annotations
import subprocess, json, shlex

def list_ollama_models() -> list[str]:
    """Return installed model names. Falls back to parsing plain text when --json unsupported."""
    # Try JSON first
    try:
        out = subprocess.check_output(["ollama", "list", "--json"], text=True, stderr=subprocess.STDOUT)
        names = []
        for line in out.splitlines():
            try:
                j = json.loads(line)
                if "name" in j:
                    names.append(j["name"])
            except Exception:
                continue
        if names:
            return names
    except Exception:
        pass

    # Fallback: plain text parsing (columns: NAME  SIZE  MODIFIED)
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, stderr=subprocess.STDOUT)
    except Exception:
        return []

    names: list[str] = []
    for i, line in enumerate(out.splitlines()):
        line = line.strip()
        if not line:
            continue
        # Skip header if present
        if i == 0 and ("NAME" in line and "SIZE" in line):
            continue
        # The name is the first whitespace-separated token; allow spaces via split once
        # But ‘ollama list’ aligns columns, so split() is fine.
        parts = line.split()
        if not parts:
            continue
        # Some outputs show `model:tag` in the first column; use it verbatim.
        names.append(parts[0])
    return names

def pull_model_blocking(model: str) -> tuple[bool, str]:
    try:
        p = subprocess.run(["ollama", "pull", model], text=True, capture_output=True)
        ok = p.returncode == 0
        return ok, (p.stdout if ok else (p.stderr or "pull failed"))
    except Exception as e:
        return False, str(e)

def model_tooltip_map() -> dict[str, str]:
    return {
    "qwen2:7b":       "Balanced speed/quality. Fits mid-range GPUs (≈8–10 GB VRAM). Good default choice.",
    "mistral:7b":     "Fast, fluent generalist. Low latency. ≈4–6 GB VRAM.",
    "gemma2:9b":      "Larger, more accurate. Needs ≈12 GB VRAM. Good knowledge coverage.",
    "phi4:14b":       "Reasoning-focused. Slower, heavier (≈14–16 GB VRAM).",
    "mathstral:7b":   "Math- and formula-focused. Similar footprint to mistral:7b.",
    "deepseek-r1:7b": "Reasoning-oriented 7B. Efficient, small VRAM requirement.",
    
    "dolphin3:8b":    "≈4.9 GB. Balanced model tuned for science/coding. Good mix of speed & quality.",
    "qwen3:14b":      "≈9.3 GB. Larger, deeper reasoning than 7B. Slower, needs ≥14 GB VRAM.",
    "gemma3:4b":      "≈3.3 GB. Lightweight, very fast. Fits low-VRAM GPUs. Weaker on complex tasks.",
    "gemma3:latest":  "Alias for gemma3:4b (≈3.3 GB). Always points to latest 4B release."
}


import subprocess, json

def list_ollama_models() -> list[str]:
    # Try JSON first (short timeout)
    try:
        out = subprocess.check_output(
            ["ollama", "list", "--json"],
            text=True, stderr=subprocess.STDOUT, timeout=2.5
        )
        names = []
        for line in out.splitlines():
            try:
                j = json.loads(line)
                if "name" in j:
                    names.append(j["name"])
            except Exception:
                continue
        if names:
            return names
    except Exception:
        pass

    # Fallback: plain text (also short timeout)
    try:
        out = subprocess.check_output(
            ["ollama", "list"],
            text=True, stderr=subprocess.STDOUT, timeout=2.0
        )
    except Exception:
        return []

    names = []
    for i, line in enumerate(out.splitlines()):
        line = line.strip()
        if not line:
            continue
        if i == 0 and ("NAME" in line and "SIZE" in line):
            continue
        parts = line.split()
        if parts:
            names.append(parts[0])
    return names
