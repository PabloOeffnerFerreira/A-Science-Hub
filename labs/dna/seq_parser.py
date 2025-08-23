
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFileDialog
from Bio import SeqIO
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Sequence File Parser"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        self.setMinimumHeight(350)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Open a FASTA or GenBank file:"))
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)
        btn = QPushButton("Open File")
        btn.clicked.connect(self.open_file)
        layout.addWidget(btn)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open FASTA/GenBank File", "",
                                              "FASTA/GenBank (*.fasta *.fa *.gb *.gbk)")
        if path:
            try:
                try:
                    records = list(SeqIO.parse(path, "fasta"))
                    if not records:
                        raise ValueError("No FASTA records")
                except Exception:
                    records = list(SeqIO.parse(path, "genbank"))
                text = []
                for rec in records:
                    text.append(f"ID: {rec.id}\nLength: {len(rec.seq)}\nSequence:\n{rec.seq}\n{'-'*30}\n")
                out = "".join(text)
                self.result.setText(out)
                add_log_entry("Seq Parser", action="Parse",
                              data={"file": path, "records": len(records)},
                              tags=["bio", "seqio"])
            except Exception as e:
                self.result.setText(f"Error: {e}")
                add_log_entry("Seq Parser", action="Error",
                              data={"file": path, "error": str(e)})
