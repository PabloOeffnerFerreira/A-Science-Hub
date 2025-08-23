from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Titration Curve (Strong Acid–Strong Base)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(680)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("c_acid (mol/L):")); self.ca = QLineEdit("0.1"); r1.addWidget(self.ca)
        r1.addWidget(QLabel("V_acid (L):")); self.va = QLineEdit("0.025"); r1.addWidget(self.va)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("c_base (mol/L):")); self.cb = QLineEdit("0.1"); r2.addWidget(self.cb)
        r2.addWidget(QLabel("V_base (L):")); self.vb = QLineEdit("0.020"); r2.addWidget(self.vb)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute pH"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            ca = float(self.ca.text()); va = float(self.va.text())
            cb = float(self.cb.text()); vb = float(self.vb.text())
            if ca <= 0 or va <= 0 or cb <= 0 or vb < 0: raise ValueError("invalid inputs")
            nA = ca * va
            nB = cb * vb
            Vtot = va + vb
            if nB < nA:
                h = (nA - nB) / Vtot
                pH = -math.log10(h)
                region = "acidic (pre-equivalence)"
            elif nB > nA:
                oh = (nB - nA) / Vtot
                pH = 14 + math.log10(oh)
                region = "basic (post-equivalence)"
            else:
                pH = 7.0
                region = "equivalence"
            self.result.setText(f"pH = {pH:.4f}  —  {region}")
            add_log_entry(self.TITLE, action="Compute", data={"ca": ca, "va": va, "cb": cb, "vb": vb, "pH": pH, "region": region})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
