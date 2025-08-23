from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Standing Wave in Air Column"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Length L (m):")); self.L = QLineEdit("0.5"); r1.addWidget(self.L)
        r1.addWidget(QLabel("Mode n:")); self.n = QLineEdit("1"); r1.addWidget(self.n)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Speed of sound v (m/s):")); self.v = QLineEdit("343"); r2.addWidget(self.v)
        r2.addWidget(QLabel("Ends:")); self.ends = QComboBox(); self.ends.addItems(["Both Open", "One Closed"]); r2.addWidget(self.ends)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            L = float(self.L.text()); n = int(float(self.n.text())); v = float(self.v.text())
            if L <= 0 or n <= 0 or v <= 0: raise ValueError("invalid inputs")
            if self.ends.currentText() == "Both Open":
                lam = 2*L/n
            else:
                lam = 4*L/(2*n-1)
            f = v/lam
            self.result.setText(f"λ = {lam:.6g} m, f = {f:.6g} Hz")
            add_log_entry(self.TITLE, action="Compute", data={"L": L, "n": n, "v": v, "ends": self.ends.currentText(), "lambda": lam, "f": f})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
