from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Single-Slit Diffraction (Minima)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Wavelength λ (nm):")); self.lmbd = QLineEdit("632.8"); r1.addWidget(self.lmbd)
        r1.addWidget(QLabel("Slit width a (m):")); self.a = QLineEdit("1e-4"); r1.addWidget(self.a)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Screen distance L (m):")); self.L = QLineEdit("1.0"); r2.addWidget(self.L)
        r2.addWidget(QLabel("Order m (≥1):")); self.m = QLineEdit("1"); r2.addWidget(self.m)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            lam_nm = float(self.lmbd.text()); a_m = float(self.a.text()); L = float(self.L.text()); m = int(float(self.m.text()))
            if lam_nm <= 0 or a_m <= 0 or L <= 0 or m <= 0:
                raise ValueError("invalid inputs")
            lam = lam_nm * 1e-9
            arg = m * lam / a_m
            if abs(arg) > 1:
                self.result.setText(f"a = {a_m:.6g} m, No real minimum for given m (mλ > a).")
                add_log_entry(self.TITLE, action="NoSolution",
                              data={"lambda_nm": lam_nm, "a_m": a_m, "L": L, "m": m})
                return
            theta = math.asin(arg)
            y = L * math.tan(theta)
            central_width = 2 * L * math.tan(math.asin(min(1.0, lam / a_m)))
            self.result.setText(
                f"a = {a_m:.6g} m, θ_m ≈ {math.degrees(theta):.6g}°, "
                f"y_m ≈ {y:.6g} m, central max width ≈ {central_width:.6g} m"
            )
            add_log_entry(self.TITLE, action="Compute",
                          data={"lambda_nm": lam_nm, "a_m": a_m, "L": L, "m": m,
                                "theta_deg": math.degrees(theta), "y": y, "central_width": central_width})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
