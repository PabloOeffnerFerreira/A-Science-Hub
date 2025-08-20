import importlib
from core.data.functions.tool_registry import humanize_tool_key

def create_tool_factory(category: str, key: str):
    modname = f"tools.{category}.{key}"
    mod = importlib.import_module(modname)
    cls = getattr(mod, "Tool", None)
    if cls is None:
        raise ImportError("Tool class 'Tool' not found")
    def factory():
        return cls()
    title = humanize_tool_key(key)
    return factory, title
