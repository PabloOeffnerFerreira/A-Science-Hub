from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Two-Lens System (Separation d)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("f1 (mm):")); self.f1 = QLineEdit("50"); r1.addWidget(self.f1)
        r1.addWidget(QLabel("f2 (mm):")); self.f2 = QLineEdit("100"); r1.addWidget(self.f2)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Separation d (mm):")); self.d = QLineEdit("10"); r2.addWidget(self.d)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute f_eq"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            f1 = float(self.f1.text()) * 1e-3
            f2 = float(self.f2.text()) * 1e-3
            d = float(self.d.text()) * 1e-3
            if f1 == 0 or f2 == 0: raise ValueError("f ≠ 0")
            feq = 1.0 / (1.0/f1 + 1.0/f2 - d/(f1*f2))
            self.result.setText(f"f_eq ≈ {feq*1e3:.6g} mm")
            add_log_entry(self.TITLE, action="Compute", data={"f1_mm": f1*1e3, "f2_mm": f2*1e3, "d_mm": d*1e3, "f_eq_mm": feq*1e3})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
