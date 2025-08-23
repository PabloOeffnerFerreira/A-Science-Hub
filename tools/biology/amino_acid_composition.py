from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry
from core.data.functions.bio_utils import AA_MASS

class Tool(QDialog):
    TITLE = "Amino Acid Composition"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Protein sequence (AA letters):")); self.seq = QLineEdit("MGLSDGEWQLVLNVWGK..."); r0.addWidget(self.seq)
        lay.addLayout(r0)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Analyze"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            s = self.seq.text().strip().upper().replace(" ", "")
            if not s or any(c not in AA_MASS for c in s): raise ValueError("Invalid protein sequence")
            counts = {aa: 0 for aa in AA_MASS}
            for c in s: counts[c] += 1
            N = len(s)
            mw = sum(AA_MASS[c] for c in s) + 18.015  # add water mass once for termini (approx)
            top = sorted(((aa, counts[aa], 100*counts[aa]/N) for aa in counts if counts[aa] > 0), key=lambda x: -x[1])
            summary = ", ".join(f"{aa}:{cnt}({pct:.1f}%)" for aa, cnt, pct in top[:10])
            self.result.setText(f"Length={N}, MW≈{mw:.2f} Da; Top AAs: {summary}")
            add_log_entry(self.TITLE, action="Analyze", data={"length": N, "mw_approx_Da": mw, "counts": counts})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
