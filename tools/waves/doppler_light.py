from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry
import math

c = 3e8

class Tool(QDialog):
    TITLE = "Relativistic Doppler (Light)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("f_source (Hz):")); self.f = QLineEdit("6e14"); r1.addWidget(self.f)
        r1.addWidget(QLabel("v (m/s, +approach):")); self.v = QLineEdit("1e6"); r1.addWidget(self.v)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            f = float(self.f.text()); v = float(self.v.text())
            if abs(v) >= c: raise ValueError("|v|<c")
            factor = math.sqrt((1+v/c)/(1-v/c))
            f_obs = f*factor
            self.result.setText(f"Observed f' = {f_obs:.6g} Hz")
            add_log_entry(self.TITLE, action="Compute", data={"f": f, "v": v, "f_obs": f_obs})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
