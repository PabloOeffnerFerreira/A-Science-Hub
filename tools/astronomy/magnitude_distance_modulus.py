from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Magnitude ↔ Distance (Distance Modulus)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Mode:")); self.mode = QComboBox(); self.mode.addItems(["m,M → distance", "m,d → M", "M,d → m"])
        r0.addWidget(self.mode); lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("m (apparent mag):")); self.m = QLineEdit("10"); r1.addWidget(self.m)
        r1.addWidget(QLabel("M (absolute mag):")); self.M = QLineEdit("5"); r1.addWidget(self.M)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Distance d (pc):")); self.d = QLineEdit(""); r2.addWidget(self.d)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            mode = self.mode.currentText()
            m = float(self.m.text()) if self.m.text().strip() else None
            M = float(self.M.text()) if self.M.text().strip() else None
            d = float(self.d.text()) if self.d.text().strip() else None
            if mode == "m,M → distance":
                if m is None or M is None: raise ValueError("need m and M")
                mu = m - M
                d = 10**((mu + 5)/5.0)
                self.result.setText(f"d ≈ {d:.6g} pc (μ={mu:.3f})")
            elif mode == "m,d → M":
                if m is None or d is None or d <= 0: raise ValueError("need m and d>0")
                M = m - 5*math.log10(d) + 5
                self.result.setText(f"M ≈ {M:.6g}")
            else:
                if M is None or d is None or d <= 0: raise ValueError("need M and d>0")
                m = M + 5*math.log10(d) - 5
                self.result.setText(f"m ≈ {m:.6g}")
            add_log_entry(self.TITLE, action="Compute", data={"mode": mode, "m": m, "M": M, "d_pc": d})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
