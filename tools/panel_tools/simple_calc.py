# tools/panel_tools/simple_calc.py

import ast
import math

class SafeEvaluator:
    """Safe evaluator supporting variables, scientific notation, and math funcs"""
    def __init__(self):
        self.vars = {}
        self.env = {
            "pi": math.pi, "π": math.pi, "e": math.e, "tau": math.tau,
            "inf": math.inf, "nan": math.nan,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "asin": math.asin, "acos": math.acos, "atan": math.atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "ln": math.log, "log": lambda x, b=10: math.log(x, b),
            "log2": math.log2, "log10": math.log10,
            "sqrt": math.sqrt, "exp": math.exp, "abs": abs,
            "floor": math.floor, "ceil": math.ceil,
            "deg": math.degrees, "rad": math.radians,
            "In": math.log,
        }

    def evaluate(self, text: str):
        """Evaluate expression or assignment; return None for incomplete input"""
        s = (text or "").strip()
        if not s:
            return None
        s = self._normalize(s)
        try:
            if "=" in s and self._is_top_level_assign(s):
                name, expr = s.split("=", 1)
                name = name.strip()
                val = self._eval_expr(expr.strip())
                if val is None or callable(val):
                    return None
                self.vars[name] = val
                return val
        except SyntaxError:
            return None
        try:
            val = self._eval_expr(s)
        except SyntaxError:
            return None
        if callable(val):
            return None
        return val

    def get_variables(self):
        """Return saved variables"""
        return dict(self.vars)

    def set_variable(self, name: str, value: float):
        """Set variable"""
        self.vars[name] = float(value)

    def delete_variable(self, name: str):
        """Delete variable"""
        if name in self.vars:
            del self.vars[name]

    def reset_variables(self):
        """Reset all variables"""
        self.vars.clear()

    def _normalize(self, s: str) -> str:
        """Normalize tokens"""
        t = s.replace("^", "**").replace("×", "*").replace("·", "*").replace("÷", "/").replace("−", "-")
        t = t.replace("sin-1(", "asin(").replace("cos-1(", "acos(").replace("tan-1(", "atan(")
        t = t.replace("SIN-1(", "asin(").replace("COS-1(", "acos(").replace("TAN-1(", "atan(")
        return t

    def _is_top_level_assign(self, s: str) -> bool:
        """Detect single top-level assignment"""
        tree = ast.parse(s, mode="exec")
        return len(tree.body) == 1 and isinstance(tree.body[0], ast.Assign) and len(tree.body[0].targets) == 1

    def _eval_expr(self, s: str):
        """Evaluate expression with AST whitelist"""
        node = ast.parse(s, mode="eval")
        return self._eval_node(node.body)

    def _eval_node(self, node):
        """Recursively evaluate allowed AST nodes"""
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self.vars:
                return self.vars[node.id]
            if node.id in self.env:
                return self.env[node.id]
            raise NameError(f"Unknown name: {node.id}")
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left); right = self._eval_node(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div): return left / right
            if isinstance(node.op, ast.FloorDiv): return left // right
            if isinstance(node.op, ast.Mod): return left % right
            if isinstance(node.op, ast.Pow): return left ** right
            raise ValueError("Operator not allowed")
        if isinstance(node, ast.UnaryOp):
            val = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd): return +val
            if isinstance(node.op, ast.USub): return -val
            raise ValueError("Unary operator not allowed")
        if isinstance(node, ast.Call):
            func = self._eval_node(node.func)
            args = [self._eval_node(a) for a in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords}
            return func(*args, **kwargs)
        if isinstance(node, ast.Expr):
            return self._eval_node(node.value)
        raise ValueError("Expression not allowed")
