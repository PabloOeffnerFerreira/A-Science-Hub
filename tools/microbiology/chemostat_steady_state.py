from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Chemostat Steady State (μ = D)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(740)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Dilution rate D (1/h):")); self.D = QLineEdit("0.4"); r1.addWidget(self.D)
        r1.addWidget(QLabel("μmax (1/h):")); self.umax = QLineEdit("1.0"); r1.addWidget(self.umax)
        r1.addWidget(QLabel("Ks:")); self.Ks = QLineEdit("0.5"); r1.addWidget(self.Ks)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Influent substrate S_in:")); self.Sin = QLineEdit("10"); r2.addWidget(self.Sin)
        lay.addLayout(r2)

        self.result = QLabel("Educational model only."); lay.addWidget(self.result)
        btn = QPushButton("Compute S* and μ"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            D = float(self.D.text()); umax = float(self.umax.text()); Ks = float(self.Ks.text()); Sin = float(self.Sin.text())
            if any(v < 0 for v in [D, umax, Ks, Sin]): raise ValueError("Nonnegative only")
            # Steady state for Monod: μ = D = umax*S*/(Ks+S*)  => solve for S*
            if D >= umax:
                self.result.setText("Washout regime (D ≥ μmax).")
                add_log_entry(self.TITLE, action="Compute", data={"D": D, "umax": umax, "Ks": Ks, "Sin": Sin, "state": "washout"})
                return
            Sstar = (D*Ks)/(umax - D)
            self.result.setText(f"S* ≈ {Sstar:.6g}, μ* = D = {D:.6g} 1/h")
            add_log_entry(self.TITLE, action="Compute", data={"D": D, "umax": umax, "Ks": Ks, "Sin": Sin, "S_star": Sstar})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
