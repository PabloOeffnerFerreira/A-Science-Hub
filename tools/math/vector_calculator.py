# Todo: I will add a more advanced vector calculator later, this is just a simple one.
# It will handle more operations, provide a better UI, and the 3d visualization will be improved. Its currently just some matplotlib (basically) 2d 3d plotting. It will be more improved.

from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

def _parse_vec(text: str) -> np.ndarray:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("Empty vector.")
    return np.array([float(p) for p in parts], dtype=float)

class Tool(QDialog):
    TITLE = "Vector Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)

        self.operation = QComboBox()
        self.operation.addItems([
            "Dot Product",
            "Cross Product (3D)",
            "Angle Between",
            "Magnitude of A",
            "Magnitude of B",
            "Normalize A",
            "Normalize B"
        ])
        lay.addWidget(self.operation)

        lay.addWidget(QLabel("Vector A (comma-separated):"))
        self.a_in = QLineEdit(); lay.addWidget(self.a_in)
        lay.addWidget(QLabel("Vector B (comma-separated):"))
        self.b_in = QLineEdit(); lay.addWidget(self.b_in)

        self.run = QPushButton("Calculate"); lay.addWidget(self.run)
        self.result = QLabel(""); lay.addWidget(self.result)

        # Embedded plot
        self.fig = Figure(figsize=(5,4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self))
        lay.addWidget(self.canvas, 1)
        self.export_btn = QPushButton("Export Image…"); lay.addWidget(self.export_btn)

        self.run.clicked.connect(self._calc)
        self.export_btn.clicked.connect(self._export)

    def _calc(self):
        op = self.operation.currentText()
        A_txt = self.a_in.text().strip()
        B_txt = self.b_in.text().strip()

        try:
            A = _parse_vec(A_txt) if A_txt else np.array([])
            B = _parse_vec(B_txt) if B_txt else np.array([])

            res = None
            if op == "Dot Product":
                if A.size == 0 or B.size == 0 or A.shape != B.shape:
                    raise ValueError("Vectors must have the same dimension.")
                res = float(np.dot(A, B))
                self.result.setText(f"Result: {res:.6g}")

            elif op == "Cross Product (3D)":
                if A.size != 3 or B.size != 3:
                    raise ValueError("Cross product requires two 3D vectors.")
                res = np.cross(A, B)
                self.result.setText("Result: [" + ", ".join(f"{v:.6g}" for v in res) + "]")

            elif op == "Angle Between":
                if A.size == 0 or B.size == 0 or A.shape != B.shape:
                    raise ValueError("Vectors must have the same dimension.")
                denom = (np.linalg.norm(A) * np.linalg.norm(B))
                if denom == 0:
                    raise ValueError("Angle undefined for zero vector.")
                cos_t = float(np.dot(A, B) / denom)
                cos_t = float(np.clip(cos_t, -1.0, 1.0))
                ang = float(np.degrees(np.arccos(cos_t)))
                res = ang
                self.result.setText(f"Angle: {ang:.6g}°")

            elif op == "Magnitude of A":
                if A.size == 0:
                    raise ValueError("Vector A required.")
                res = float(np.linalg.norm(A))
                self.result.setText(f"|A| = {res:.6g}")

            elif op == "Magnitude of B":
                if B.size == 0:
                    raise ValueError("Vector B required.")
                res = float(np.linalg.norm(B))
                self.result.setText(f"|B| = {res:.6g}")

            elif op == "Normalize A":
                if A.size == 0:
                    raise ValueError("Vector A required.")
                n = float(np.linalg.norm(A))
                if n == 0:
                    raise ValueError("Cannot normalise zero vector.")
                res = (A / n)
                self.result.setText("Â = [" + ", ".join(f"{v:.6g}" for v in res) + "]")

            elif op == "Normalize B":
                if B.size == 0:
                    raise ValueError("Vector B required.")
                n = float(np.linalg.norm(B))
                if n == 0:
                    raise ValueError("Cannot normalise zero vector.")
                res = (B / n)
                self.result.setText("B̂ = [" + ", ".join(f"{v:.6g}" for v in res) + "]")

            # Draw if 3D inputs available
            self._plot_vectors(A if A.size==3 else None, B if B.size==3 else None, res if isinstance(res, np.ndarray) and res.size==3 else None)

            # Log
            add_log_entry(self.TITLE, action="Calculate", data={
                "op": op, "A": A_txt, "B": B_txt, "result": (float(res) if isinstance(res, (int,float,np.floating)) else (res.tolist() if isinstance(res, np.ndarray) else str(res)))
            })
        except Exception as e:
            self.result.setText(f"Error: {e}")
            self.fig.clear(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Error", data={"op": op, "A": A_txt, "B": B_txt, "msg": str(e)})

    def _plot_vectors(self, A, B, R=None):
        self.fig.clear()
        if A is None and B is None and R is None:
            self.canvas.draw(); return
        ax = self.fig.add_subplot(111, projection='3d')
        ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
        ax.set_xlim([-10, 10]); ax.set_ylim([-10, 10]); ax.set_zlim([-10, 10])
        if A is not None: ax.quiver(0,0,0, A[0],A[1],A[2], label='A')
        if B is not None: ax.quiver(0,0,0, B[0],B[1],B[2], label='B')
        if R is not None: ax.quiver(0,0,0, R[0],R[1],R[2], label='Result')
        if any(v is not None for v in (A,B,R)): ax.legend(loc='upper left')
        self.fig.tight_layout(); self.canvas.draw()

    def _export(self):
        try:
            path = export_figure(self.fig)
            add_log_entry(self.TITLE, action="ExportImage", data={"path": str(path)})
        except Exception as e:
            add_log_entry(self.TITLE, action="ExportError", data={"msg": str(e)})
