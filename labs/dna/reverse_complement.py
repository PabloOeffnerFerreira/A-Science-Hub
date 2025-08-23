
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from Bio.Seq import Seq
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Reverse Complement"

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
            rc = str(Seq(seq).reverse_complement())
            self.result.setText(f"Reverse Complement: {rc}")
            add_log_entry("Reverse Complement", action="Compute",
                          data={"input": seq, "result": rc},
                          tags=["bio", "dna"])
        except Exception as e:
            self.result.setText(f"Error: {e}")
            add_log_entry("Reverse Complement", action="Error",
                          data={"input": seq, "error": str(e)})
