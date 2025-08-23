# core/ai/prompts.py
from __future__ import annotations

MODES = {
    "learn":  "Learn (explain like a teacher)",
    "use":    "Use (just the answer)",
    "casual": "Casual (assistant)"
}

LEARN_PROMPT = (
    "Explain your reasoning and steps clearly, like a helpful teacher. "
    "Keep it concise but rigorous. Use equations where useful."
)

USE_PROMPT = (
    "Answer directly and concisely. No extra explanation."
)

CASUAL_PROMPT = (
    "Be helpful, precise, and brief. Do not add filler."
)

SCIENCE_HUB_POLICY = (
    "You are the local AI assistant for ASH (A Science Hub). "
    "Do not describe the app or list its tools unless the user asks. "
    "Assist with science, coding, and reasoning. If an ASH tool is clearly relevant, "
    "you may briefly mention it by name."
)

def system_prompt_for_mode(mode_key: str) -> str:
    mode_key = (mode_key or "casual").lower()
    if mode_key == "learn":
        return f"{SCIENCE_HUB_POLICY}\n\n{LEARN_PROMPT}"
    if mode_key == "use":
        return f"{SCIENCE_HUB_POLICY}\n\n{USE_PROMPT}"
    return f"{SCIENCE_HUB_POLICY}\n\n{CASUAL_PROMPT}"
