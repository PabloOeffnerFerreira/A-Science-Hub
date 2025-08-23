from __future__ import annotations
import re
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry
from core.data.functions.bio_utils import SITES

class Tool(QDialog):
    TITLE = "Restriction Site Mapper"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Sequence (DNA):")); self.seq = QLineEdit("AAGAATTCTTGGATCCGCGGCCGC"); r0.addWidget(self.seq)
        lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Enzyme:")); self.enzyme = QComboBox(); self.enzyme.addItems(list(SITES.keys())); r1.addWidget(self.enzyme)
        r1.addWidget(QLabel("Custom site (if chosen):")); self.custom = QLineEdit(""); r1.addWidget(self.custom)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Find sites"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            s = self.seq.text().strip().upper().replace(" ", "")
            if not s or any(c not in "ATGC" for c in s): raise ValueError("DNA must contain only A,T,G,C")
            choice = self.enzyme.currentText()
            motif = SITES[choice] if choice != "Custom" else self.custom.text().strip().upper()
            if not motif or any(c not in "ATGC" for c in motif): raise ValueError("Invalid recognition site")
            # Find all overlapping matches
            positions = [m.start() for m in re.finditer(f"(?={motif})", s)]
            self.result.setText(f"Found {len(positions)} site(s) at positions: {positions if positions else '—'}")
            add_log_entry(self.TITLE, action="Scan", data={"enzyme": choice, "motif": motif, "count": len(positions), "positions": positions})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
