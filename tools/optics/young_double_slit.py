from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Young's Double-Slit"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Wavelength λ (nm):")); self.lmbd = QLineEdit("532"); r1.addWidget(self.lmbd)
        r1.addWidget(QLabel("Slit separation d (m):")); self.d = QLineEdit("1e-4"); r1.addWidget(self.d)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Screen distance L (m):")); self.L = QLineEdit("1.0"); r2.addWidget(self.L)
        r2.addWidget(QLabel("Fringe order m (integer):")); self.m = QLineEdit("1"); r2.addWidget(self.m)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            lam_nm = float(self.lmbd.text()); d_m = float(self.d.text()); L = float(self.L.text()); m = int(float(self.m.text()))
            if lam_nm <= 0 or d_m <= 0 or L <= 0 or m < 0:
                raise ValueError("invalid inputs")
            lam = lam_nm * 1e-9
            arg = m * lam / d_m
            theta = math.asin(min(1.0, arg))
            y = L * math.tan(theta)
            spacing = lam * L / d_m
            self.result.setText(
                f"d = {d_m:.6g} m, θ_m ≈ {math.degrees(theta):.6g}°, "
                f"y_m ≈ {y:.6g} m, fringe spacing Δy ≈ {spacing:.6g} m"
            )
            add_log_entry(self.TITLE, action="Compute",
                          data={"lambda_nm": lam_nm, "d_m": d_m, "L": L, "m": m,
                                "theta_deg": math.degrees(theta), "y": y, "spacing": spacing})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
