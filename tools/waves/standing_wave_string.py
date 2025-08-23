from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Standing Wave on a String"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Length L (m):")); self.L = QLineEdit("1"); r1.addWidget(self.L)
        r1.addWidget(QLabel("Mode n (integer):")); self.n = QLineEdit("1"); r1.addWidget(self.n)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Wave speed v (m/s):")); self.v = QLineEdit("100"); r2.addWidget(self.v)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            L = float(self.L.text()); n = int(float(self.n.text())); v = float(self.v.text())
            if L <= 0 or n <= 0 or v <= 0: raise ValueError("L>0, n>0, v>0")
            wavelength = 2*L/n
            freq = v / wavelength
            self.result.setText(f"λ = {wavelength:.6g} m, f = {freq:.6g} Hz")
            add_log_entry(self.TITLE, action="Compute", data={"L": L, "n": n, "v": v, "lambda": wavelength, "f": freq})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
