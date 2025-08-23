from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

G = 6.67430e-11  # m^3 kg^-1 s^-2

class Tool(QDialog):
    TITLE = "Kepler's 3rd Law (Orbital Period)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(700)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Semi-major axis a (m):")); self.a = QLineEdit("1.496e11"); r1.addWidget(self.a)
        r1.addWidget(QLabel("Central mass M (kg):")); self.M = QLineEdit("1.989e30"); r1.addWidget(self.M)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute Period"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            a = float(self.a.text()); M = float(self.M.text())
            if a <= 0 or M <= 0: raise ValueError("a>0, M>0")
            T = 2*math.pi*math.sqrt(a**3/(G*M))
            self.result.setText(f"T ≈ {T:.6g} s  (≈ {T/86400:.6g} days)")
            add_log_entry(self.TITLE, action="Compute", data={"a": a, "M": M, "T_s": T, "T_days": T/86400})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
