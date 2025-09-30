
from __future__ import annotations
import re
from typing import Dict, List, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QCheckBox, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.log import add_log_entry
from core.data.databases.codon_table import CODON_TABLE
from core.data.functions.bio_utils import AA1

def _sanitize_dna(s: str) -> str:
    s = re.sub(r"\s+", "", s).upper().replace("U", "T")
    s = re.sub(r"[^ACGTRYSWKMBDHVN]", "", s)
    return s

def _rc_dna(s: str) -> str:
    comp = str.maketrans("ACGTRYSWKMBDHVN", "TGCAYRSWMKVHDBN")
    return s.translate(comp)[::-1]

def _to_aa(codon: str) -> str:
    aa3 = CODON_TABLE.get(codon)
    if aa3 is None:
        return "X"
    if aa3 == "STOP":
        return "*"
    return AA1.get(aa3, "X")

def translate_linear(dna: str, frame_offset: int, stop_at_first: bool) -> Tuple[str, List[Tuple[int, int, str]]]:
    """Return AA string and list of (start_nt, end_nt, aa_one) for every codon in this frame."""
    rna = dna.replace("T", "U")
    aa: List[str] = []
    codons: List[Tuple[int, int, str]] = []
    for i in range(frame_offset, len(rna) - 2, 3):
        codon = rna[i:i+3]
        one = _to_aa(codon)
        aa.append(one)
        codons.append((i, i+3, one))
        if stop_at_first and one == "*":
            break
    return "".join(aa), codons

def translate_orfs(dna: str, frame_offset: int) -> List[Tuple[int, int, str]]:
    """Return list of ORFs as (start_nt, end_nt, aa_string) starting at AUG and ending at stop."""
    rna = dna.replace("T", "U")
    out: List[Tuple[int, int, str]] = []
    i = frame_offset
    while i <= len(rna) - 3:
        codon = rna[i:i+3]
        if codon == "AUG":
            aa: List[str] = ["M"]
            j = i + 3
            stop_found = False
            while j <= len(rna) - 3:
                c = rna[j:j+3]
                a = _to_aa(c)
                if a == "*":
                    stop_found = True
                    j += 3
                    break
                aa.append(a if a != "X" else "X")
                j += 3
            if stop_found:
                out.append((i, j, "".join(aa)))
                i = j  # continue after this ORF
            else:
                # No stop; treat as open-ended ORF
                out.append((i, len(rna) - (len(rna) - i) % 3, "".join(aa)))
                break
        else:
            i += 3
    return out

