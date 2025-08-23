from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

g0 = 9.80665  # m/s^2

class Tool(QDialog):
    TITLE = "Rocket Equation (Tsiolkovsky)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Isp (s):")); self.isp = QLineEdit("300"); r1.addWidget(self.isp)
        r1.addWidget(QLabel("m0 (kg):")); self.m0 = QLineEdit("50000"); r1.addWidget(self.m0)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("mf (kg):")); self.mf = QLineEdit("15000"); r2.addWidget(self.mf)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute Δv"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            Isp = float(self.isp.text()); m0 = float(self.m0.text()); mf = float(self.mf.text())
            if Isp <= 0 or m0 <= 0 or mf <= 0 or mf >= m0: raise ValueError("Isp>0, 0<mf<m0")
            dv = Isp * g0 * math.log(m0/mf)
            self.result.setText(f"Δv ≈ {dv:.6g} m/s")
            add_log_entry(self.TITLE, action="Compute", data={"Isp": Isp, "m0": m0, "mf": mf, "delta_v": dv})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
