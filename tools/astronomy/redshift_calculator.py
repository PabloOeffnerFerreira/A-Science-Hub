from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

c = 299792458.0  # m/s

class Tool(QDialog):
    TITLE = "Redshift / Velocity (Nonrelativistic + Relativistic)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(780)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Mode:")); self.mode = QComboBox(); self.mode.addItems(["z → v (relativistic)", "v → z (relativistic)", "z ↔ Δλ/λ (definition)"])
        r0.addWidget(self.mode); lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("z or v (m/s):")); self.x = QLineEdit("0.01"); r1.addWidget(self.x)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

        self.input_value = self.x
    def _go(self):
        try:
            mode = self.mode.currentText()
            val = float(self.x.text())
            if mode == "z → v (relativistic)":
                z = val
                if z <= -1: raise ValueError("z>-1")
                beta = ((1+z)**2 - 1)/((1+z)**2 + 1)
                v = beta*c
                self.result.setText(f"v ≈ {v:.6g} m/s (β={beta:.6g})")
                out = {"z": z, "v": v, "beta": beta}
            elif mode == "v → z (relativistic)":
                v = val
                if abs(v) >= c: raise ValueError("|v|<c")
                beta = v/c
                z = math.sqrt((1+beta)/(1-beta)) - 1
                self.result.setText(f"z ≈ {z:.6g}")
                out = {"v": v, "beta": beta, "z": z}
            else:
                z = val
                self.result.setText(f"Δλ/λ = z = {z:.6g}")
                out = {"z": z}
            add_log_entry(self.TITLE, action="Compute", data={"mode": mode, **out})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
