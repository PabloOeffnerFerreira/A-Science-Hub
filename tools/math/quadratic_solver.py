#Todo: I will add a more advanced quadratic solver later, this is just a simple one.
# It will handle complex numbers and provide a more detailed output.
# Even though its more complex, it will hopefully add value to the tool.

from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
import sympy as sp
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Quadratic Solver"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(360)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("ax² + bx + c = 0"))

        self.a = QLineEdit(); self.b = QLineEdit(); self.c = QLineEdit()
        for w, txt in ((self.a, "a:"), (self.b, "b:"), (self.c, "c:")):
            row = QHBoxLayout(); row.addWidget(QLabel(txt)); row.addWidget(w); lay.addLayout(row)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Solve"); lay.addWidget(btn)
        btn.clicked.connect(self._solve)

    def _solve(self):
        try:
            A = float(self.a.text()); B = float(self.b.text()); C = float(self.c.text())
            x = sp.symbols('x')
            poly = A*x**2 + B*x + C
            sol = sp.solve(poly, x)
            self.result.setText(f"Solutions: {sol}")
            add_log_entry(self.TITLE, action="Solve", data={"a": A, "b": B, "c": C, "solutions": [str(s) for s in sol]})
        except Exception:
            msg = "Invalid input."
            self.result.setText(msg)
            add_log_entry(self.TITLE, action="Error", data={"a": self.a.text(), "b": self.b.text(), "c": self.c.text(), "msg": msg})
