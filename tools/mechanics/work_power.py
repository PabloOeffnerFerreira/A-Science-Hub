from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Work & Power"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Force F (N):")); self.F = QLineEdit("10"); r1.addWidget(self.F)
        r1.addWidget(QLabel("Distance s (m):")); self.s = QLineEdit("3"); r1.addWidget(self.s)
        r1.addWidget(QLabel("Angle θ (deg):")); self.theta = QLineEdit("0"); r1.addWidget(self.theta)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Time t (s, optional):")); self.t = QLineEdit(""); r2.addWidget(self.t)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            F = float(self.F.text()); s = float(self.s.text()); th_deg = float(self.theta.text() or "0")
            th = math.radians(th_deg)
            W = F * s * math.cos(th)
            txt = f"W = {W:.6g} J"
            t_str = self.t.text().strip()
            if t_str:
                t = float(t_str)
                if t <= 0: raise ValueError("t>0")
                P = W / t
                txt += f",  P = {P:.6g} W"
            self.result.setText(txt)
            add_log_entry(self.TITLE, action="Compute", data={"F": F, "s": s, "theta_deg": th_deg, "W": W, "t": t_str or None})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
