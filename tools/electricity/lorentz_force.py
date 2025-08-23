from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Lorentz Force (q(E + v×B))"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("q (C):")); self.q = QLineEdit("1e-6"); r0.addWidget(self.q)
        lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("E (Ex,Ey,Ez) V/m:")); self.Ex = QLineEdit("0"); r1.addWidget(self.Ex)
        self.Ey = QLineEdit("0"); r1.addWidget(self.Ey)
        self.Ez = QLineEdit("0"); r1.addWidget(self.Ez)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("v (vx,vy,vz) m/s:")); self.vx = QLineEdit("0"); r2.addWidget(self.vx)
        self.vy = QLineEdit("0"); r2.addWidget(self.vy)
        self.vz = QLineEdit("0"); r2.addWidget(self.vz)
        lay.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("B (Bx,By,Bz) T:")); self.Bx = QLineEdit("0"); r3.addWidget(self.Bx)
        self.By = QLineEdit("0"); r3.addWidget(self.By)
        self.Bz = QLineEdit("1"); r3.addWidget(self.Bz)
        lay.addLayout(r3)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute F"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            q = float(self.q.text())
            Ex, Ey, Ez = float(self.Ex.text()), float(self.Ey.text()), float(self.Ez.text())
            vx, vy, vz = float(self.vx.text()), float(self.vy.text()), float(self.vz.text())
            Bx, By, Bz = float(self.Bx.text()), float(self.By.text()), float(self.Bz.text())
            cx = vy*Bz - vz*By
            cy = vz*Bx - vx*Bz
            cz = vx*By - vy*Bx
            Fx = q*(Ex + cx)
            Fy = q*(Ey + cy)
            Fz = q*(Ez + cz)
            self.result.setText(f"F = ({Fx:.6g}, {Fy:.6g}, {Fz:.6g}) N")
            add_log_entry(self.TITLE, action="Compute", data={"q": q, "E": (Ex,Ey,Ez), "v": (vx,vy,vz), "B": (Bx,By,Bz), "F": (Fx,Fy,Fz)})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
