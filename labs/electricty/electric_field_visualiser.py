
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

K = 8.9875517923e9

class Tool(QDialog):
    TITLE = "Electric Field Visualiser (two charges)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("q1 (C):")); self.q1 = QLineEdit("5e-6"); r1.addWidget(self.q1)
        r1.addWidget(QLabel("x1 (m):")); self.x1 = QLineEdit("-0.2"); r1.addWidget(self.x1)
        r1.addWidget(QLabel("y1 (m):")); self.y1 = QLineEdit("0.0"); r1.addWidget(self.y1)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("q2 (C):")); self.q2 = QLineEdit("-5e-6"); r2.addWidget(self.q2)
        r2.addWidget(QLabel("x2 (m):")); self.x2 = QLineEdit("0.2"); r2.addWidget(self.x2)
        r2.addWidget(QLabel("y2 (m):")); self.y2 = QLineEdit("0.0"); r2.addWidget(self.y2)
        lay.addLayout(r2)

        rng = QHBoxLayout()
        rng.addWidget(QLabel("Plot half-width (m):")); self.H = QLineEdit("0.6"); rng.addWidget(self.H)
        rng.addWidget(QLabel("Grid (n x n):")); self.N = QLineEdit("25"); rng.addWidget(self.N)
        lay.addLayout(rng)

        b = QHBoxLayout(); self.btn_plot = QPushButton("Plot field"); b.addWidget(self.btn_plot); self.btn_export = QPushButton("Export Image…"); b.addWidget(self.btn_export); lay.addLayout(b)

        self.fig = Figure(figsize=(7.2, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas, 1)

        self.btn_plot.clicked.connect(self._plot)
        self.btn_export.clicked.connect(lambda: export_figure(self.fig))

    def _E(self, q, xq, yq, X, Y):
        dx = X - xq; dy = Y - yq
        r2 = dx*dx + dy*dy
        r = np.sqrt(r2) + 1e-12
        Ex = K*q*dx/(r**3)
        Ey = K*q*dy/(r**3)
        return Ex, Ey

    def _plot(self):
        try:
            q1 = float(self.q1.text()); x1 = float(self.x1.text()); y1 = float(self.y1.text())
            q2 = float(self.q2.text()); x2 = float(self.x2.text()); y2 = float(self.y2.text())
            H = float(self.H.text()); N = int(float(self.N.text()))
            xs = np.linspace(-H, H, N); ys = np.linspace(-H, H, N)
            X, Y = np.meshgrid(xs, ys)

            E1x, E1y = self._E(q1, x1, y1, X, Y)
            E2x, E2y = self._E(q2, x2, y2, X, Y)
            Ex = E1x + E2x; Ey = E1y + E2y
            E = np.sqrt(Ex**2 + Ey**2)

            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.streamplot(X, Y, Ex, Ey, density=1.2, linewidth=1, arrowsize=1)
            # Potential-like map (not exact V, but |E| magnitude for reference)
            im = ax.imshow(np.log10(E+1e-12), extent=[-H, H, -H, H], origin="lower", alpha=0.3)
            ax.scatter([x1, x2], [y1, y2], s=80, c=["r","b"])
            ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)"); ax.set_title("Field lines (two point charges)")
            self.fig.colorbar(im, ax=ax, label="log10|E|")
            self.fig.tight_layout(); self.canvas.draw()

            add_log_entry(self.TITLE, action="Plot", data={"q1": q1, "q2": q2, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "H": H, "N": N})
        except Exception as e:
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
