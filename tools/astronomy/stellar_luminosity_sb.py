from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

sigma = 5.670374419e-8  # W m^-2 K^-4

class Tool(QDialog):
    TITLE = "Stellar Luminosity (Stefan–Boltzmann)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(680)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Radius R (m):")); self.R = QLineEdit("6.96e8"); r1.addWidget(self.R)
        r1.addWidget(QLabel("Temperature T (K):")); self.T = QLineEdit("5778"); r1.addWidget(self.T)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute L"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            R = float(self.R.text()); T = float(self.T.text())
            if R <= 0 or T <= 0: raise ValueError("R>0, T>0")
            L = 4*math.pi*R*R*sigma*T**4
            self.result.setText(f"L ≈ {L:.6g} W")
            add_log_entry(self.TITLE, action="Compute", data={"R": R, "T": T, "L": L})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
