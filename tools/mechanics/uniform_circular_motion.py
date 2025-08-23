from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Uniform Circular Motion"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Radius r (m):")); self.r = QLineEdit("1.0"); r1.addWidget(self.r)
        r1.addWidget(QLabel("Period T (s):")); self.T = QLineEdit("2.0"); r1.addWidget(self.T)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            r = float(self.r.text()); T = float(self.T.text())
            if r <= 0 or T <= 0: raise ValueError("r>0, T>0")
            v = 2*math.pi*r / T
            a_c = v*v / r
            omega = 2*math.pi / T
            self.result.setText(f"v = {v:.6g} m/s, a_c = {a_c:.6g} m/s², ω = {omega:.6g} rad/s")
            add_log_entry(self.TITLE, action="Compute", data={"r": r, "T": T, "v": v, "a_c": a_c, "omega": omega})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
