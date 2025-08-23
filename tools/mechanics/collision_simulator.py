from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "1D Collision Simulator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("m₁ (kg):")); self.m1 = QLineEdit("1"); r1.addWidget(self.m1)
        r1.addWidget(QLabel("v₁ (m/s):")); self.v1 = QLineEdit("2"); r1.addWidget(self.v1)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("m₂ (kg):")); self.m2 = QLineEdit("1"); r2.addWidget(self.m2)
        r2.addWidget(QLabel("v₂ (m/s):")); self.v2 = QLineEdit("0"); r2.addWidget(self.v2)
        lay.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Type:")); self.typ = QComboBox(); self.typ.addItems(["Elastic", "Perfectly Inelastic"]); r3.addWidget(self.typ)
        lay.addLayout(r3)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            m1 = float(self.m1.text()); m2 = float(self.m2.text())
            v1 = float(self.v1.text()); v2 = float(self.v2.text())
            if m1 <= 0 or m2 <= 0: raise ValueError("m>0")
            mode = self.typ.currentText()
            if mode == "Elastic":
                v1f = (m1-m2)/(m1+m2)*v1 + (2*m2)/(m1+m2)*v2
                v2f = (2*m1)/(m1+m2)*v1 + (m2-m1)/(m1+m2)*v2
                txt = f"Elastic: v₁' = {v1f:.6g} m/s, v₂' = {v2f:.6g} m/s"
                log = {"mode": "elastic", "v1f": v1f, "v2f": v2f}
            else:
                vf = (m1*v1 + m2*v2)/(m1+m2)
                txt = f"Inelastic: shared v' = {vf:.6g} m/s"
                log = {"mode": "inelastic", "vf": vf}
            self.result.setText(txt)
            add_log_entry(self.TITLE, action="Compute", data={"m1": m1, "v1": v1, "m2": m2, "v2": v2, **log})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
