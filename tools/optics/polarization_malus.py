from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Polarization (Malus' Law)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("I₀ (arbitrary):")); self.I0 = QLineEdit("1.0"); r1.addWidget(self.I0)
        r1.addWidget(QLabel("Angle θ (deg):")); self.theta = QLineEdit("30"); r1.addWidget(self.theta)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute I"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            I0 = float(self.I0.text()); th = math.radians(float(self.theta.text()))
            if I0 < 0: raise ValueError("I0≥0")
            I = I0 * (math.cos(th)**2)
            self.result.setText(f"I = {I:.6g} (relative units)")
            add_log_entry(self.TITLE, action="Compute", data={"I0": I0, "theta_deg": math.degrees(th), "I": I})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
