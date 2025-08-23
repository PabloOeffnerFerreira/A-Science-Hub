
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

K = 8.9875517923e9  # 1/(4*pi*epsilon0)

class Tool(QDialog):
    TITLE = "Coulomb Force Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("q1 (C):")); self.q1 = QLineEdit("1e-6"); r1.addWidget(self.q1)
        r1.addWidget(QLabel("q2 (C):")); self.q2 = QLineEdit("-2e-6"); r1.addWidget(self.q2)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Distance r (m):")); self.r = QLineEdit("0.05"); r2.addWidget(self.r)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            q1 = float(self.q1.text()); q2 = float(self.q2.text()); r = float(self.r.text())
            if r <= 0: raise ValueError("r>0")
            F = K * abs(q1*q2) / (r*r)
            nature = "repulsive" if q1*q2 > 0 else "attractive"
            self.result.setText(f"|F| = {F:.6g} N ({nature})")
            add_log_entry(self.TITLE, action="Compute", data={"q1": q1, "q2": q2, "r": r, "F": F, "nature": nature})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
