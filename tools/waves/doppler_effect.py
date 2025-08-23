from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Doppler Effect (Sound, 1D)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("f_source (Hz):")); self.f = QLineEdit("440"); r1.addWidget(self.f)
        r1.addWidget(QLabel("v_sound (m/s):")); self.v = QLineEdit("343"); r1.addWidget(self.v)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("v_source (m/s):")); self.vs = QLineEdit("0"); r2.addWidget(self.vs)
        r2.addWidget(QLabel("v_observer (m/s):")); self.vo = QLineEdit("0"); r2.addWidget(self.vo)
        lay.addLayout(r2)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            f = float(self.f.text()); v = float(self.v.text())
            vs = float(self.vs.text()); vo = float(self.vo.text())
            if v <= 0 or abs(vs) >= v: raise ValueError("0<|vs|<v, v>0")
            f_obs = f * (v + vo) / (v - vs)
            self.result.setText(f"Observed f' = {f_obs:.6g} Hz")
            add_log_entry(self.TITLE, action="Compute", data={"f": f, "v": v, "vs": vs, "vo": vo, "f_obs": f_obs})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
