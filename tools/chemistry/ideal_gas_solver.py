from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry
from core.data.functions.chemistry_utils import R

class Tool(QDialog):
    TITLE = "Ideal Gas Solver (PV = nRT)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Solve for:"))
        self.target = QComboBox(); self.target.addItems(["P (Pa)", "V (m³)", "n (mol)", "T (K)"])
        r0.addWidget(self.target); lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("P (Pa):")); self.P = QLineEdit("101325"); r1.addWidget(self.P)
        r1.addWidget(QLabel("V (m³):")); self.V = QLineEdit("0.024"); r1.addWidget(self.V)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("n (mol):")); self.n = QLineEdit("1.0"); r2.addWidget(self.n)
        r2.addWidget(QLabel("T (K):")); self.T = QLineEdit("298"); r2.addWidget(self.T)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            P = float(self.P.text()); V = float(self.V.text()); n = float(self.n.text()); T = float(self.T.text())
            if V <= 0 or T <= 0 or n < 0: raise ValueError("V>0, T>0, n≥0")
            tgt = self.target.currentText()
            if tgt.startswith("P"):
                P = n*R*T / V
                self.result.setText(f"P ≈ {P:.6g} Pa")
            elif tgt.startswith("V"):
                V = n*R*T / P
                self.result.setText(f"V ≈ {V:.6g} m³")
            elif tgt.startswith("n"):
                n = P*V / (R*T)
                self.result.setText(f"n ≈ {n:.6g} mol")
            else:
                T = P*V / (n*R) if n > 0 else float("inf")
                self.result.setText(f"T ≈ {T:.6g} K")
            add_log_entry(self.TITLE, action="Compute", data={"P": P, "V": V, "n": n, "T": T, "target": tgt})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
