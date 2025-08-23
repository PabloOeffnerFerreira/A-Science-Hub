from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Buffer pH (Henderson–Hasselbalch)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("pKa:")); self.pKa = QLineEdit("4.76"); r1.addWidget(self.pKa)
        r1.addWidget(QLabel("[A-] (M):")); self.Am = QLineEdit("0.1"); r1.addWidget(self.Am)
        r1.addWidget(QLabel("[HA] (M):")); self.HA = QLineEdit("0.1"); r1.addWidget(self.HA)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute pH"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            pKa = float(self.pKa.text()); A = float(self.Am.text()); HA = float(self.HA.text())
            if A <= 0 or HA <= 0: raise ValueError("[A-], [HA] > 0")
            pH = pKa + math.log10(A/HA)
            self.result.setText(f"pH ≈ {pH:.4f}")
            add_log_entry(self.TITLE, action="Compute", data={"pKa": pKa, "A-": A, "HA": HA, "pH": pH})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
