
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Kinetic Energy"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(420)
        lay = QVBoxLayout(self)

        def row(lbl, default="", units=None):
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); e = QLineEdit(default); r.addWidget(e); u=None
            if units: u=QComboBox(); u.addItems(units); r.addWidget(u)
            lay.addLayout(r); return e,u
        self.m, self.mu = row("Mass m:", "1", ["kg","g","lb"])
        self.v, self.vu = row("Speed v:", "10", ["m/s","km/h","mph"])

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            m = float(self.m.text()); v = float(self.v.text())
            if self.mu.currentText()=="g": m /= 1000
            elif self.mu.currentText()=="lb": m *= 0.45359237
            if self.vu.currentText()=="km/h": v /= 3.6
            elif self.vu.currentText()=="mph": v *= 0.44704
            KE = 0.5 * m * v*v
            self.result.setText(f"E_k = {KE:.6g} J")
            add_log_entry(self.TITLE, action="Compute", data={"m": m, "v": v, "KE": KE})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
