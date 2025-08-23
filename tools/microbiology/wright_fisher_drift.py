from __future__ import annotations
import random
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Wright–Fisher Genetic Drift (Allele p)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Population size N (haploid):")); self.N = QLineEdit("100"); r1.addWidget(self.N)
        r1.addWidget(QLabel("Initial p (0..1):")); self.p0 = QLineEdit("0.5"); r1.addWidget(self.p0)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Generations:")); self.gens = QLineEdit("50"); r2.addWidget(self.gens)
        r2.addWidget(QLabel("Trials (avg):")); self.trials = QLineEdit("1"); r2.addWidget(self.trials)
        lay.addLayout(r2)

        self.result = QLabel("Educational model only."); lay.addWidget(self.result)
        btn = QPushButton("Simulate"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            N = int(float(self.N.text())); p = float(self.p0.text())
            G = int(float(self.gens.text())); T = int(float(self.trials.text()))
            if N <= 0 or not (0 <= p <= 1) or G < 0 or T <= 0: raise ValueError("Invalid inputs")
            p_sum = 0.0
            for _ in range(T):
                cur = p
                for _ in range(G):
                    k = sum(1 for _ in range(N) if random.random() < cur)
                    cur = k / N
                p_sum += cur
            p_avg = p_sum / T
            self.result.setText(f"Mean allele frequency after {G} gen ≈ {p_avg:.4f}")
            add_log_entry(self.TITLE, action="Sim", data={"N": N, "p0": p, "G": G, "trials": T, "p_end_avg": p_avg})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
