from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Power Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(480)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Work W (J):")); self.W = QLineEdit("10"); r1.addWidget(self.W)
        r1.addWidget(QLabel("Time t (s):")); self.t = QLineEdit("2"); r1.addWidget(self.t)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            W = float(self.W.text()); t = float(self.t.text())
            if t <= 0: raise ValueError("t>0")
            P = W/t
            self.result.setText(f"P = {P:.6g} W")
            add_log_entry(self.TITLE, action="Compute", data={"W": W, "t": t, "P": P})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
