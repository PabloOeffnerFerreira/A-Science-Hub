from core.data.databases.constants_data import constants_data

def categories():
    return list(constants_data.keys())

def all_items():
    for cat, items in constants_data.items():
        for name, meta in items.items():
            yield {
                "category": cat,
                "name": name,
                "value": meta.get("value"),
                "unit": meta.get("unit"),
                "description": meta.get("description"),
                "exact": bool(meta.get("exact"))
            }

def items_by_category(category: str):
    d = constants_data.get(category, {})
    return [
        {
            "category": category,
            "name": name,
            "value": meta.get("value"),
            "unit": meta.get("unit"),
            "description": meta.get("description"),
            "exact": bool(meta.get("exact"))
        }
        for name, meta in d.items()
    ]

def find_by_name(query: str):
    if not query:
        return []
    q = query.strip().lower()
    out = []
    for rec in all_items():
        if q in rec["name"].lower():
            out.append(rec)
    return out

def get_constant(category: str, name: str):
    meta = constants_data.get(category, {}).get(name)
    if not meta:
        return None
    return {
        "category": category,
        "name": name,
        "value": meta.get("value"),
        "unit": meta.get("unit"),
        "description": meta.get("description"),
        "exact": bool(meta.get("exact"))
    }
