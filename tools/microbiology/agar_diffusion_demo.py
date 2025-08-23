from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Agar Diffusion (Math Demo, 1D)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Diffusivity D (mm²/h):")); self.D = QLineEdit("1.0"); r1.addWidget(self.D)
        r1.addWidget(QLabel("Time t (h):")); self.t = QLineEdit("4"); r1.addWidget(self.t)
        lay.addLayout(r1)

        self.result = QLabel("Educational demonstration of Gaussian spread only."); lay.addWidget(self.result)
        btn = QPushButton("Compute RMS distance"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            D = float(self.D.text()); t = float(self.t.text())
            if D <= 0 or t < 0: raise ValueError("D>0, t≥0")
            rms = math.sqrt(2*D*t)
            self.result.setText(f"RMS distance ≈ {rms:.6g} mm")
            add_log_entry(self.TITLE, action="Compute", data={"D_mm2h": D, "t_h": t, "rms_mm": rms})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
