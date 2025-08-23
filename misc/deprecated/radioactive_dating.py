
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.log import add_log_entry
from core.data.functions.geo_utils import half_life_decay, estimate_age_from_remaining

PRESETS = [
    ("Carbon-14", 5730.0),
    ("Potassium-40", 1.248e9),
    ("Uranium-235", 7.038e8),
    ("Uranium-238", 4.468e9),
    ("Rubidium-87", 4.88e10),
]

class Tool(QDialog):
    TITLE = "Radioactive Dating"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Half-life (years):"))
        self.h = QLineEdit(); lay.addWidget(self.h)
        lay.addWidget(QLabel("Remaining (%) [0–100]:"))
        self.p = QLineEdit(); lay.addWidget(self.p)
        row = QHBoxLayout()
        self.run = QPushButton("Estimate Age"); row.addWidget(self.run)
        self.decay_plot = QPushButton("Plot Decay Curve"); row.addWidget(self.decay_plot)
        lay.addLayout(row)

        # Presets
        row2 = QHBoxLayout(); row2.addWidget(QLabel("Presets:"))
        for name, hl in PRESETS:
            b = QPushButton(name); b.clicked.connect(lambda _, v=hl: self.h.setText(str(v))); row2.addWidget(b)
        lay.addLayout(row2)

        self.result = QLabel(""); lay.addWidget(self.result)

        self.fig = Figure(figsize=(5,3), dpi=100)
        self.canvas = FigureCanvas(self.fig); lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas)

        self.run.clicked.connect(self._estimate)
        self.decay_plot.clicked.connect(self._plot)

    def _estimate(self):
        try:
            half_life = float(self.h.text())
            pct = float(self.p.text())
            age = estimate_age_from_remaining(pct/100.0, half_life)
            self.result.setText(f"Estimated age: {age:,.3g} years")
            add_log_entry(self.TITLE, action="Estimate", data={"half_life": half_life, "remaining_pct": pct, "age": age})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})

    def _plot(self):
        try:
            half_life = float(self.h.text())
        except Exception:
            self.result.setText("Enter a valid half-life first."); return
        import numpy as np
        self.fig.clear(); ax = self.fig.add_subplot(111)
        t = np.linspace(0, 10*half_life, 400)
        y = (0.5) ** (t / half_life)
        ax.plot(t, y); ax.set_xlabel("Time (years)"); ax.set_ylabel("Fraction remaining")
        ax.set_title("Exponential Decay"); ax.grid(True, alpha=0.3)
        self.fig.tight_layout(); self.canvas.draw()
        add_log_entry(self.TITLE, action="PlotDecay", data={"half_life": half_life})
