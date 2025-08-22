
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Average Speed"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(380)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout(); r1.addWidget(QLabel("Distance:")); self.d = QLineEdit("100"); self.du = QComboBox(); self.du.addItems(["m","km","mile","ft"]); r1.addWidget(self.d); r1.addWidget(self.du); lay.addLayout(r1)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("Time:")); self.t = QLineEdit("10"); self.tu = QComboBox(); self.tu.addItems(["s","min","hr"]); r2.addWidget(self.t); r2.addWidget(self.tu); lay.addLayout(r2)
        r3 = QHBoxLayout(); r3.addWidget(QLabel("Output unit:")); self.su = QComboBox(); self.su.addItems(["m/s","km/h","mph"]); r3.addWidget(self.su); lay.addLayout(r3)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn)
        btn.clicked.connect(self._go)

    def _go(self):
        try:
            d = float(self.d.text()); t = float(self.t.text())
            if t == 0: raise ValueError("t=0")
            # to meters
            du = self.du.currentText()
            if du=="km": d *= 1000
            elif du=="mile": d *= 1609.344
            elif du=="ft": d *= 0.3048
            # to seconds
            tu = self.tu.currentText()
            if tu=="min": t *= 60
            elif tu=="hr": t *= 3600
            v = d/t
            # from m/s
            su = self.su.currentText()
            if su=="km/h": v *= 3.6
            elif su=="mph": v *= 2.23693629
            self.result.setText(f"Speed = {v:.6g} {su}")
            add_log_entry(self.TITLE, action="Compute", data={"d_m": d, "t_s": t, "v_out": v, "unit": su})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
