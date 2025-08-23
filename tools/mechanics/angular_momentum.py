from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Angular Momentum Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(480)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Moment of inertia I (kg·m²):")); self.I = QLineEdit("1"); r1.addWidget(self.I)
        r1.addWidget(QLabel("Angular velocity ω (rad/s):")); self.w = QLineEdit("2"); r1.addWidget(self.w)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            I = float(self.I.text()); w = float(self.w.text())
            if I < 0: raise ValueError("I≥0")
            L = I*w
            self.result.setText(f"L = {L:.6g} kg·m²/s")
            add_log_entry(self.TITLE, action="Compute", data={"I": I, "omega": w, "L": L})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
