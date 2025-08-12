from core.data.functions import units

def convert_value(category, from_unit, from_prefix, to_unit, to_prefix, value):
    """Converts a value using category/unit/prefix selections.
    Returns: (converted_value, formatted_string) or (None, None) on error.
    """
    v = units.parse_number(value)
    if v is None:
        return None, None

    if units.supports_si(category, from_unit):
        v = units.apply_prefix(v, from_prefix)

    try:
        base_out = units.convert(v, from_unit, to_unit, category)
    except Exception:
        return None, None

    if units.supports_si(category, to_unit):
        base_out = base_out / units.apply_prefix(1.0, to_prefix)

    formatted = f"{value} {units.compose_label(from_prefix, from_unit)} = {base_out:.6g} {units.compose_label(to_prefix, to_unit)}"
    return base_out, formatted
