from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry
from core.data.functions.chemistry_utils import R

class Tool(QDialog):
    TITLE = "Equilibrium Constant from ΔG°"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(680)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("ΔG° (kJ/mol):")); self.dG = QLineEdit("-5.0"); r1.addWidget(self.dG)
        r1.addWidget(QLabel("Temperature T (K):")); self.T = QLineEdit("298"); r1.addWidget(self.T)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute K"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            dG_kJ = float(self.dG.text()); T = float(self.T.text())
            if T <= 0: raise ValueError("T>0")
            dG = dG_kJ * 1e3
            K = math.exp(-dG/(R*T))
            self.result.setText(f"K ≈ {K:.6g}")
            add_log_entry(self.TITLE, action="Compute", data={"dG_kJmol": dG_kJ, "T": T, "K": K})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
