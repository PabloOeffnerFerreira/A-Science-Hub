from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Enzyme Kinetics (Michaelis–Menten)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Vmax (rate units):")); self.vmax = QLineEdit("1.0"); r1.addWidget(self.vmax)
        r1.addWidget(QLabel("Km (same conc units as [S]):")); self.km = QLineEdit("0.5"); r1.addWidget(self.km)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("[S] (substrate concentration):")); self.S = QLineEdit("0.25"); r2.addWidget(self.S)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute v"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            Vmax = float(self.vmax.text()); Km = float(self.km.text()); S = float(self.S.text())
            if Vmax < 0 or Km < 0 or S < 0: raise ValueError("Inputs must be ≥ 0")
            v = (Vmax * S) / (Km + S) if (Km + S) > 0 else 0.0
            self.result.setText(f"v = {v:.6g} (rate units)")
            add_log_entry(self.TITLE, action="Compute", data={"Vmax": Vmax, "Km": Km, "S": S, "v": v})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
