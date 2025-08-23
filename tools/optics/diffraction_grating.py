from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Diffraction Grating Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Lines per mm:")); self.lines = QLineEdit("600"); r1.addWidget(self.lines)
        r1.addWidget(QLabel("Order m:")); self.m = QLineEdit("1"); r1.addWidget(self.m)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Wavelength λ (nm):")); self.lmbd = QLineEdit("532"); r2.addWidget(self.lmbd)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            lines = float(self.lines.text()); m = int(float(self.m.text())); l_nm = float(self.lmbd.text())
            if lines <= 0 or m <= 0 or l_nm <= 0: raise ValueError("inputs>0")
            d = 1.0 / (lines * 1e3)   # mm⁻¹ → m spacing
            lam = l_nm * 1e-9
            arg = m * lam / d
            if abs(arg) > 1:
                self.result.setText("No real solution: mλ > d")
                add_log_entry(self.TITLE, action="NoSolution", data={"lines_per_mm": lines, "m": m, "lambda_nm": l_nm})
                return
            theta = math.degrees(math.asin(arg))
            self.result.setText(f"d = {d:.6g} m, θ = {theta:.6g}°")
            add_log_entry(self.TITLE, action="Compute", data={"lines_per_mm": lines, "m": m, "lambda_nm": l_nm, "d": d, "theta_deg": theta})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
