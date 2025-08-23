from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Parallax Distance (pc = 1/p\")"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Parallax p (arcseconds):")); self.p = QLineEdit("0.1"); r1.addWidget(self.p)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute distance"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            p = float(self.p.text())
            if p <= 0: raise ValueError("p>0")
            d_pc = 1.0/p
            self.result.setText(f"d ≈ {d_pc:.6g} pc  (≈ {d_pc*3.26156:.6g} ly)")
            add_log_entry(self.TITLE, action="Compute", data={"p_arcsec": p, "d_pc": d_pc, "d_ly": d_pc*3.26156})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
