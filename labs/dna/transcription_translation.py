
from __future__ import annotations
import re
from collections import Counter
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog, QApplication
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry
from core.data.databases.codon_table

class Tool(QDialog):
    TITLE = "DNA Transcription & Translation"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        self.setWindowTitle(self.TITLE)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Enter DNA sequence:"))
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("A, T, C, G only (whitespace ignored)")
        lay.addWidget(self.entry)

        btn_row = QHBoxLayout()
        self.translate_btn = QPushButton("Translate")
        self.copy_btn = QPushButton("Copy Result")
        self.export_btn = QPushButton("Export Chart…")
        btn_row.addWidget(self.translate_btn); btn_row.addWidget(self.copy_btn); btn_row.addWidget(self.export_btn)
        lay.addLayout(btn_row)

        self.out = QTextEdit(); self.out.setReadOnly(True); lay.addWidget(self.out, 1)

        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.canvas = FigureCanvas(self.fig); lay.addWidget(self.canvas)

        self.translate_btn.clicked.connect(self._translate)
        self.copy_btn.clicked.connect(self._copy)
        self.export_btn.clicked.connect(self._export_chart)

        self._last_codons = []

    def _translate(self):
        raw = re.sub(r"\s+", "", self.entry.text().upper())
        if not raw or re.search(r"[^ATCG]", raw):
            self._err("DNA must contain only A,T,C,G."); return

        mrna = raw.replace("T", "U")
        codons = [mrna[i:i+3] for i in range(0, len(mrna) - 2, 3)]
        protein = [CODON_TABLE.get(c, "?") for c in codons]
        self._last_codons = codons

        text = f"mRNA:\n{mrna}\n\nProtein:\n" + "-".join(protein)
        self.out.setPlainText(text)

        self._plot_codon_usage(codons)
        add_log_entry(self.TITLE, action="Translate", data={"len": len(raw), "codons": len(codons)})

    def _plot_codon_usage(self, codons):
        self.fig.clear(); ax = self.fig.add_subplot(111)
        if not codons:
            self.canvas.draw(); return
        counts = Counter(codons)
        labels = sorted(counts)
        vals = [counts[c] for c in labels]
        ax.barh(labels, vals)
        ax.set_xlabel("Frequency"); ax.set_title("Codon Usage")
        self.fig.tight_layout(); self.canvas.draw()

    def _copy(self):
        QApplication.clipboard().setText(self.out.toPlainText())
        add_log_entry(self.TITLE, action="Copy")

    def _export_chart(self):
        try:
            path = export_figure(self.fig)
            self.out.append(f"\n[Chart saved to: {path}]")
            add_log_entry(self.TITLE, action="ExportChart", data={"path": str(path)})
        except Exception as e:
            self._err(f"Failed to export: {e}")

    def _err(self, msg: str):
        self.out.setPlainText(f"Error: {msg}")
        add_log_entry(self.TITLE, action="Error", data={"msg": msg})
