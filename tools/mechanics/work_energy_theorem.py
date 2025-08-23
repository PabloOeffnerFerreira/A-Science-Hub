from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Work–Energy Theorem"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Mass m (kg):")); self.m = QLineEdit("1"); r1.addWidget(self.m)
        r1.addWidget(QLabel("v₀ (m/s):")); self.v0 = QLineEdit("0"); r1.addWidget(self.v0)
        r1.addWidget(QLabel("v_f (m/s):")); self.vf = QLineEdit("2"); r1.addWidget(self.vf)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            m = float(self.m.text()); v0 = float(self.v0.text()); vf = float(self.vf.text())
            if m <= 0: raise ValueError("m>0")
            W = 0.5*m*(vf*vf - v0*v0)
            self.result.setText(f"W = ΔE_k = {W:.6g} J")
            add_log_entry(self.TITLE, action="Compute", data={"m": m, "v0": v0, "vf": vf, "W": W})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
