
from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QApplication, QFileDialog
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from core.data.functions.bio_utils import CODON_TABLE, AMINO_ACID_GROUPS
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Codon Lookup"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520); self.setWindowTitle(self.TITLE)
        lay = QVBoxLayout(self)

        lay.addWidget(QLabel("Enter RNA Codon (e.g., AUG):"))
        self.entry = QLineEdit(); self.entry.setPlaceholderText("AUG, UUU, GGA …"); lay.addWidget(self.entry)

        row = QHBoxLayout()
        self.lookup_btn = QPushButton("Lookup"); row.addWidget(self.lookup_btn)
        self.copy_btn = QPushButton("Copy"); row.addWidget(self.copy_btn)
        self.export_btn = QPushButton("Export Chart…"); row.addWidget(self.export_btn)
        lay.addLayout(row)

        self.out = QTextEdit(); self.out.setReadOnly(True); lay.addWidget(self.out)

        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.canvas = FigureCanvas(self.fig); lay.addWidget(self.canvas)

        self.lookup_btn.clicked.connect(self._lookup)
        self.copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.out.toPlainText()))
        self.export_btn.clicked.connect(self._export)

    def _lookup(self):
        codon = self.entry.text().strip().upper()
        if len(codon) != 3 or any(c not in "AUGC" for c in codon):
            self._err("Codon must be exactly 3 of A,U,G,C."); return
        aa = CODON_TABLE.get(codon)
        if aa is None:
            self._err(f"Unknown codon: {codon}"); return
        group = AMINO_ACID_GROUPS.get(aa, "Unknown")
        self.out.setPlainText(f"Codon: {codon}\nAmino acid: {aa}\nGroup: {group}")
        self._plot_group_highlight(group)
        add_log_entry(self.TITLE, action="Lookup", data={"codon": codon, "aa": aa, "group": group})

    def _plot_group_highlight(self, target_group: str):
        self.fig.clear(); ax = self.fig.add_subplot(111)
        groups = ["Hydrophobic", "Polar", "Charged", "Stop Codon"]
        counts = {g: 0 for g in groups}
        for aa in CODON_TABLE.values():
            g = AMINO_ACID_GROUPS.get(aa, "Unknown")
            if g in counts: counts[g] += 1
        sizes = [counts[g] for g in groups]
        explode = [0.12 if g == target_group else 0.0 for g in groups]
        ax.pie(sizes, labels=groups, explode=explode, autopct="%1.1f%%", startangle=140)
        ax.set_title("Amino Acid Group Distribution"); self.canvas.draw()

    def _export(self):
        try:
            path = export_figure(self.fig)
            self.out.append(f"\n[Chart saved to: {path}]")
            add_log_entry(self.TITLE, action="ExportChart", data={"path": str(path)})
        except Exception as e:
            self._err(str(e))

    def _err(self, msg: str):
        self.out.setPlainText(f"Error: {msg}")
        add_log_entry(self.TITLE, action="Error", data={"msg": msg})
