
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Magnetic Flux & Induction (Faraday)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("N (turns):")); self.N = QLineEdit("200"); row.addWidget(self.N)
        row.addWidget(QLabel("Area A (m²):")); self.A = QLineEdit("0.01"); row.addWidget(self.A)
        row.addWidget(QLabel("dB/dt (T/s):")); self.dBdt = QLineEdit("0.5"); row.addWidget(self.dBdt)
        lay.addLayout(row)

        # Time profile for B(t)
        prof = QHBoxLayout()
        prof.addWidget(QLabel("Profile:"))
        self.profile = QComboBox(); self.profile.addItems(["Linear B(t)=B0 + k t", "Sinusoidal B(t)=B0+ΔB sin(ω t)"])
        prof.addWidget(self.profile)
        self.B0 = QLineEdit("0.0"); self.dB = QLineEdit("0.2"); self.omega = QLineEdit("50.0")
        prof.addWidget(QLabel("B0:")); prof.addWidget(self.B0)
        prof.addWidget(QLabel("ΔB:")); prof.addWidget(self.dB)
        prof.addWidget(QLabel("ω (rad/s):")); prof.addWidget(self.omega)
        lay.addLayout(prof)

        rng = QHBoxLayout()
        self.tmax = QLineEdit("2.0"); rng.addWidget(QLabel("t_max (s):")); rng.addWidget(self.tmax)
        lay.addLayout(rng)

        b = QHBoxLayout()
        self.btn_plot = QPushButton("Plot EMF"); b.addWidget(self.btn_plot)
        self.btn_export = QPushButton("Export Image…"); b.addWidget(self.btn_export)
        lay.addLayout(b)

        self.fig = Figure(figsize=(7.2, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas, 1)

        self.btn_plot.clicked.connect(self._plot)
        self.btn_export.clicked.connect(lambda: export_figure(self.fig))

    def _plot(self):
        try:
            N = float(self.N.text()); A = float(self.A.text()); tmax = float(self.tmax.text())
            t = np.linspace(0, tmax, 800)

            if self.profile.currentText().startswith("Linear"):
                B0 = float(self.B0.text()); k = float(self.dBdt.text())
                B = B0 + k*t
                emf = -N * A * (np.gradient(B, t))
                title = f"EMF for linear B(t) with dB/dt={k} T/s"
            else:
                B0 = float(self.B0.text()); dB = float(self.dB.text()); w = float(self.omega.text())
                B = B0 + dB*np.sin(w*t)
                emf = -N * A * (np.gradient(B, t))
                title = f"EMF for sinusoidal B(t) with ΔB={dB}, ω={w}"

            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.plot(t, emf, label="EMF (V)")
            ax.set_xlabel("t (s)"); ax.set_ylabel("EMF (V)"); ax.set_title(title)
            ax.grid(True, alpha=0.3); ax.legend(loc="best")
            self.fig.tight_layout(); self.canvas.draw()

            add_log_entry(self.TITLE, action="PlotEMF", data={
                "N": N, "A": A, "profile": self.profile.currentText(), "B0": self.B0.text(), "dBdt/ΔB": self.dBdt.text() or self.dB.text(), "omega": self.omega.text(), "tmax": tmax
            })
        except Exception as e:
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
