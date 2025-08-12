import json
from functools import lru_cache
from core.data.paths import QUANTITIES_JSON_PATH

REGIONS = ["EU", "UK/US", "BR"]

@lru_cache(maxsize=1)
def _load():
    with open(QUANTITIES_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@lru_cache(maxsize=8)
def _indexes(region: str):
    data = _load()
    by_q = {}
    by_qsym = {}
    by_usym = {}
    for item in data:
        qname = item["names"]["en"]
        usym = item["unit_symbol"]
        qsym = item["regions"][region]["Q"]
        by_q[qname] = item
        by_qsym[qsym] = item
        by_usym[usym] = item
    return by_q, by_qsym, by_usym

def selector_items(region: str, mode: str):
    by_q, by_qsym, by_usym = _indexes(region)
    if mode == "Quantity":
        return sorted(by_q.keys())
    if mode == "Q Symbol":
        return sorted(by_qsym.keys(), key=lambda s: (len(s), s))
    return sorted(by_usym.keys(), key=lambda s: (len(s), s))

def lookup(region: str, mode: str, key: str):
    by_q, by_qsym, by_usym = _indexes(region)
    if mode == "Quantity":
        return by_q.get(key)
    if mode == "Q Symbol":
        return by_qsym.get(key)
    return by_usym.get(key)
