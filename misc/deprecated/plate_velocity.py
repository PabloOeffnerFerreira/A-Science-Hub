
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Plate Velocity Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(420)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Distance (km):")); self.dist = QLineEdit(); lay.addWidget(self.dist)
        lay.addWidget(QLabel("Time (million years):")); self.time = QLineEdit(); lay.addWidget(self.time)
        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn)
        btn.clicked.connect(self._go)

    def _go(self):
        try:
            d_km = float(self.dist.text()); t_ma = float(self.time.text())
            # velocity in mm/yr: 1 km / 1 Myr = 1 mm/yr
            v_mm_yr = (d_km / t_ma) if t_ma != 0 else float("inf")
            self.result.setText(f"Velocity: {v_mm_yr:.3g} mm/yr")
            add_log_entry(self.TITLE, action="Compute", data={"d_km": d_km, "t_ma": t_ma, "v_mm_yr": v_mm_yr})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
