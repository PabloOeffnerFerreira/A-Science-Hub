from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Biofilm Growth (Gompertz Model)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(700)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("A (asymptote):")); self.A = QLineEdit("1.0"); r1.addWidget(self.A)
        r1.addWidget(QLabel("μ (rate):")); self.mu = QLineEdit("0.5"); r1.addWidget(self.mu)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("λ (lag time):")); self.lmbd = QLineEdit("2.0"); r2.addWidget(self.lmbd)
        r2.addWidget(QLabel("t:")); self.t = QLineEdit("5.0"); r2.addWidget(self.t)
        lay.addLayout(r2)

        self.result = QLabel("Educational model only."); lay.addWidget(self.result)
        btn = QPushButton("Compute size"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            A = float(self.A.text()); mu = float(self.mu.text()); lam = float(self.lmbd.text()); t = float(self.t.text())
            if A < 0 or mu < 0 or lam < 0 or t < 0: raise ValueError("Nonnegative only")
            y = A * math.exp(-math.exp((mu*math.e/A)*(lam - t) + 1))
            self.result.setText(f"Size ≈ {y:.6g} (relative units)")
            add_log_entry(self.TITLE, action="Compute", data={"A": A, "mu": mu, "lambda": lam, "t": t, "size": y})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
