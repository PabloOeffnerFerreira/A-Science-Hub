from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Impulse & Momentum"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Mass m (kg):")); self.m = QLineEdit("1"); r1.addWidget(self.m)
        r1.addWidget(QLabel("v₀ (m/s):")); self.v0 = QLineEdit("0"); r1.addWidget(self.v0)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Avg Force F (N):")); self.F = QLineEdit("10"); r2.addWidget(self.F)
        r2.addWidget(QLabel("Δt (s):")); self.dt = QLineEdit("0.5"); r2.addWidget(self.dt)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            m = float(self.m.text()); v0 = float(self.v0.text())
            F = float(self.F.text()); dt = float(self.dt.text())
            if m <= 0 or dt <= 0: raise ValueError("m>0, dt>0")
            J = F * dt
            dv = J / m
            vf = v0 + dv
            self.result.setText(f"Impulse J = {J:.6g} N·s,  v_f = {vf:.6g} m/s")
            add_log_entry(self.TITLE, action="Compute", data={"m": m, "v0": v0, "F": F, "dt": dt, "J": J, "vf": vf})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
