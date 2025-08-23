
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from Bio.SeqUtils import gc_fraction
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "GC Content Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter DNA sequence:"))
        self.seq_entry = QLineEdit()
        layout.addWidget(self.seq_entry)
        self.result = QLabel("")
        layout.addWidget(self.result)
        btn = QPushButton("Compute")
        btn.clicked.connect(self.compute)
        layout.addWidget(btn)

    def compute(self):
        seq = self.seq_entry.text().strip().upper()
        try:
            gc = gc_fraction(seq) * 100
            msg = f"GC Content: {gc:.2f}%"
            self.result.setText(msg)
            add_log_entry("GC Content", action="Compute",
                          data={"input": seq, "gc_percent": gc},
                          tags=["bio", "dna"])
        except Exception as e:
            self.result.setText(f"Error: {e}")
            add_log_entry("GC Content", action="Error",
                          data={"input": seq, "error": str(e)})
