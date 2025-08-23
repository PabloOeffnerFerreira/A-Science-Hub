from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Transmission Line (Z0, v)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(700)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("L' (H/m):")); self.Lp = QLineEdit("2e-7"); r1.addWidget(self.Lp)
        r1.addWidget(QLabel("C' (F/m):")); self.Cp = QLineEdit("8e-11"); r1.addWidget(self.Cp)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute Z0 & v"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            Lp = float(self.Lp.text()); Cp = float(self.Cp.text())
            if Lp <= 0 or Cp <= 0: raise ValueError("L', C' > 0")
            Z0 = math.sqrt(Lp/Cp)
            v = 1.0/math.sqrt(Lp*Cp)
            self.result.setText(f"Z0 ≈ {Z0:.6g} Ω,  v ≈ {v:.6g} m/s")
            add_log_entry(self.TITLE, action="Compute", data={"L_prime": Lp, "C_prime": Cp, "Z0": Z0, "v": v})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
