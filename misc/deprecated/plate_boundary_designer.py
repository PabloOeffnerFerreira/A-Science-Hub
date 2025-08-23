
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import FancyArrow, Rectangle
from core.data.functions.log import add_log_entry
from core.data.functions.image_export import export_figure

class Tool(QDialog):
    TITLE = "Plate Boundary Designer"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("Boundary Type:"))
        self.kind = QComboBox(); self.kind.addItems(["Convergent", "Divergent", "Transform"])
        row.addWidget(self.kind)
        self.draw_btn = QPushButton("Draw"); row.addWidget(self.draw_btn)
        self.save_btn = QPushButton("Export Diagram…"); row.addWidget(self.save_btn)
        lay.addLayout(row)

        self.fig = Figure(figsize=(7,4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self))
        lay.addWidget(self.canvas, 1)

        self.draw_btn.clicked.connect(self._draw)
        self.save_btn.clicked.connect(self._save)

    def _draw(self):
        kind = self.kind.currentText()
        self.fig.clear(); ax = self.fig.add_subplot(111)
        ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")

        # Base plates
        left = Rectangle((1, 2.5), 3, 1, facecolor="#c0d5ff", edgecolor="k")
        right = Rectangle((6, 2.5), 3, 1, facecolor="#ffd4aa", edgecolor="k")
        ax.add_patch(left); ax.add_patch(right)

        if kind == "Convergent":
            ax.add_patch(FancyArrow(4, 3, -2.2, 0, width=0.1, head_width=0.4, head_length=0.4, length_includes_head=True))
            ax.add_patch(FancyArrow(6, 3, 2.2, 0, width=0.1, head_width=0.4, head_length=0.4, length_includes_head=True))
            # Trench and volcano
            ax.plot([5, 5.4], [2.5, 1.2], color="k", linewidth=2)  # trench
            ax.plot([4.7, 5.2, 5.5], [2.5, 3.8, 2.5], color="brown")  # arc/volcano
            ax.text(5.1, 4.0, "Volcano", ha="center")

        elif kind == "Divergent":
            ax.add_patch(FancyArrow(4, 3, -2.2, 0, width=0.1, head_width=0.4, head_length=0.4, length_includes_head=True))
            ax.add_patch(FancyArrow(6, 3, 2.2, 0, width=0.1, head_width=0.4, head_length=0.4, length_includes_head=True))
            # Ridge
            ax.plot([5, 5], [2.5, 4.0], color="k", linewidth=3)
            ax.text(5.0, 4.1, "Ridge", ha="center")

        else:  # Transform
            # Sideways motion arrows
            ax.add_patch(FancyArrow(4.5, 2.2, 0, -1.5, width=0.1, head_width=0.3, head_length=0.3, length_includes_head=True))
            ax.add_patch(FancyArrow(5.5, 3.8, 0, 1.5, width=0.1, head_width=0.3, head_length=0.3, length_includes_head=True))
            ax.plot([5, 5], [2.0, 4.0], color="k", linewidth=2, linestyle="--")
            ax.text(5.0, 4.1, "Fault", ha="center")

        self.fig.tight_layout(); self.canvas.draw()
        add_log_entry(self.TITLE, action="Draw", data={"kind": kind})

    def _save(self):
        try:
            path = export_figure(self.figure if False else self.fig)
            add_log_entry(self.TITLE, action="ExportImage", data={"path": str(path)})
        except Exception as e:
            add_log_entry(self.TITLE, action="ExportError", data={"msg": str(e)})
