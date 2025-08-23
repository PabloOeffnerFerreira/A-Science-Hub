from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

R = 8.314462618  # J/(mol·K)

class Tool(QDialog):
    TITLE = "Reaction Rate (Arrhenius)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("A (s⁻¹ or units of k):")); self.A = QLineEdit("1e7"); r1.addWidget(self.A)
        r1.addWidget(QLabel("Ea (kJ/mol):")); self.Ea = QLineEdit("50"); r1.addWidget(self.Ea)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Temperature T (K):")); self.T = QLineEdit("298"); r2.addWidget(self.T)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute k"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            A = float(self.A.text()); Ea_kJ = float(self.Ea.text()); T = float(self.T.text())
            if T <= 0 or A <= 0 or Ea_kJ < 0: raise ValueError("invalid inputs")
            Ea = Ea_kJ * 1e3
            k = A * math.exp(-Ea/(R*T))
            self.result.setText(f"k ≈ {k:.6g} (units depend on reaction order)")
            add_log_entry(self.TITLE, action="Compute", data={"A": A, "Ea_kJmol": Ea_kJ, "T": T, "k": k})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
