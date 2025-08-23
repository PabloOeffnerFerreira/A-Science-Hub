from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "SIR Model (Well-mixed, deterministic)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("S0:")); self.S0 = QLineEdit("990"); r1.addWidget(self.S0)
        r1.addWidget(QLabel("I0:")); self.I0 = QLineEdit("10"); r1.addWidget(self.I0)
        r1.addWidget(QLabel("R0:")); self.R0 = QLineEdit("0"); r1.addWidget(self.R0)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("β (1/day):")); self.beta = QLineEdit("0.3"); r2.addWidget(self.beta)
        r2.addWidget(QLabel("γ (1/day):")); self.gamma = QLineEdit("0.1"); r2.addWidget(self.gamma)
        r2.addWidget(QLabel("t (days):")); self.t = QLineEdit("30"); r2.addWidget(self.t)
        lay.addLayout(r2)

        self.result = QLabel("Educational model only."); lay.addWidget(self.result)
        btn = QPushButton("Compute R0 and peak I"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            S0 = float(self.S0.text()); I0 = float(self.I0.text()); R0x = float(self.R0.text())
            beta = float(self.beta.text()); gamma = float(self.gamma.text()); t = float(self.t.text())
            if any(v < 0 for v in [S0, I0, R0x, beta, gamma, t]): raise ValueError("Nonnegative only")
            N = S0 + I0 + R0x
            R0_basic = beta / gamma if gamma > 0 else float("inf")
            # Simple heuristic peak approx for SIR: S_peak ≈ N / R0_basic (if R0>1)
            S_peak = N / R0_basic if R0_basic > 1 else N
            I_peak_est = N - S_peak - (gamma/beta)*N*math.log(S_peak/N) if R0_basic > 1 else I0
            self.result.setText(f"R0 ≈ {R0_basic:.3f}, Estimated I_peak ≈ {max(I_peak_est, 0):.3f}")
            add_log_entry(self.TITLE, action="Compute", data={"S0": S0, "I0": I0, "R0": R0x, "beta": beta, "gamma": gamma, "R0_basic": R0_basic, "I_peak_est": I_peak_est})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
