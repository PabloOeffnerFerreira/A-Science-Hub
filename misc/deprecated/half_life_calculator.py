
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.log import add_log_entry
from core.data.functions.geo_utils import half_life_decay

class Tool(QDialog):
    TITLE = "Half-life Calculator (Decay vs Time)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Initial quantity (N₀):")); self.n0 = QLineEdit(); lay.addWidget(self.n0)
        lay.addWidget(QLabel("Half-life (t½):")); self.hl = QLineEdit(); lay.addWidget(self.hl)
        lay.addWidget(QLabel("Total time span:")); self.tmax = QLineEdit(); lay.addWidget(self.tmax)
        self.result = QLabel(""); lay.addWidget(self.result)
        row = QHBoxLayout(); self.run = QPushButton("Compute"); row.addWidget(self.run); lay.addLayout(row)

        self.fig = Figure(figsize=(5,3), dpi=100)
        self.canvas = FigureCanvas(self.fig); lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas)

        self.run.clicked.connect(self._go)

    def _go(self):
        try:
            N0 = float(self.n0.text()); hl = float(self.hl.text()); T = float(self.tmax.text())
            if hl <= 0 or T <= 0: raise ValueError
            t = np.linspace(0, T, 400)
            y = [half_life_decay(N0, ti, hl) for ti in t]
            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.plot(t, y); ax.set_xlabel("Time"); ax.set_ylabel("Quantity"); ax.grid(True, alpha=0.3)
            self.fig.tight_layout(); self.canvas.draw()
            self.result.setText(f"N(T) = {y[-1]:.6g}")
            add_log_entry(self.TITLE, action="Compute", data={"N0": N0, "hl": hl, "T": T, "NT": y[-1]})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
