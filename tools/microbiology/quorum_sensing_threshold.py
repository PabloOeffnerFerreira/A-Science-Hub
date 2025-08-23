from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Quorum Sensing Threshold (Hill function)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Signal conc. A (arb.):")); self.A = QLineEdit("1.0"); r1.addWidget(self.A)
        r1.addWidget(QLabel("K (threshold):")); self.K = QLineEdit("1.0"); r1.addWidget(self.K)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("n (Hill coeff):")); self.n = QLineEdit("2"); r2.addWidget(self.n)
        r2.addWidget(QLabel("Max response:")); self.Rmax = QLineEdit("1.0"); r2.addWidget(self.Rmax)
        lay.addLayout(r2)

        self.result = QLabel("Educational model only."); lay.addWidget(self.result)
        btn = QPushButton("Compute response"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            A = float(self.A.text()); K = float(self.K.text()); n = float(self.n.text()); Rmax = float(self.Rmax.text())
            if A < 0 or K <= 0 or n <= 0 or Rmax < 0: raise ValueError("Invalid inputs")
            resp = Rmax * (A**n) / (K**n + A**n)
            self.result.setText(f"Response ≈ {resp:.6g} (0..{Rmax})")
            add_log_entry(self.TITLE, action="Compute", data={"A": A, "K": K, "n": n, "Rmax": Rmax, "response": resp})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
