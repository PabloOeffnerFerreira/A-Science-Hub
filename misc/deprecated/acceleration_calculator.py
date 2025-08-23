
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Acceleration"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(360)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout(); r1.addWidget(QLabel("Δv:")); self.dv = QLineEdit("10"); self.dvu = QComboBox(); self.dvu.addItems(["m/s","km/h","mph"]); r1.addWidget(self.dv); r1.addWidget(self.dvu); lay.addLayout(r1)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("Time:")); self.t = QLineEdit("5"); self.tu = QComboBox(); self.tu.addItems(["s","min","hr"]); r2.addWidget(self.t); r2.addWidget(self.tu); lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn)
        btn.clicked.connect(self._go)

    def _go(self):
        try:
            dv = float(self.dv.text()); t = float(self.t.text())
            if self.dvu.currentText()=="km/h": dv /= 3.6
            elif self.dvu.currentText()=="mph": dv *= 0.44704
            if self.tu.currentText()=="min": t *= 60
            elif self.tu.currentText()=="hr": t *= 3600
            if t == 0: raise ValueError("t=0")
            a = dv/t
            self.result.setText(f"a = {a:.6g} m/s²")
            add_log_entry(self.TITLE, action="Compute", data={"dv_ms": dv, "t_s": t, "a": a})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
