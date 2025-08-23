from __future__ import annotations
import re
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "CRISPR Guide Finder (SpCas9 NGG)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Sequence (DNA):")); self.seq = QLineEdit("ACGTACGTACGTGGTTACCGG..."); r0.addWidget(self.seq)
        lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Guide length (nt, typically 20):")); self.glen = QLineEdit("20"); r1.addWidget(self.glen)
        r1.addWidget(QLabel("Max results to display:")); self.maxn = QLineEdit("10"); r1.addWidget(self.maxn)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Find guides"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            s = self.seq.text().strip().upper().replace(" ", "")
            if not s or any(c not in "ATGC" for c in s): raise ValueError("DNA must contain only A,T,G,C")
            gl = int(float(self.glen.text()))
            maxn = int(float(self.maxn.text()))
            if gl <= 0 or maxn <= 0: raise ValueError("glen>0, max>0")
            # Find 20nt guides immediately upstream of NGG (3' PAM on forward strand)
            guides = []
            for m in re.finditer(r"(?=(GG))", s):  # capture PAM GG at positions m.start()..m.start()+1
                pam_start = m.start()
                guide_start = pam_start - gl
                if guide_start >= 0:
                    guide = s[guide_start:pam_start]
                    if len(guide) == gl:
                        guides.append((guide_start, guide, s[pam_start:pam_start+2]))
                if len(guides) >= maxn:
                    break
            self.result.setText(f"Found {len(guides)} guide(s): {guides if guides else '—'}")
            add_log_entry(self.TITLE, action="Find", data={"glen": gl, "max": maxn, "count": len(guides), "guides": guides})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
