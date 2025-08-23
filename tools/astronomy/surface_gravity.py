from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

G = 6.67430e-11

class Tool(QDialog):
    TITLE = "Surface Gravity (g = GM/R²)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Mass M (kg):")); self.M = QLineEdit("5.972e24"); r1.addWidget(self.M)
        r1.addWidget(QLabel("Radius R (m):")); self.R = QLineEdit("6.371e6"); r1.addWidget(self.R)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute g"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            M = float(self.M.text()); R = float(self.R.text())
            if M <= 0 or R <= 0: raise ValueError("M>0, R>0")
            g = G*M/(R*R)
            self.result.setText(f"g ≈ {g:.6g} m/s²")
            add_log_entry(self.TITLE, action="Compute", data={"M": M, "R": R, "g": g})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
