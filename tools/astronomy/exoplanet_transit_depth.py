from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Exoplanet Transit Depth"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(700)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Planet radius Rp (km):")); self.Rp = QLineEdit("6371"); r1.addWidget(self.Rp)
        r1.addWidget(QLabel("Star radius Rs (km):")); self.Rs = QLineEdit("696340"); r1.addWidget(self.Rs)
        lay.addLayout(r1)

        self.result = QLabel("Depth ≈ (Rp/Rs)^2"); lay.addWidget(self.result)
        btn = QPushButton("Compute depth"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            Rp = float(self.Rp.text()); Rs = float(self.Rs.text())
            if Rp <= 0 or Rs <= 0 or Rp >= Rs: raise ValueError("0<Rp<Rs")
            depth = (Rp/Rs)**2
            self.result.setText(f"Transit depth ≈ {depth*100:.6g}%")
            add_log_entry(self.TITLE, action="Compute", data={"Rp_km": Rp, "Rs_km": Rs, "depth_frac": depth})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
