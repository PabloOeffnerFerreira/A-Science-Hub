from core.utils.num_format import convert_both

def convert(value: str, digits: int | None):
    return convert_both(value, digits=digits)
