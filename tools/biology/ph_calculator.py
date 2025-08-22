
from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "pH Calculator"

    def __init__(self):
        super().__init__(); self.setMinimumWidth(420); self.setWindowTitle(self.TITLE)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Enter H⁺ concentration [mol/L] (leave blank if using OH⁻):"))
        self.h = QLineEdit(); lay.addWidget(self.h)
        lay.addWidget(QLabel("Enter OH⁻ concentration [mol/L] (leave blank if using H⁺):"))
        self.oh = QLineEdit(); lay.addWidget(self.oh)
        self.out = QLabel(""); lay.addWidget(self.out)
        btn = QPushButton("Calculate"); lay.addWidget(btn)
        btn.clicked.connect(self._calc)

    def _calc(self):
        htxt = self.h.text().strip(); ohtxt = self.oh.text().strip()
        try:
            if htxt and ohtxt:
                msg = "Enter only one concentration."
            elif htxt:
                h = float(htxt); 
                if h <= 0: raise ValueError
                pH = -math.log10(h); msg = f"pH = {pH:.2f}"
            elif ohtxt:
                oh = float(ohtxt);
                if oh <= 0: raise ValueError
                pOH = -math.log10(oh); pH = 14 - pOH; msg = f"pOH = {pOH:.2f}, pH = {pH:.2f}"
            else:
                msg = "Enter at least one concentration."
        except Exception:
            msg = "Invalid input."
        self.out.setText(msg); add_log_entry(self.TITLE, action="Calculate", data={"H": htxt, "OH": ohtxt, "msg": msg})
