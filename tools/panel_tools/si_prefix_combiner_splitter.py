from core.data.functions import si_prefix_tools

def combine_split(value, in_prefix, in_unit, out_prefix):
    out_val, base_val = si_prefix_tools.compute_combined_and_base(value, in_prefix, in_unit, out_prefix)
    if out_val is None:
        return None, None
    return (
        f"{out_val:.12g}",
        f"{base_val:.12g} {in_unit}"
    )
