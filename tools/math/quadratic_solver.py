from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGridLayout, QCheckBox, QSpinBox, QMessageBox, QSizePolicy
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from core.data.functions.log import add_log_entry
from core.data.functions.image_export import export_figure
try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


@dataclass
class QuadResult:
    roots: Tuple[complex, complex]
    vertex: Tuple[float, float]
    axis: float
    discriminant: float


class Tool(QDialog):
    TITLE = "Quadratic Explorer"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.TITLE)
        self.setMinimumWidth(840)

        self._build_ui()
        self._wire()

        # First draw with defaults
        self.a_edit.setText("1")
        self.b_edit.setText("0")
        self.c_edit.setText("0")
        self._solve_and_plot()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)

        # Inputs grid
        grid = QGridLayout()
        self.a_edit = QLineEdit(); self._num(self.a_edit, "a")
        self.b_edit = QLineEdit(); self._num(self.b_edit, "b")
        self.c_edit = QLineEdit(); self._num(self.c_edit, "c")

        grid.addWidget(QLabel("ax² + bx + c = 0"), 0, 0, 1, 6)

        grid.addWidget(QLabel("a:"), 1, 0); grid.addWidget(self.a_edit, 1, 1)
        grid.addWidget(QLabel("b:"), 1, 2); grid.addWidget(self.b_edit, 1, 3)
        grid.addWidget(QLabel("c:"), 1, 4); grid.addWidget(self.c_edit, 1, 5)

        # Range controls
        self.xmin = QSpinBox(); self.xmin.setRange(-10000, 9999); self.xmin.setValue(-10)
        self.xmax = QSpinBox(); self.xmax.setRange(-9999, 10000); self.xmax.setValue(10)
        grid.addWidget(QLabel("x-range:"), 2, 0)
        grid.addWidget(self.xmin, 2, 1)
        grid.addWidget(QLabel("to"), 2, 2)
        grid.addWidget(self.xmax, 2, 3)

        # Options
        self.cb_vertex = QCheckBox("Show vertex"); self.cb_vertex.setChecked(True)
        self.cb_axis   = QCheckBox("Show axis of symmetry"); self.cb_axis.setChecked(True)
        self.cb_roots  = QCheckBox("Show real roots"); self.cb_roots.setChecked(True)
        self.cb_grid   = QCheckBox("Grid"); self.cb_grid.setChecked(True)
        grid.addWidget(self.cb_vertex, 3, 0, 1, 2)
        grid.addWidget(self.cb_axis,   3, 2, 1, 2)
        grid.addWidget(self.cb_roots,  3, 4, 1, 2)
        grid.addWidget(self.cb_grid,   4, 0, 1, 2)

        root.addLayout(grid)

        # Buttons
        row = QHBoxLayout()
        self.solve_btn  = QPushButton("Solve & Plot")
        self.clear_btn  = QPushButton("Clear")
        self.export_btn = QPushButton("Export Image")
        row.addWidget(self.solve_btn); row.addWidget(self.clear_btn); row.addWidget(self.export_btn)
        root.addLayout(row)

        # Figure
        self.fig = Figure(figsize=(7.6, 4.6), dpi=110)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(NavigationToolbar(self.canvas, self))
        root.addWidget(self.canvas)

        # Result text
        self.out = QLabel("")
        self.out.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.out)

    def _num(self, line: QLineEdit, name: str):
        v = QDoubleValidator(bottom=-1e18, top=1e18, decimals=8)
        v.setNotation(QDoubleValidator.Notation.StandardNotation)
        line.setValidator(v)
        line.setPlaceholderText(name)

    def _wire(self):
        self.solve_btn.clicked.connect(self._solve_and_plot)
        self.clear_btn.clicked.connect(self._clear)
        self.export_btn.clicked.connect(self._export)

        # Live update when Enter pressed in inputs
        for w in (self.a_edit, self.b_edit, self.c_edit):
            w.returnPressed.connect(self._solve_and_plot)
        for w in (self.xmin, self.xmax):
            w.valueChanged.connect(self._solve_and_plot)
        for w in (self.cb_vertex, self.cb_axis, self.cb_roots, self.cb_grid):
            w.stateChanged.connect(self._solve_and_plot)

    # ---------- core ----------
    def _collect(self):
        try:
            a = float(self.a_edit.text())
            b = float(self.b_edit.text())
            c = float(self.c_edit.text())
        except Exception:
            raise ValueError("Coefficients must be numbers.")
        if abs(a) < 1e-15:
            raise ValueError("a must be non-zero for a quadratic.")
        if self.xmin.value() >= self.xmax.value():
            raise ValueError("x-range must have xmin < xmax.")
        return a, b, c

    def _solve(self, a: float, b: float, c: float) -> QuadResult:
        D = b*b - 4*a*c
        xv = -b / (2*a)
        yv = a*xv*xv + b*xv + c
        if D >= 0:
            sqrtD = math.sqrt(D)
            r1 = (-b - sqrtD) / (2*a)
            r2 = (-b + sqrtD) / (2*a)
        else:
            sqrtD = math.sqrt(-D)
            real = -b / (2*a)
            imag = sqrtD / (2*a)
            r1 = complex(real, -imag)
            r2 = complex(real, +imag)
        return QuadResult((r1, r2), (xv, yv), xv, D)

    def _clear(self):
        self.a_edit.clear(); self.b_edit.clear(); self.c_edit.clear()
        self.out.setText("")
        self.fig.clear(); self.canvas.draw()

    def _solve_and_plot(self):
        # Parse and solve
        try:
            a, b, c = self._collect()
            res = self._solve(a, b, c)
        except Exception as e:
            self.out.setText(f"Error: {e}")
            self.fig.clear(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
            return

        # Present results (concise, math-ish)
        def fmt(z):
            if isinstance(z, complex):
                return f"{z.real:.6g}{'+' if z.imag>=0 else '-'}{abs(z.imag):.6g}i"
            return f"{z:.6g}"

        txt = (
            f"Discriminant Δ = {res.discriminant:.6g}\n"
            f"Roots x₁, x₂ = {fmt(res.roots[0])}, {fmt(res.roots[1])}\n"
            f"Vertex V({res.vertex[0]:.6g}, {res.vertex[1]:.6g}); axis x = {res.axis:.6g}"
        )
        self.out.setText(txt)

        # Plot
        self._draw(a, b, c, res)

        # Log
        add_log_entry(self.TITLE, action="Solve",
                      data={"a": a, "b": b, "c": c,
                            "D": res.discriminant,
                            "roots": [fmt(res.roots[0]), fmt(res.roots[1])],
                            "vertex": [res.vertex[0], res.vertex[1]]})

    def _draw(self, a: float, b: float, c: float, res: QuadResult):
        self.fig.clear()

        # Main axes for y(x)
        ax = self.fig.add_subplot(121)
        ax.set_xlabel("x"); ax.set_ylabel("y = ax² + bx + c")
        ax.grid(self.cb_grid.isChecked(), alpha=0.3)

        xs = np.linspace(self.xmin.value(), self.xmax.value(), 600)
        ys = a*xs*xs + b*xs + c
        ax.plot(xs, ys, linewidth=2.0)

        # Vertex
        if self.cb_vertex.isChecked():
            xv, yv = res.vertex
            ax.scatter([xv], [yv], s=28)
            ax.annotate(f"V({xv:.3g},{yv:.3g})", (xv, yv),
                        textcoords="offset points", xytext=(6, 6))

        # Axis of symmetry
        if self.cb_axis.isChecked():
            xv = res.axis
            ax.axvline(xv, linestyle="--", linewidth=1.2, alpha=0.8)

        # Real roots
        if self.cb_roots.isChecked() and res.discriminant >= 0:
            r1, r2 = res.roots
            ax.axhline(0, linewidth=1.0, alpha=0.5)
            ax.scatter([r1, r2], [0, 0], s=26)
            ax.annotate(f"x₁={r1:.3g}", (r1, 0), textcoords="offset points", xytext=(6, 8))
            ax.annotate(f"x₂={r2:.3g}", (r2, 0), textcoords="offset points", xytext=(6, -10))

        # Tight-ish view
        ax.relim(); ax.autoscale_view()

        # Secondary view: roots in complex plane if needed
        ax2 = self.fig.add_subplot(122)
        ax2.set_xlabel("Re"); ax2.set_ylabel("Im")
        ax2.grid(self.cb_grid.isChecked(), alpha=0.3)
        if res.discriminant < 0:
            r1, r2 = res.roots
            ax2.scatter([r1.real, r2.real], [r1.imag, r2.imag])
            ax2.axhline(0, linewidth=1.0, alpha=0.5)
            ax2.axvline(0, linewidth=1.0, alpha=0.5)
            ax2.annotate("x₁", (r1.real, r1.imag), textcoords="offset points", xytext=(6, 6))
            ax2.annotate("x₂", (r2.real, r2.imag), textcoords="offset points", xytext=(6, -10))
            # Equal aspect for Argand diagram
            lim = max(1.0, abs(r1.real), abs(r2.real), abs(r1.imag), abs(r2.imag))
            ax2.set_xlim(-lim, lim); ax2.set_ylim(-lim, lim)
            ax2.set_aspect("equal", adjustable="box")
            ax2.set_title("Roots (complex plane)")
        else:
            ax2.axis("off")
            ax2.set_title("Δ ≥ 0")

        self.fig.tight_layout()
        self.canvas.draw()

    # ---------- export ----------
    def _export(self):
        try:
            path = export_figure(self.fig, out_dir=IMAGES_DIR)
            QMessageBox.information(self, "Export", f"Plot exported to:\n{path}")
            add_log_entry(self.TITLE, action="Export", data={"path": str(path)})
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))
            add_log_entry(self.TITLE, action="ExportError", data={"msg": str(e)})
