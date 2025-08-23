from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Diversity Indices (Shannon, Simpson)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Relative abundances (comma-separated, sum≈1):"))
        self.abunds = QLineEdit("0.4,0.3,0.2,0.1"); r0.addWidget(self.abunds)
        lay.addLayout(r0)

        self.result = QLabel("Educational indices only."); lay.addWidget(self.result)
        btn = QPushButton("Compute indices"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            parts = [float(x.strip()) for x in self.abunds.text().split(",") if x.strip() != ""]
            if any(p < 0 for p in parts) or sum(parts) <= 0: raise ValueError("Nonnegative and sum>0")
            total = sum(parts)
            p = [x/total for x in parts]
            H = -sum(pi*math.log(pi) for pi in p if pi > 0)
            D = 1 - sum(pi*pi for pi in p)
            self.result.setText(f"Shannon H ≈ {H:.4f}, Simpson D ≈ {D:.4f}")
            add_log_entry(self.TITLE, action="Compute", data={"abund": p, "H": H, "D": D})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
