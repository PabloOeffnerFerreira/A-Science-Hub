from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Simple Harmonic Motion"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Mode:"))
        self.mode = QComboBox(); self.mode.addItems(["Given ω", "Given k and m"])
        r0.addWidget(self.mode)
        lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Amplitude A (m):")); self.A = QLineEdit("1"); r1.addWidget(self.A)
        r1.addWidget(QLabel("Phase φ (deg):")); self.phi = QLineEdit("0"); r1.addWidget(self.phi)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("ω (rad/s) or k (N/m):")); self.x1 = QLineEdit("2*3.14159"); r2.addWidget(self.x1)
        r2.addWidget(QLabel("m (kg) (only if k given):")); self.m = QLineEdit(""); r2.addWidget(self.m)
        lay.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("t (s):")); self.t = QLineEdit("0.25"); r3.addWidget(self.t)
        lay.addLayout(r3)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            A = float(eval(self.A.text()))
            phi = math.radians(float(eval(self.phi.text())))
            t = float(eval(self.t.text()))
            if self.mode.currentText() == "Given ω":
                omega = float(eval(self.x1.text()))
            else:
                k = float(eval(self.x1.text()))
                m = float(eval(self.m.text()))
                if m <= 0 or k <= 0: raise ValueError("k>0, m>0")
                omega = math.sqrt(k/m)
            x = A*math.cos(omega*t + phi)
            v = -A*omega*math.sin(omega*t + phi)
            a = -A*omega*omega*math.cos(omega*t + phi)
            self.result.setText(f"x = {x:.6g} m, v = {v:.6g} m/s, a = {a:.6g} m/s², ω = {omega:.6g} rad/s")
            add_log_entry(self.TITLE, action="Compute", data={"A": A, "phi": phi, "t": t, "omega": omega, "x": x, "v": v, "a": a})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
