import math

class SafeEvaluator:
    def __init__(self):
        self.vars = {}
        self.allowed_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
        self.allowed_names.update({"pi": math.pi, "e": math.e, "ans": None})

    def evaluate(self, expr: str):
        if not expr.strip():
            return None
        try:
            if "=" in expr:
                name, val = expr.split("=", 1)
                name = name.strip()
                val = val.strip()
                result = eval(val, {"__builtins__": {}}, {**self.allowed_names, **self.vars})
                self.set_variable(name, result)
                self.allowed_names["ans"] = result
                return result
            else:
                result = eval(expr, {"__builtins__": {}}, {**self.allowed_names, **self.vars})
                self.allowed_names["ans"] = result
                return result
        except Exception:
            return None

    def get_variables(self):
        return self.vars

    def set_variable(self, name: str, value):
        self.vars[name] = value

    def delete_variable(self, name: str):
        if name in self.vars:
            del self.vars[name]

    def reset_variables(self):
        self.vars.clear()
