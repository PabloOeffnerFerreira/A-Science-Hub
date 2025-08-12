from core.data.functions.quantities import REGIONS, selector_items, lookup

def regions():
    return REGIONS

def options_for(region: str, mode: str):
    return selector_items(region, mode)

def describe(region: str, mode: str, key: str):
    item = lookup(region, mode, key)
    if not item:
        return None
    qname = item["names"]["en"]
    qsym = item["regions"][region]["Q"]
    return {
        "q_name": qname,
        "q_sym": qsym,
        "u_name": item["unit_name"],
        "u_sym": item["unit_symbol"]
    }
