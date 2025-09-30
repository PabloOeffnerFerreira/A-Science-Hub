from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry
from core.data.functions.elect_utils import MU0

class Tool(QDialog):
    TITLE = "Skin Depth (δ = sqrt(2/(ωμσ)))"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Frequency f (Hz):")); self.f = QLineEdit("1e6"); r1.addWidget(self.f)
        r1.addWidget(QLabel("Conductivity σ (S/m):")); self.sigma = QLineEdit("5.8e7"); r1.addWidget(self.sigma)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Relative μ_r:")); self.mu_r = QLineEdit("1.0"); r2.addWidget(self.mu_r)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute δ"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            f = float(self.f.text()); sigma = float(self.sigma.text()); mu_r = float(self.mu_r.text())
            if f <= 0 or sigma <= 0 or mu_r <= 0: raise ValueError("All inputs > 0")
            omega = 2*math.pi*f
            mu = MU0*mu_r
            delta = math.sqrt(2.0/(omega*mu*sigma))
            self.result.setText(f"δ ≈ {delta:.6g} m")
            add_log_entry(self.TITLE, action="Compute", data={"f": f, "sigma": sigma, "mu_r": mu_r, "delta": delta})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
