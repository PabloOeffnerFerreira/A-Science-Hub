from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Hardy–Weinberg Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Allele frequency p (0..1):")); self.p = QLineEdit("0.6"); r1.addWidget(self.p)
        r1.addWidget(QLabel("Population size N (optional):")); self.N = QLineEdit(""); r1.addWidget(self.N)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            p = float(self.p.text())
            if not (0 <= p <= 1): raise ValueError("p must be in [0,1]")
            q = 1 - p
            AA = p*p
            Aa = 2*p*q
            aa = q*q
            txt = f"p={p:.4f}, q={q:.4f}  →  f(AA)={AA:.4f}, f(Aa)={Aa:.4f}, f(aa)={aa:.4f}"
            Ntxt = self.N.text().strip()
            if Ntxt:
                N = int(float(Ntxt))
                if N <= 0: raise ValueError("N>0")
                txt += f"  |  expected counts: AA≈{AA*N:.2f}, Aa≈{Aa*N:.2f}, aa≈{aa*N:.2f}"
            self.result.setText(txt)
            add_log_entry(self.TITLE, action="Compute", data={"p": p, "q": q, "f_AA": AA, "f_Aa": Aa, "f_aa": aa, "N": Ntxt or None})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
