
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from core.data.functions.log import add_log_entry

DNA_W = {"A": 313.21, "T": 304.2, "G": 329.21, "C": 289.18, "U": 290.17}
PROT_W = {
    "A": 89.09, "R": 174.2, "N": 132.12, "D": 133.1, "C": 121.15,
    "E": 147.13, "Q": 146.15, "G": 75.07, "H": 155.16, "I": 131.17,
    "L": 131.17, "K": 146.19, "M": 149.21, "F": 165.19, "P": 115.13,
    "S": 105.09, "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15
}

class Tool(QDialog):
    TITLE = "Molecular Weight Calculator"

    def __init__(self):
        super().__init__(); self.setMinimumWidth(460); self.setWindowTitle(self.TITLE)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Enter Sequence (DNA/RNA or Protein):"))
        self.seq = QTextEdit(); self.seq.setFixedHeight(60); lay.addWidget(self.seq)
        self.out = QLabel(""); lay.addWidget(self.out)
        btn = QPushButton("Calculate"); lay.addWidget(btn)
        btn.clicked.connect(self._calc)

    def _calc(self):
        s = self.seq.toPlainText().strip().upper().replace("\n","").replace(" ","")
        if not s:
            msg = "Please enter a sequence."; self.out.setText(msg); return
        if all(ch in DNA_W for ch in s):
            w = sum(DNA_W[ch] for ch in s); msg = f"Approximate DNA/RNA MW: {w:.2f} Da"
        elif all(ch in PROT_W for ch in s):
            w = sum(PROT_W[ch] for ch in s); msg = f"Approximate Protein MW: {w:.2f} Da"
        else:
            msg = "Sequence contains invalid characters."
        self.out.setText(msg); add_log_entry(self.TITLE, action="Calculate", data={"len": len(s), "msg": msg})
