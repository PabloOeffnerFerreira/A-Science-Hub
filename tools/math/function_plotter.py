# Todo: I will add a more advanced function plotter later, this is just a simple one.
# It will handle more complex functions, provide better error handling, and allow for more customization of the plot.
# The UI will also be improved to make it more user-friendly.

from __future__ import annotations
import numpy as np
import sympy as sp
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Function Plotter"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Enter function of x (e.g., x**2 + 3*x - 2):"))
        self.entry = QLineEdit(); lay.addWidget(self.entry)

        r = QHBoxLayout()
        self.xmin = QLineEdit(); self.xmin.setPlaceholderText("xmin (default -10)")
        self.xmax = QLineEdit(); self.xmax.setPlaceholderText("xmax (default 10)")
        r.addWidget(self.xmin); r.addWidget(self.xmax)
        lay.addLayout(r)

        b = QHBoxLayout()
        self.plot_btn = QPushButton("Plot"); b.addWidget(self.plot_btn)
        self.save_btn = QPushButton("Export Image…"); b.addWidget(self.save_btn)
        lay.addLayout(b)

        self.fig = Figure(figsize=(5,4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self))
        lay.addWidget(self.canvas, 1)

        self.plot_btn.clicked.connect(self._plot)
        self.save_btn.clicked.connect(self._save)

    def _plot(self):
        expr_txt = self.entry.text().strip()
        try:
            x = sp.symbols('x')
            expr = sp.sympify(expr_txt)
            f = sp.lambdify(x, expr, "numpy")
            try:
                xmin = float(self.xmin.text()) if self.xmin.text().strip() else -10.0
                xmax = float(self.xmax.text()) if self.xmax.text().strip() else 10.0
            except Exception:
                xmin, xmax = -10.0, 10.0
            if xmin >= xmax: xmin, xmax = -10.0, 10.0
            xs = np.linspace(xmin, xmax, 1000)
            ys = f(xs)

            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.plot(xs, ys)
            ax.set_title(f"y = {expr_txt}")
            ax.set_xlabel("x"); ax.set_ylabel("y"); ax.grid(True)
            self.fig.tight_layout(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Plot", data={"expr": expr_txt, "xmin": xmin, "xmax": xmax})
        except Exception as e:
            self.fig.clear(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Error", data={"expr": expr_txt, "msg": str(e)})

    def _save(self):
        try:
            path = export_figure(self.fig)
            add_log_entry(self.TITLE, action="ExportImage", data={"path": str(path)})
        except Exception as e:
            add_log_entry(self.TITLE, action="ExportError", data={"msg": str(e)})
