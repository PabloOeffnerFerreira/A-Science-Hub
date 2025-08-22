# This file must be improved. It's just some text input - text output tool, and has no real visualization or advanced features.
# It will be replaced with a more advanced tool that can handle complex functions, provide better error handling,
# and allow for more customization of the plot. The UI will also be improved to make it more user-friendly.

from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Ferromagnetism Helper"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(700)
        lay = QVBoxLayout(self)

        r = QHBoxLayout()
        r.addWidget(QLabel("Curie temperature T_c (K):")); self.tc = QLineEdit("770"); r.addWidget(self.tc)
        r.addWidget(QLabel("M₀ (arb.):")); self.m0 = QLineEdit("1.0"); r.addWidget(self.m0)
        r.addWidget(QLabel("Max T (K):")); self.tmax = QLineEdit("1000"); r.addWidget(self.tmax)
        lay.addLayout(r)

        self.fig = Figure(figsize=(7,4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas, 1)

        b = QHBoxLayout(); self.btn_plot = QPushButton("Plot"); b.addWidget(self.btn_plot); self.btn_export = QPushButton("Export Image…"); b.addWidget(self.btn_export); lay.addLayout(b)

        self.btn_plot.clicked.connect(self._plot)
        self.btn_export.clicked.connect(lambda: export_figure(self.fig))

    def _plot(self):
        try:
            Tc = float(self.tc.text()); M0 = float(self.m0.text()); Tmax = float(self.tmax.text())
            if Tc<=0 or M0<=0 or Tmax<=0: raise ValueError("positive")
            T = np.linspace(0, Tmax, 500)
            beta = 0.33
            M = np.where(T<Tc, M0*(1 - T/Tc)**beta, 0.0)
            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.plot(T, M, label=f"T_c={Tc}")
            ax.set_xlabel("Temperature (K)"); ax.set_ylabel("Magnetisation (arb.)"); ax.set_title("Ferromagnetism: M vs T"); ax.grid(True, alpha=0.3); ax.legend(loc="best")
            self.fig.tight_layout(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Plot", data={"Tc": Tc, "M0": M0, "Tmax": Tmax})
        except Exception as e:
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
