
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QSizePolicy
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

MU0 = 4e-7 * np.pi  # vacuum permeability

class Tool(QDialog):
    TITLE = "Magnetic Field Calculator (wire / loop / solenoid)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        # Top row: geometry
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Geometry:"))
        self.geom = QComboBox(); self.geom.addItems(["Infinite straight wire", "Circular loop (on-axis)", "Long solenoid (on-axis)"])
        row1.addWidget(self.geom)
        lay.addLayout(row1)

        # Inputs row
        self.i = QLineEdit("5.0"); self.i.setPlaceholderText("Current I (A)")
        self.r = QLineEdit("0.05"); self.r.setPlaceholderText("r (m)  [wire: radial distance; loop: loop radius; solenoid: coil radius]")
        self.n = QLineEdit("500"); self.n.setPlaceholderText("N (turns) [loop/solenoid]")
        self.L = QLineEdit("0.4"); self.L.setPlaceholderText("Length L (m) [solenoid only]")
        inp = QHBoxLayout()
        for w in (QLabel("I:"), self.i, QLabel("r:"), self.r, QLabel("N:"), self.n, QLabel("L:"), self.L):
            inp.addWidget(w)
        lay.addLayout(inp)

        # Range for plots
        rng = QHBoxLayout()
        self.xmin = QLineEdit("0.0"); self.xmin.setPlaceholderText("x_min (m)")
        self.xmax = QLineEdit("0.2"); self.xmax.setPlaceholderText("x_max (m)")
        rng.addWidget(QLabel("Plot range along axis / radius:")); rng.addWidget(self.xmin); rng.addWidget(self.xmax)
        lay.addLayout(rng)

        # Buttons
        b = QHBoxLayout()
        self.btn_calc = QPushButton("Compute / Plot"); b.addWidget(self.btn_calc)
        self.btn_export = QPushButton("Export Image…"); b.addWidget(self.btn_export)
        lay.addLayout(b)

        # Figure
        self.fig = Figure(figsize=(7,4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas, 1)

        self.btn_calc.clicked.connect(self._plot)
        self.btn_export.clicked.connect(lambda: export_figure(self.fig))

    def _plot(self):
        try:
            geom = self.geom.currentText()
            I = float(self.i.text())
            r = float(self.r.text())

            xmin = float(self.xmin.text())
            xmax = float(self.xmax.text())
            if xmax <= xmin:
                xmin, xmax = 0.0, max(0.1, abs(r)*4)

            xs = np.linspace(xmin, xmax, 400)
            ys = None
            label = ""

            if geom == "Infinite straight wire":
                # B(r) = mu0 I / (2π r)
                rr = np.clip(xs, 1e-6, None)
                ys = MU0 * I / (2*np.pi*rr)
                label = "B(r) around straight wire"

            elif geom == "Circular loop (on-axis)":
                # B(x) = mu0 I R^2 / (2 (R^2 + x^2)^(3/2))  for single turn
                R = r
                N = max(1, int(float(self.n.text()) if self.n.text().strip() else 1))
                denom = (R*R + xs*xs)**1.5
                ys = MU0 * I * R*R / (2*denom) * N
                label = f"B(x) along axis of loop (R={R} m, N={N})"

            else:  # Long solenoid (on-axis, near the centre)
                # Approx uniform interior field: B ≈ mu0 * n * I, where n = N / L
                N = float(self.n.text()) if self.n.text().strip() else 100.0
                L = float(self.L.text()) if self.L.text().strip() else 0.5
                n_turns_per_m = N / max(L, 1e-6)
                ys = np.ones_like(xs) * MU0 * n_turns_per_m * I
                label = f"B (centre) of long solenoid (N={N}, L={L} m)"

            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.plot(xs, ys)
            ax.set_xlabel("x (m) [axis or radial distance]")
            ax.set_ylabel("B (tesla)")
            ax.set_title(label)
            ax.grid(True, alpha=0.3)
            self.fig.tight_layout(); self.canvas.draw()

            add_log_entry(self.TITLE, action="Plot", data={
                "geom": geom, "I": I, "r": r, "N": self.n.text(), "L": self.L.text(), "xmin": xmin, "xmax": xmax
            })
        except Exception as e:
            # keep quiet visually; you can add a label if you want
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
