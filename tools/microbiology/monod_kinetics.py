from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Monod Kinetics (μ = μmax S/(Ks+S))"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(680)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("μmax (1/h):")); self.umax = QLineEdit("1.0"); r1.addWidget(self.umax)
        r1.addWidget(QLabel("Ks (same units as S):")); self.Ks = QLineEdit("0.5"); r1.addWidget(self.Ks)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Substrate S:")); self.S = QLineEdit("0.8"); r2.addWidget(self.S)
        lay.addLayout(r2)

        self.result = QLabel("Educational model only."); lay.addWidget(self.result)
        btn = QPushButton("Compute μ"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            umax = float(self.umax.text()); Ks = float(self.Ks.text()); S = float(self.S.text())
            if umax < 0 or Ks < 0 or S < 0: raise ValueError("Inputs must be ≥ 0")
            mu = umax * S / (Ks + S) if (Ks + S) > 0 else 0.0
            self.result.setText(f"μ ≈ {mu:.6g} 1/h")
            add_log_entry(self.TITLE, action="Compute", data={"umax": umax, "Ks": Ks, "S": S, "mu": mu})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
