from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Damped Oscillator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Amplitude A (m):")); self.A = QLineEdit("1"); r1.addWidget(self.A)
        r1.addWidget(QLabel("γ (1/s):")); self.gamma = QLineEdit("0.1"); r1.addWidget(self.gamma)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("ω₀ (rad/s):")); self.w0 = QLineEdit("6.28"); r2.addWidget(self.w0)
        r2.addWidget(QLabel("t (s):")); self.t = QLineEdit("1"); r2.addWidget(self.t)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            A = float(self.A.text()); gamma = float(self.gamma.text())
            w0 = float(self.w0.text()); t = float(self.t.text())
            if A < 0 or gamma < 0 or w0 <= 0 or t < 0: raise ValueError("invalid input")
            x = A*math.exp(-gamma*t)*math.cos(math.sqrt(max(0,w0*w0-gamma*gamma))*t)
            self.result.setText(f"x(t) = {x:.6g} m")
            add_log_entry(self.TITLE, action="Compute", data={"A": A, "gamma": gamma, "w0": w0, "t": t, "x": x})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
