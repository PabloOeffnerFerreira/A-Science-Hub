from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Momentum Conservation"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("m₁ (kg):")); self.m1 = QLineEdit("1"); r1.addWidget(self.m1)
        r1.addWidget(QLabel("v₁ (m/s):")); self.v1 = QLineEdit("2"); r1.addWidget(self.v1)
        r1.addWidget(QLabel("m₂ (kg):")); self.m2 = QLineEdit("1"); r1.addWidget(self.m2)
        r1.addWidget(QLabel("v₂ (m/s):")); self.v2 = QLineEdit("0"); r1.addWidget(self.v2)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            m1 = float(self.m1.text()); v1 = float(self.v1.text())
            m2 = float(self.m2.text()); v2 = float(self.v2.text())
            if m1 <= 0 or m2 <= 0: raise ValueError("m>0")
            p_tot = m1*v1 + m2*v2
            self.result.setText(f"Total momentum p = {p_tot:.6g} kg·m/s")
            add_log_entry(self.TITLE, action="Compute", data={"m1": m1, "v1": v1, "m2": m2, "v2": v2, "p_total": p_tot})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
