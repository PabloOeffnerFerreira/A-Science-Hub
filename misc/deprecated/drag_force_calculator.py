
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Drag Force"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(420)
        lay = QVBoxLayout(self)

        def row(lbl, default="", units=None):
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); e = QLineEdit(default); r.addWidget(e); u = None
            if units: u = QComboBox(); u.addItems(units); r.addWidget(u)
            lay.addLayout(r); return e,u
        self.rho, self.rhou = row("Air density ρ:", "1.225", ["kg/m³","g/cm³"])
        self.v, self.vu = row("Velocity v:", "10", ["m/s","km/h","mph"])
        self.cd, _ = row("Drag coefficient C_d:", "1.0")
        self.A, self.Au = row("Area A:", "0.5", ["m²","cm²","ft²"])

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            rho = float(self.rho.text()); v = float(self.v.text()); cd = float(self.cd.text()); A = float(self.A.text())
            if self.rhou.currentText()=="g/cm³": rho *= 1000.0
            if self.vu.currentText()=="km/h": v /= 3.6
            elif self.vu.currentText()=="mph": v *= 0.44704
            if self.Au.currentText()=="cm²": A /= 1e4
            elif self.Au.currentText()=="ft²": A *= 0.09290304
            Fd = 0.5 * rho * v*v * cd * A
            self.result.setText(f"F_d = {Fd:.6g} N")
            add_log_entry(self.TITLE, action="Compute", data={"rho": rho, "v": v, "cd": cd, "A": A, "Fd": Fd})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
