
import math
import numpy as np
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSizePolicy
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Circle  # <-- correct import
from core.data.functions.chemistry_utils import load_element_data
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


class Tool(QDialog):
    TITLE = "Shell Visualiser"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        self.resize(640, 700)
        self.data = load_element_data()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Element Symbol:"))
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("e.g., H, He, Fe")
        layout.addWidget(self.entry)

        self.draw_btn = QPushButton("Draw & Save")
        layout.addWidget(self.draw_btn)
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)

        self.draw_btn.clicked.connect(self._draw)

    def _draw(self):
        sym = self.entry.text().strip().capitalize()
        el = self.data.get(sym)
        if not el or "shells" not in el:
            QMessageBox.warning(self, "Not found", f"No shell data for element '{sym}'")
            return
        shells = el["shells"]
        max_shells = len(shells)

        # Scaled radii so large-Z elements still fit
        base_radius = 0.6
        def radius_func(i):  # i = 0..(n-1)
            return base_radius + math.sqrt(i + 1) * 0.7
        radii = np.array([radius_func(i) for i in range(max_shells)], dtype=float)
        max_radius = radii[-1] if len(radii) else base_radius
        max_allowed_radius = 8.0
        scale = min(1.0, (max_allowed_radius / max_radius) if max_radius else 1.0)
        radii *= scale
        max_radius *= scale

        # Prepare figure/axes
        self.figure.set_size_inches(5 + max_radius * 0.8, 5 + max_radius * 0.8)
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        cx, cy = 0.0, 0.0
        colours = ["#b0c4de", "#add8e6", "#90ee90", "#ffa07a", "#ffd700", "#e9967a", "#dda0dd"]

        # Draw shells and electrons
        for i, count in enumerate(shells):
            r = float(radii[i])
            shell_circle = Circle((cx, cy), r, fill=False,
                                  edgecolor=colours[i % len(colours)], linewidth=2)
            ax.add_patch(shell_circle)

            # Place electrons evenly on the shell
            for j in range(max(1, count)):
                ang = 2 * math.pi * j / max(1, count)
                ex = cx + r * math.cos(ang)
                ey = cy + r * math.sin(ang)
                e = Circle((ex, ey), 0.06 * scale, facecolor="black", edgecolor="none")
                ax.add_patch(e)

        # Nucleus label
        ax.text(cx, cy, sym, fontsize=max(10, int(16 * scale)), fontweight="bold",
                ha='center', va='center')

        # Frame
        pad = max_radius * 0.6 + 1.0
        ax.set_xlim(-max_radius - pad, max_radius + pad)
        ax.set_ylim(-max_radius - pad, max_radius + pad)
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')

        self.canvas.draw()

        # Export
        try:
            path = export_figure(self.figure, out_dir=IMAGES_DIR) if IMAGES_DIR else export_figure(self.figure)
            self.status_label.setText(f"Saved: {path}")
            add_log_entry("Shell Visualiser", action="Draw",
                          data={"symbol": sym, "shells": shells, "image": str(path)})
        except Exception as e:
            self.status_label.setText(f"Save failed: {e}")
