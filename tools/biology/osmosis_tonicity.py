from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Osmosis & Tonicity"

    def __init__(self):
        super().__init__(); self.setMinimumWidth(360); self.setWindowTitle(self.TITLE)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Internal concentration (mM):"))
        self.int_e = QLineEdit()
        r1.addWidget(self.int_e)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("External concentration (mM):"))
        self.ext_e = QLineEdit()
        r2.addWidget(self.ext_e)
        lay.addLayout(r2)
        
        self.result = QLabel("")
        lay.addWidget(self.result)

        btn = QPushButton("Assess")
        lay.addWidget(btn)
        btn.clicked.connect(self._assess)

    def _assess(self):
        try:
            inside = float(self.int_e.text())
            outside = float(self.ext_e.text())
        except Exception:
            msg = "Invalid input."
            self.result.setText(msg)
            add_log_entry(self.TITLE, action="Error", data={"msg": msg})
            return

        if inside > outside:
            msg = "Hypertonic inside: Water leaves the cell"
        elif inside < outside:
            msg = "Hypotonic inside: Water enters the cell"
        else:
            msg = "Isotonic: No net water movement"

        self.result.setText(msg)
        add_log_entry(self.TITLE, action="Assess", data={"in": inside, "out": outside, "msg": msg})
