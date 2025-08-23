from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Rotational Kinematics"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("θ₀ (rad):")); self.theta0 = QLineEdit("0"); r1.addWidget(self.theta0)
        r1.addWidget(QLabel("ω₀ (rad/s):")); self.omega0 = QLineEdit("0"); r1.addWidget(self.omega0)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("α (rad/s²):")); self.alpha = QLineEdit("1"); r2.addWidget(self.alpha)
        r2.addWidget(QLabel("t (s):")); self.t = QLineEdit("1"); r2.addWidget(self.t)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            th0 = float(self.theta0.text()); w0 = float(self.omega0.text())
            a = float(self.alpha.text()); t = float(self.t.text())
            theta = th0 + w0*t + 0.5*a*t*t
            omega = w0 + a*t
            self.result.setText(f"θ = {theta:.6g} rad, ω = {omega:.6g} rad/s")
            add_log_entry(self.TITLE, action="Compute", data={"theta0": th0, "omega0": w0, "alpha": a, "t": t, "theta": theta, "omega": omega})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
