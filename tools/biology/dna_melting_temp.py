from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "DNA Melting Temperature (Tm)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(680)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Sequence (DNA):")); self.seq = QLineEdit("ATGCGCGATATATGC"); r0.addWidget(self.seq)
        lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Na⁺ (mM):")); self.na = QLineEdit("50"); r1.addWidget(self.na)
        r1.addWidget(QLabel("Method:")); self.meth = QComboBox(); self.meth.addItems(["Wallace (<14 nt)", "Basic (>14 nt)"]); r1.addWidget(self.meth)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute Tm"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            s = self.seq.text().strip().upper().replace(" ", "")
            if not s or any(c not in "ATGC" for c in s): raise ValueError("DNA must contain only A,T,G,C")
            A = s.count("A"); T = s.count("T"); G = s.count("G"); C = s.count("C"); N = len(s)
            na_mM = float(self.na.text()); 
            if na_mM <= 0: raise ValueError("Na+ > 0")
            if self.meth.currentText().startswith("Wallace") and N <= 13:
                Tm = 2*(A+T) + 4*(G+C)
            else:
                Tm = 64.9 + 41*(G+C - 16.4)/N + 16.6 * (na_mM/1000.0)  # crude salt correction
            self.result.setText(f"Tm ≈ {Tm:.2f} °C  (N={N}, GC%={(G+C)/N*100:.1f}%)")
            add_log_entry(self.TITLE, action="Compute", data={"seq_len": N, "A": A, "T": T, "G": G, "C": C, "Na_mM": na_mM, "Tm_C": Tm})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "DNA Melting Temperature (Tm)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(680)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Sequence (DNA):")); self.seq = QLineEdit("ATGCGCGATATATGC"); r0.addWidget(self.seq)
        lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Na⁺ (mM):")); self.na = QLineEdit("50"); r1.addWidget(self.na)
        r1.addWidget(QLabel("Method:")); self.meth = QComboBox(); self.meth.addItems(["Wallace (<14 nt)", "Basic (>14 nt)"]); r1.addWidget(self.meth)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute Tm"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            s = self.seq.text().strip().upper().replace(" ", "")
            if not s or any(c not in "ATGC" for c in s): raise ValueError("DNA must contain only A,T,G,C")
            A = s.count("A"); T = s.count("T"); G = s.count("G"); C = s.count("C"); N = len(s)
            na_mM = float(self.na.text()); 
            if na_mM <= 0: raise ValueError("Na+ > 0")
            if self.meth.currentText().startswith("Wallace") and N <= 13:
                Tm = 2*(A+T) + 4*(G+C)
            else:
                Tm = 64.9 + 41*(G+C - 16.4)/N + 16.6 * (na_mM/1000.0)  # crude salt correction
            self.result.setText(f"Tm ≈ {Tm:.2f} °C  (N={N}, GC%={(G+C)/N*100:.1f}%)")
            add_log_entry(self.TITLE, action="Compute", data={"seq_len": N, "A": A, "T": T, "G": G, "C": C, "Na_mM": na_mM, "Tm_C": Tm})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
