from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry
from core.data.functions.chemistry_utils import F, R

class Tool(QDialog):
    TITLE = "Nernst Equation (E = E° - RT/nF ln Q)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("E° (V):")); self.E0 = QLineEdit("1.10"); r1.addWidget(self.E0)
        r1.addWidget(QLabel("n (electrons):")); self.n = QLineEdit("2"); r1.addWidget(self.n)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("T (K):")); self.T = QLineEdit("298"); r2.addWidget(self.T)
        r2.addWidget(QLabel("Q (reaction quotient):")); self.Q = QLineEdit("1.0"); r2.addWidget(self.Q)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute E"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            E0 = float(self.E0.text()); n = int(float(self.n.text())); T = float(self.T.text()); Q = float(self.Q.text())
            if n <= 0 or T <= 0 or Q <= 0: raise ValueError("n>0, T>0, Q>0")
            E = E0 - (R*T/(n*F))*math.log(Q)
            self.result.setText(f"E ≈ {E:.6g} V")
            add_log_entry(self.TITLE, action="Compute", data={"E0": E0, "n": n, "T": T, "Q": Q, "E": E})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
