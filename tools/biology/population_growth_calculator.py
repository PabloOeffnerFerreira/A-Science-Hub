
from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Population Growth Calculator"

    def __init__(self):
        super().__init__(); self.setMinimumWidth(380); self.setWindowTitle(self.TITLE)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Initial Population (N₀):")); self.n0 = QLineEdit(); lay.addWidget(self.n0)
        lay.addWidget(QLabel("Growth Rate (r) [per time unit]:")); self.r = QLineEdit(); lay.addWidget(self.r)
        lay.addWidget(QLabel("Time (t):")); self.t = QLineEdit(); lay.addWidget(self.t)
        self.out = QLabel(""); lay.addWidget(self.out)
        btn = QPushButton("Calculate"); lay.addWidget(btn)
        btn.clicked.connect(self._calc)

    def _calc(self):
        try:
            N0 = float(self.n0.text()); r = float(self.r.text()); t = float(self.t.text())
            N = N0 * math.exp(r * t); msg = f"Population after {t} time units: {N:.2f}"
        except Exception as e:
            msg = "Invalid input."
        self.out.setText(msg); add_log_entry(self.TITLE, action="Calculate", data={"N0": self.n0.text(), "r": self.r.text(), "t": self.t.text(), "msg": msg})
