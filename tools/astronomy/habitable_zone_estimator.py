from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

Lsun = 3.828e26  # W
AU = 1.495978707e11  # m

class Tool(QDialog):
    TITLE = "Habitable Zone (Simple Flux Scaling)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Stellar Luminosity L (in L☉):")); self.L = QLineEdit("1.0"); r1.addWidget(self.L)
        lay.addLayout(r1)

        self.result = QLabel("Uses simple scaling: r ∝ √L"); lay.addWidget(self.result)
        btn = QPushButton("Compute HZ bounds"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            L_rel = float(self.L.text())
            if L_rel <= 0: raise ValueError("L>0")
            # Simple Kasting-like scaling (very rough): recent Venus ~0.75 AU, early Mars ~1.77 AU for Sun
            rin = 0.75 * math.sqrt(L_rel)
            rout = 1.77 * math.sqrt(L_rel)
            self.result.setText(f"Inner ≈ {rin:.3f} AU, Outer ≈ {rout:.3f} AU")
            add_log_entry(self.TITLE, action="Compute", data={"L_Lsun": L_rel, "r_in_AU": rin, "r_out_AU": rout})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
