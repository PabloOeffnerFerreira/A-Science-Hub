# Todo: This is a simple algebraic calculator tool that evaluates a function at a given value of x.
# It will be improved later to handle more complex expressions and provide better error handling.

from __future__ import annotations
import sympy as sp
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Algebraic Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(480)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Enter function of x (e.g., x**2 + 3*x - 2):"))
        self.func_input = QLineEdit(); lay.addWidget(self.func_input)
        lay.addWidget(QLabel("Enter the value of x:"))
        self.x_input = QLineEdit(); lay.addWidget(self.x_input)
        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Calculate"); lay.addWidget(btn)
        btn.clicked.connect(self._calculate)

    def _calculate(self):
        ftxt = self.func_input.text().strip()
        xtxt = self.x_input.text().strip()
        try:
            expr = sp.sympify(ftxt)
            x = sp.Symbol('x')
            val = float(xtxt)
            res = expr.subs(x, val).evalf()
            msg = f"f({val}) = {res}"
            self.result.setText(msg)
            add_log_entry(self.TITLE, action="Calculate", data={"expr": ftxt, "x": val, "result": str(res)})
        except Exception as e:
            msg = "Error with the function or x."
            self.result.setText(msg)
            add_log_entry(self.TITLE, action="Error", data={"expr": ftxt, "x": xtxt, "msg": str(e)})