class Tool(QDialog):
    TITLE = "Frame Translation (with visualisation)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(900)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Paste DNA sequence (A/T/C/G; IUPAC allowed, U→T handled):"))
        self.seq = QTextEdit(); self.seq.setFixedHeight(120); root.addWidget(self.seq)

        opts = QHBoxLayout()
        self.stop_cb = QCheckBox("Stop at first stop (*)"); self.stop_cb.setChecked(False); opts.addWidget(self.stop_cb)
        self.orf_cb = QCheckBox("ORF mode (start at AUG, stop at stop)"); self.orf_cb.setChecked(False); opts.addWidget(self.orf_cb)  # default OFF
        self.rev_cb = QCheckBox("Include reverse-complement frames (−1..−3)"); self.rev_cb.setChecked(True); opts.addWidget(self.rev_cb)
        self.show_letters_cb = QCheckBox("Show amino-acid letters"); self.show_letters_cb.setChecked(True); opts.addWidget(self.show_letters_cb)
        root.addLayout(opts)

        self.run = QPushButton("Translate & Visualise"); root.addWidget(self.run)

        self.out = QTextEdit(); self.out.setReadOnly(True); root.addWidget(self.out, 1)

        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(NavigationToolbar(self.canvas, self))
        root.addWidget(self.canvas, 2)

        self.run.clicked.connect(self._run)

    def _render_tracks(self, dna: str, include_rev: bool, orf_mode: bool, stop_first: bool, show_letters: bool):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        L = len(dna)
        y_tracks: List[float] = []
        labels: List[str] = []

        # Forward frames +1..+3 at y=2.5,1.5,0.5
        for idx, f in enumerate((0,1,2)):
            y = 2.5 - idx
            y_tracks.append(y); labels.append(f"+{f+1}")
            drawn = False
            if orf_mode:
                for s,e,aa in translate_orfs(dna, f):
                    ax.add_patch(self._rect(s, e, y, colour="#77dd77"))
                    if show_letters:
                        self._label_aa(ax, aa, s, e, y)
                    drawn = True
            if (not orf_mode) or (orf_mode and not drawn):
                # Fallback: draw all codons so the track isn't empty
                aa, codons = translate_linear(dna, f, stop_first)
                for s,e,one in codons:
                    col = "#77dd77" if one == "M" else ("#ff6961" if one == "*" else "#c7cdd7")
                    ax.add_patch(self._rect(s, e, y, colour=col))
                    if show_letters and one not in ("*",):
                        ax.text((s+e)/2, y, one, ha="center", va="center", fontsize=8)

        # Reverse frames -1..-3 at y=-0.5,-1.5,-2.5
        if include_rev:
            rc = _rc_dna(dna)
            for idx, f in enumerate((0,1,2)):
                y = -0.5 - idx
                y_tracks.append(y); labels.append(f"-{f+1}")
                drawn = False
                if orf_mode:
                    for s,e,aa in translate_orfs(rc, f):
                        fs = L - e; fe = L - s
                        ax.add_patch(self._rect(fs, fe, y, colour="#77dd77"))
                        if show_letters:
                            self._label_aa(ax, aa, fs, fe, y)
                        drawn = True
                if (not orf_mode) or (orf_mode and not drawn):
                    aa, codons = translate_linear(rc, f, stop_first)
                    for s,e,one in codons:
                        fs = L - e; fe = L - s
                        col = "#77dd77" if one == "M" else ("#ff6961" if one == "*" else "#c7cdd7")
                        ax.add_patch(self._rect(fs, fe, y, colour=col))
                        if show_letters and one not in ("*",):
                            ax.text((fs+fe)/2, y, one, ha="center", va="center", fontsize=8)

        # Ruler and aesthetics
        ax.set_xlim(0, L if L > 0 else 1)
        ax.set_ylim(-3.2, 3.2)
        ax.set_yticks(y_tracks, labels)
        ax.set_xlabel("Nucleotide position (0-based)")
        ax.grid(True, axis="x", alpha=0.25, linewidth=0.6)
        for spine in ("top","right"):
            ax.spines[spine].set_visible(False)

        self.fig.tight_layout()
        self.canvas.draw()

    def _rect(self, s: int, e: int, y: float, colour: str):
        from matplotlib.patches import Rectangle
        h = 0.8
        return Rectangle((s, y - h/2), max(0.001, e - s), h, linewidth=0.6, edgecolor="k", facecolor=colour, alpha=0.85)

    def _label_aa(self, ax, aa: str, s: int, e: int, y: float):
        # Place letters evenly across span
        span = e - s
        if span <= 0 or not aa:
            return
        step = span / max(1, len(aa))
        x = s + step / 2
        for ch in aa:
            if ch != "*":
                ax.text(x, y, ch, ha="center", va="center", fontsize=8)
            x += step

    def _run(self):
        raw = self.seq.toPlainText()
        dna = _sanitize_dna(raw)
        if not dna or len(dna) < 3:
            self.out.setPlainText("Sequence too short (need ≥ 3 bases).")
            return

        stop_first = self.stop_cb.isChecked()
        orf_mode = self.orf_cb.isChecked()
        include_rev = self.rev_cb.isChecked()
        show_letters = self.show_letters_cb.isChecked()

        # Text summary (forward frames only for brevity)
        lines = []
        if orf_mode:
            for f in range(3):
                orfs = translate_orfs(dna, f)
                if orfs:
                    aa_strs = [aa for _,_,aa in orfs]
                    lines.append(f"Frame +{f+1}: " + "  |  ".join(aa_strs))
                else:
                    lines.append(f"Frame +{f+1}: (no ORF)")
        else:
            for f in range(3):
                aa, _ = translate_linear(dna, f, stop_first)
                lines.append(f"Frame +{f+1}: {aa}")

        self.out.setPlainText("\n".join(lines))

        # Visual
        self._render_tracks(dna, include_rev, orf_mode, stop_first, show_letters)

        add_log_entry(self.TITLE, action="Translate", data={
            "len": len(dna),
            "stop_first": stop_first,
            "orf_mode": orf_mode,
            "include_rev": include_rev,
            "show_letters": show_letters
        })
