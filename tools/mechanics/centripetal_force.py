from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Centripetal Force Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Mass m (kg):")); self.m = QLineEdit("1"); r1.addWidget(self.m)
        r1.addWidget(QLabel("Velocity v (m/s):")); self.v = QLineEdit("2"); r1.addWidget(self.v)
        r1.addWidget(QLabel("Radius r (m):")); self.r = QLineEdit("1"); r1.addWidget(self.r)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            m = float(self.m.text()); v = float(self.v.text()); r = float(self.r.text())
            if m <= 0 or r <= 0: raise ValueError("m>0, r>0")
            F = m*v*v/r
            self.result.setText(f"F_c = {F:.6g} N")
            add_log_entry(self.TITLE, action="Compute", data={"m": m, "v": v, "r": r, "Fc": F})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
