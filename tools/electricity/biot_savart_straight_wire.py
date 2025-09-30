from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry
from core.data.functions.elect_utils import MU0

class Tool(QDialog):
    TITLE = "Biot–Savart: Long Straight Wire"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Current I (A):")); self.I = QLineEdit("1.0"); r1.addWidget(self.I)
        r1.addWidget(QLabel("Distance r (m):")); self.r = QLineEdit("0.05"); r1.addWidget(self.r)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute B"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            I = float(self.I.text()); r = float(self.r.text())
            if r <= 0: raise ValueError("r>0")
            B = MU0*I/(2*math.pi*r)
            self.result.setText(f"B = {B:.6g} T")
            add_log_entry(self.TITLE, action="Compute", data={"I": I, "r": r, "B": B})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
