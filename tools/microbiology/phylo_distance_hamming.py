from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from core.data.functions.log import add_log_entry

def hamming(a: str, b: str) -> int:
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] != b[i]) + abs(len(a)-len(b))

class Tool(QDialog):
    TITLE = "Phylogenetic Distance (Hamming toy)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Seq A:")); self.a = QLineEdit("ATGCCGTA"); r1.addWidget(self.a)
        r1.addWidget(QLabel("Seq B:")); self.b = QLineEdit("ATGACGTT"); r1.addWidget(self.b)
        lay.addLayout(r1)

        self.result = QLabel("Toy metric for demonstration."); lay.addWidget(self.result)
        btn = QPushButton("Compute distance"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            A = self.a.text().strip().upper().replace(" ", "")
            B = self.b.text().strip().upper().replace(" ", "")
            if not A or not B: raise ValueError("Both sequences required")
            d = hamming(A, B)
            self.result.setText(f"Hamming distance = {d}")
            add_log_entry(self.TITLE, action="Compute", data={"A": A, "B": B, "Hamming": d})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
