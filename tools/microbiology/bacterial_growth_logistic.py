from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Bacterial Growth (Logistic Model)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Initial N0:")); self.N0 = QLineEdit("1e6"); r1.addWidget(self.N0)
        r1.addWidget(QLabel("Carrying cap. K:")); self.K = QLineEdit("1e9"); r1.addWidget(self.K)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Growth rate r (1/h):")); self.r = QLineEdit("0.8"); r2.addWidget(self.r)
        r2.addWidget(QLabel("Time t (h):")); self.t = QLineEdit("5"); r2.addWidget(self.t)
        lay.addLayout(r2)

        self.result = QLabel("Educational model only."); lay.addWidget(self.result)
        btn = QPushButton("Compute N(t)"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            N0 = float(self.N0.text()); K = float(self.K.text()); r = float(self.r.text()); t = float(self.t.text())
            if N0 <= 0 or K <= 0 or r < 0 or t < 0: raise ValueError("Invalid inputs")
            Nt = (K * N0 * math.exp(r*t)) / (K + N0*(math.exp(r*t)-1))
            self.result.setText(f"N(t) ≈ {Nt:.6g}")
            add_log_entry(self.TITLE, action="Compute", data={"N0": N0, "K": K, "r": r, "t": t, "Nt": Nt})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
