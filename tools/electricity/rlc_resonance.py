from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "RLC Resonance Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(680)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("R (Ω):")); self.R = QLineEdit("10"); r1.addWidget(self.R)
        r1.addWidget(QLabel("L (H):")); self.L = QLineEdit("0.1"); r1.addWidget(self.L)
        r1.addWidget(QLabel("C (F):")); self.C = QLineEdit("1e-6"); r1.addWidget(self.C)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Config:")); self.cfg = QComboBox(); self.cfg.addItems(["Series", "Parallel"]); r2.addWidget(self.cfg)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            R = float(self.R.text()); L = float(self.L.text()); C = float(self.C.text())
            if L <= 0 or C <= 0 or R < 0: raise ValueError("R≥0, L>0, C>0")
            w0 = 1.0 / math.sqrt(L*C)
            f0 = w0 / (2*math.pi)
            Q_series = (1.0/R) * math.sqrt(L/C) if R > 0 else float("inf")
            Q_parallel = R * math.sqrt(C/L)
            if self.cfg.currentText() == "Series":
                txt = f"ω₀ = {w0:.6g} rad/s, f₀ = {f0:.6g} Hz, Q_series ≈ {Q_series:.6g}"
            else:
                txt = f"ω₀ = {w0:.6g} rad/s, f₀ = {f0:.6g} Hz, Q_parallel ≈ {Q_parallel:.6g}"
            self.result.setText(txt)
            add_log_entry(self.TITLE, action="Compute", data={"R": R, "L": L, "C": C, "omega0": w0, "f0": f0, "cfg": self.cfg.currentText()})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
