
from __future__ import annotations
from typing import Tuple, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSpinBox
)
from PyQt6.QtGui import QFont
from core.data.functions.log import add_log_entry

def _nw_align(a: str, b: str, match: int = 1, mismatch: int = -1,
              gap_open: int = -2, gap_extend: int = -1) -> Tuple[str, str, int]:
    """Needleman–Wunsch with affine gaps, global alignment. Returns (aln_a, aln_b, score)."""
    a = a.strip().upper()
    b = b.strip().upper()
    n, m = len(a), len(b)
    NEG = -10**9

    # DP matrices
    M = [[NEG]*(m+1) for _ in range(n+1)]  # match/mismatch
    X = [[NEG]*(m+1) for _ in range(n+1)]  # gap in a (insert in b) -> a has letter, b has '-'
    Y = [[NEG]*(m+1) for _ in range(n+1)]  # gap in b (delete from a) -> a has '-', b has letter

    PM = [[-1]*(m+1) for _ in range(n+1)]
    PX = [[-1]*(m+1) for _ in range(n+1)]
    PY = [[-1]*(m+1) for _ in range(n+1)]

    M[0][0] = 0
    for i in range(1, n+1):
        X[i][0] = gap_open + (i-1)*gap_extend
        PX[i][0] = 1
    for j in range(1, m+1):
        Y[0][j] = gap_open + (j-1)*gap_extend
        PY[0][j] = 2

    for i in range(1, n+1):
        ai = a[i-1]
        for j in range(1, m+1):
            bj = b[j-1]
            s = match if ai == bj else mismatch

            # M
            m_candidates = ((M[i-1][j-1], 0), (X[i-1][j-1], 1), (Y[i-1][j-1], 2))
            best_m, ptr_m = max((v + s, p) for v, p in m_candidates)
            M[i][j], PM[i][j] = best_m, ptr_m

            # X (gap in a)
            open_x = M[i-1][j] + gap_open
            ext_x  = X[i-1][j] + gap_extend
            if open_x >= ext_x:
                X[i][j], PX[i][j] = open_x, 0
            else:
                X[i][j], PX[i][j] = ext_x, 1

            # Y (gap in b)
            open_y = M[i][j-1] + gap_open
            ext_y  = Y[i][j-1] + gap_extend
            if open_y >= ext_y:
                Y[i][j], PY[i][j] = open_y, 0
            else:
                Y[i][j], PY[i][j] = ext_y, 2

    # end
    end_choices = ((M[n][m], 0), (X[n][m], 1), (Y[n][m], 2))
    score, state = max(end_choices)

    # traceback
    i, j = n, m
    top: List[str] = []
    bot: List[str] = []
    while i > 0 or j > 0:
        if state == 0:  # M
            prev = PM[i][j]
            top.append(a[i-1]); bot.append(b[j-1])
            i -= 1; j -= 1; state = prev
        elif state == 1:  # X: gap in a -> b has '-'
            prev = PX[i][j]
            top.append(a[i-1]); bot.append('-')
            i -= 1; state = prev
        else:            # Y: gap in b -> a has '-'
            prev = PY[i][j]
            top.append('-'); bot.append(b[j-1])
            j -= 1; state = prev

    return ''.join(reversed(top)), ''.join(reversed(bot)), score

def pretty_alignment(a_aln: str, b_aln: str, score: int) -> str:
    mid = []
    for x, y in zip(a_aln, b_aln):
        if x == '-' or y == '-':
            mid.append(' ')
        elif x == y:
            mid.append('|')
        else:
            mid.append('.')
    return f"{a_aln}\n{''.join(mid)}\n{b_aln}\n  Score={score}"

class Tool(QDialog):
    TITLE = "Pairwise Alignment (NW, affine gaps)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(700)

        root = QVBoxLayout(self)

        # Inputs
        row1 = QHBoxLayout(); row1.addWidget(QLabel("Sequence A:")); self.a = QLineEdit(); row1.addWidget(self.a, 1); root.addLayout(row1)
        row2 = QHBoxLayout(); row2.addWidget(QLabel("Sequence B:")); self.b = QLineEdit(); row2.addWidget(self.b, 1); root.addLayout(row2)

        # Scoring
        scr = QHBoxLayout()
        scr.addWidget(QLabel("match:")); self.match = QSpinBox(); self.match.setRange(-10, 10); self.match.setValue(1); scr.addWidget(self.match)
        scr.addWidget(QLabel("mismatch:")); self.mismatch = QSpinBox(); self.mismatch.setRange(-10, 10); self.mismatch.setValue(-1); scr.addWidget(self.mismatch)
        scr.addWidget(QLabel("gap open:")); self.gap_open = QSpinBox(); self.gap_open.setRange(-50, 0); self.gap_open.setValue(-2); scr.addWidget(self.gap_open)
        scr.addWidget(QLabel("gap extend:")); self.gap_ext = QSpinBox(); self.gap_ext.setRange(-50, 0); self.gap_ext.setValue(-1); scr.addWidget(self.gap_ext)
        self.run = QPushButton("Align"); scr.addWidget(self.run)
        root.addLayout(scr)

        # Output
        self.out = QTextEdit(); self.out.setReadOnly(True); self.out.setFont(QFont("Consolas", 11))
        root.addWidget(self.out, 1)

        self.run.clicked.connect(self._do_align)

    def _do_align(self):
        a = self.a.text().strip().upper()
        b = self.b.text().strip().upper()
        if not a or not b:
            self.out.setPlainText("Enter both sequences."); return
        aln_a, aln_b, sc = _nw_align(a, b,
                                     match=self.match.value(),
                                     mismatch=self.mismatch.value(),
                                     gap_open=self.gap_open.value(),
                                     gap_extend=self.gap_ext.value())
        self.out.setPlainText(pretty_alignment(aln_a, aln_b, sc))
        add_log_entry(self.TITLE, action="Align", data={"len_a": len(a), "len_b": len(b), "score": sc})
