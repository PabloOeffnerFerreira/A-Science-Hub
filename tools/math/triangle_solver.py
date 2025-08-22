#Todo: I will add a more advanced triangle solver later, this is just a simple Pythagorean theorem solver.
# It will have a coordinate system and allow to calculate angles, area, etc.
# The whole thing will be a bit more complex, but I think it will be worth it.

from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Triangle Side Solver (Pythagorean)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(380)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Leave the unknown side blank. a² + b² = c²"))

        self.a = QLineEdit(); self.b = QLineEdit(); self.c = QLineEdit()
        for w, txt in ((self.a, "a:"), (self.b, "b:"), (self.c, "c (hypotenuse):")):
            row = QHBoxLayout(); row.addWidget(QLabel(txt)); row.addWidget(w); lay.addLayout(row)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Solve"); lay.addWidget(btn)
        btn.clicked.connect(self._solve)

    def _solve(self):
        A = self.a.text().strip(); B = self.b.text().strip(); C = self.c.text().strip()
        try:
            if C == "":
                value = (float(A)**2 + float(B)**2) ** 0.5
                msg = f"c = {value:.6g}"
            elif A == "":
                value = (float(C)**2 - float(B)**2) ** 0.5
                msg = f"a = {value:.6g}"
            elif B == "":
                value = (float(C)**2 - float(A)**2) ** 0.5
                msg = f"b = {value:.6g}"
            else:
                msg = "Leave exactly one field blank."
            self.result.setText(msg)
            add_log_entry(self.TITLE, action="Solve", data={"a": A, "b": B, "c": C, "msg": msg})
        except Exception:
            msg = "Invalid input."
            self.result.setText(msg)
            add_log_entry(self.TITLE, action="Error", data={"a": A, "b": B, "c": C, "msg": msg})
