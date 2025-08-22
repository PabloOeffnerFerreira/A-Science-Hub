
"""
Magnetic field line visualiser. Provides a PyQt6 QDialog tool that lets the user
place point dipole-like magnets and render field lines using Matplotlib.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, Qt

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Shared project imports (logging & export), paths guarded
from core.data.functions.log import add_log_entry
from core.data.functions.image_export import export_figure
import core.data.paths as paths  # use getattr to guard optional constants

TITLE = "Magnetic Field Lines"

class Tool(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TITLE)
        self.setMinimumSize(720, 560)

        self.magnets = []  # list of dicts: {"x": float, "y": float, "strength": float}

        # Layouts
        self.main_layout = QVBoxLayout(self)

        # Inputs
        self.inputs_row = QHBoxLayout()
        self.x_edit = QLineEdit(); self.x_edit.setPlaceholderText("x")
        self.y_edit = QLineEdit(); self.y_edit.setPlaceholderText("y")
        self.s_edit = QLineEdit(); self.s_edit.setPlaceholderText("strength (+/-)")

        num_regex = QRegularExpression(r"[-+]?[0-9]*\.?[0-9]+")
        validator = QRegularExpressionValidator(num_regex)
        for w in (self.x_edit, self.y_edit, self.s_edit):
            w.setValidator(validator)

        self.inputs_row.addWidget(QLabel("X:"))
        self.inputs_row.addWidget(self.x_edit)
        self.inputs_row.addWidget(QLabel("Y:"))
        self.inputs_row.addWidget(self.y_edit)
        self.inputs_row.addWidget(QLabel("Strength:"))
        self.inputs_row.addWidget(self.s_edit)
        self.main_layout.addLayout(self.inputs_row)

        # Buttons
        btns = QHBoxLayout()
        self.add_btn = QPushButton("Add magnet")
        self.clear_btn = QPushButton("Clear magnets")
        self.draw_btn = QPushButton("Draw field lines")
        self.export_btn = QPushButton("Export image…")

        btns.addWidget(self.add_btn)
        btns.addWidget(self.clear_btn)
        btns.addWidget(self.draw_btn)
        btns.addWidget(self.export_btn)
        self.main_layout.addLayout(btns)

        # Magnet list
        self.magnet_list = QListWidget()
        self.main_layout.addWidget(self.magnet_list)

        # Status
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.main_layout.addWidget(self.status_label)

        # Matplotlib canvas
        self.figure = Figure(figsize=(5, 4), layout="constrained")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ax = self.figure.add_subplot(111)
        self._init_axes()

        self.main_layout.addWidget(self.canvas)

        # Scatter + tooltip state
        self._scatter = None
        self._annot = self.ax.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self._annot.set_visible(False)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)

        # Connections
        self.add_btn.clicked.connect(self.add_magnet)
        self.clear_btn.clicked.connect(self.clear_magnets)
        self.draw_btn.clicked.connect(self.draw_field)
        self.export_btn.clicked.connect(self.export_image)

    def _init_axes(self):
        self.ax.clear()
        self.ax.set_title("Magnetic field lines")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_aspect("equal", "box")
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.canvas.draw_idle()

    def _refresh_scatter(self):
        # Render magnet markers
        if self._scatter is not None:
            self._scatter.remove()
            self._scatter = None
        if not self.magnets:
            self.canvas.draw_idle()
            return
        xs = [m["x"] for m in self.magnets]
        ys = [m["y"] for m in self.magnets]
        colours = ["red" if m["strength"] > 0 else "blue" for m in self.magnets]
        self._scatter = self.ax.scatter(xs, ys, s=60, marker="o", edgecolors="k", zorder=3)
        # Colour set on face after creation to keep pick math precise
        self._scatter.set_facecolors(colours)
        self.canvas.draw_idle()

    def _on_motion(self, event):
        if self._scatter is None or event.inaxes != self.ax:
            if self._annot.get_visible():
                self._annot.set_visible(False)
                self.canvas.draw_idle()
            return
        contains, info = self._scatter.contains(event)
        if not contains:
            if self._annot.get_visible():
                self._annot.set_visible(False)
                self.canvas.draw_idle()
            return
        ind = info.get("ind", [])
        if not ind:
            return
        i = int(ind[0])
        m = self.magnets[i]
        self._annot.xy = (m["x"], m["y"])
        self._annot.set_text(f"({m['x']:.3g}, {m['y']:.3g})\nS = {m['strength']:.3g}")
        self._annot.set_visible(True)
        self.canvas.draw_idle()

    def add_magnet(self):
        try:
            x = float(self.x_edit.text())
            y = float(self.y_edit.text())
            s = float(self.s_edit.text())
        except Exception:
            QMessageBox.warning(self, "Input error", "Please enter valid numbers for x, y, and strength.")
            return
        self.magnets.append({"x": x, "y": y, "strength": s})
        self.magnet_list.addItem(f"({x}, {y})  strength {s:+g}")
        self.x_edit.clear(); self.y_edit.clear(); self.s_edit.clear()
        self.status_label.setText(f"{len(self.magnets)} magnet(s) defined.")
        # Minimal logging: one per explicit user action
        try:
            add_log_entry("Magnoline", "add_magnet", {"x": x, "y": y, "strength": s})
        except Exception:
            pass
        self._refresh_scatter()

    def clear_magnets(self):
        count = len(self.magnets)
        self.magnets.clear()
        self.magnet_list.clear()
        self._init_axes()
        self.status_label.setText("Cleared all magnets.")
        try:
            add_log_entry("Magnoline", "clear_magnets", {"count": count})
        except Exception:
            pass

    def draw_field(self):
        if not self.magnets:
            QMessageBox.warning(self, "No magnets", "Add at least one magnet before drawing.")
            return

        # Field over fixed grid
        self.ax.clear()
        self._init_axes()

        grid_size = 80
        margin = 5.0
        xs = np.linspace(-margin, margin, grid_size)
        ys = np.linspace(-margin, margin, grid_size)
        X, Y = np.meshgrid(xs, ys)

        Bx = np.zeros_like(X, dtype=float)
        By = np.zeros_like(Y, dtype=float)

        # Simple dipole-like superposition (mirrors legacy behaviour)
        for m in self.magnets:
            mx, my, strength = m["x"], m["y"], m["strength"]
            dx = X - mx
            dy = Y - my
            r2 = dx**2 + dy**2
            r2[r2 == 0] = 1e-12
            r5 = r2 ** 2.5
            Bx += -3.0 * strength * dx * dy / r5
            By += strength * (2.0 * dy**2 - dx**2) / r5

        mag = np.hypot(Bx, By)
        nz = mag > 1e-14
        Bx[nz] /= mag[nz]
        By[nz] /= mag[nz]

        self.ax.streamplot(X, Y, Bx, By, density=1.3, linewidth=0.7, arrowsize=1.0)
        # plot magnets
        for m in self.magnets:
            c = "red" if m["strength"] > 0 else "blue"
            self.ax.plot(m["x"], m["y"], "o", color=c, markersize=7, zorder=3)
            self.ax.text(m["x"], m["y"], f"{m['strength']:+.2f}", color=c, fontsize=9,
                         ha="center", va="center", zorder=4)

        self._refresh_scatter()
        self.canvas.draw_idle()

        try:
            add_log_entry("Magnoline", "draw_field", {"magnets": len(self.magnets)})
        except Exception:
            pass

    def export_image(self):
        # Delegate to shared exporter; it should handle paths/dialogs.
        try:
            export_figure(self.figure, suggested_name="magnoline_field")
        except Exception as e:
            QMessageBox.warning(self, "Export failed", f"Could not export image: {e}")
