from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Thin-Film Interference (Normal Incidence)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Film thickness t (nm):")); self.t = QLineEdit("300"); r1.addWidget(self.t)
        r1.addWidget(QLabel("Refractive index n:")); self.n = QLineEdit("1.33"); r1.addWidget(self.n)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Condition:")); self.cond = QComboBox(); self.cond.addItems(["Constructive", "Destructive"]); r2.addWidget(self.cond)
        r2.addWidget(QLabel("Order m (integer ≥ 0):")); self.m = QLineEdit("0"); r2.addWidget(self.m)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute λ"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            t_nm = float(self.t.text()); n = float(self.n.text()); m = int(float(self.m.text()))
            if t_nm <= 0 or n <= 0 or m < 0: raise ValueError("invalid inputs")
            t_m = t_nm * 1e-9
            if self.cond.currentText() == "Constructive":
                lam = 2*n*t_m / (m + 0.5)  # with one phase inversion
            else:
                lam = 2*n*t_m / m if m > 0 else float("nan")
            lam_nm = lam * 1e9
            if not math.isfinite(lam_nm) or lam_nm <= 0:
                self.result.setText("No valid wavelength for chosen parameters.")
                add_log_entry(self.TITLE, action="NoSolution", data={"t_nm": t_nm, "n": n, "m": m, "mode": self.cond.currentText()})
                return
            self.result.setText(f"λ ≈ {lam_nm:.6g} nm")
            add_log_entry(self.TITLE, action="Compute", data={"t_nm": t_nm, "n": n, "m": m, "mode": self.cond.currentText(), "lambda_nm": lam_nm})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
