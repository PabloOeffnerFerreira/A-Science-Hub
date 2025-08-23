from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QSizePolicy, QMessageBox
)

# 3D realtime stack (preferred)
PG_OK = True
try:
    import pyqtgraph as pg
    import pyqtgraph.opengl as gl
except Exception:
    PG_OK = False
    pg = None
    gl = None

# 2D fallback (only used if no GL available)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry
try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


# ---------- helpers ----------

def _parse_vec(text: str) -> np.ndarray:
    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    if not parts:
        raise ValueError("Empty vector.")
    arr = np.array([float(p) for p in parts], dtype=float)
    return arr

def _norm(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))

def _safe_unit(v: np.ndarray) -> np.ndarray:
    n = _norm(v)
    if n == 0.0:
        raise ValueError("Cannot normalize zero vector.")
    return v / n

def _angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    na = _norm(a); nb = _norm(b)
    if na == 0 or nb == 0:
        raise ValueError("Angle undefined for zero vector.")
    cos_t = float(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0))
    return float(np.degrees(math.acos(cos_t)))

def _proj_of_a_on_b(a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    nb2 = float(np.dot(b, b))
    if nb2 == 0:
        raise ValueError("Projection undefined onto zero vector.")
    proj = (np.dot(a, b) / nb2) * b
    perp = a - proj
    return proj, perp


# ---------- arrow geometry (GL) ----------

def _make_arrow(start: np.ndarray, vec: np.ndarray, color=(0.85, 0.9, 1.0, 1.0)):
    """
    Compose a shaft (line) + tiny cone head using GLLinePlotItem + GLMeshItem.
    start: 3D point; vec: 3D vector from start.
    """
    if gl is None:
        return None, None
    start = np.asarray(start, dtype=float)
    end = start + vec
    line_pts = np.vstack([start, end]).astype(float)

    shaft = gl.GLLinePlotItem(pos=line_pts, width=3.0, antialias=True)
    shaft.setGLOptions('opaque')

    # arrow head: small cone aligned with vec
    length = _norm(vec)
    head = None
    if length > 1e-9:
        # Create cone pointing along +Z, then rotate to vec direction, then translate to tip
        cone_data = gl.MeshData.cylinder(rows=1, cols=16, radius=[0.0, 0.045 * length], length=0.12 * length)
        head = gl.GLMeshItem(meshdata=cone_data, color=color, smooth=True, shader='shaded')
        # Orthonormal frame: align z-axis to vec
        v = vec / length
        z = np.array([0, 0, 1.0], dtype=float)
        axis = np.cross(z, v)
        s = _norm(axis)
        if s < 1e-9:
            R = np.eye(3)
        else:
            axis /= s
            c = float(np.dot(z, v))
            K = np.array([[0, -axis[2], axis[1]],
                          [axis[2], 0, -axis[0]],
                          [-axis[1], axis[0], 0]])
            R = np.eye(3) + K + K @ K * ((1 - c) / (s * s))
        # place base at slightly before the end
        base = end - v * (0.12 * length)
        # Build 4x4 transform
        M = np.eye(4)
        M[:3, :3] = R
        M[:3, 3] = base
        # set transform
        head.resetTransform()
        head.setTransform(pg.Transform3D(*M.T.reshape(-1)))
    return shaft, head


# ---------- Tool ----------

@dataclass
class Result:
    text: str
    vector: Optional[np.ndarray] = None  # for 3D drawing

class Tool(QDialog):
    TITLE = "Vector Calculator (3D)"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.TITLE)
        self.setMinimumWidth(760)

        self._build_ui()
        self._build_views()
        self._wire()

        self._arrows = []  # GL items
        self._hud = None

    # ----- UI -----
    def _build_ui(self):
        lay = QVBoxLayout(self)

        # Operation row
        op_row = QHBoxLayout()
        self.operation = QComboBox()
        self.operation.addItems([
            "Dot Product",
            "Cross Product",
            "Angle Between",
            "Magnitude of A",
            "Magnitude of B",
            "Normalize A",
            "Normalize B",
            "Projection of A onto B",
            "Components of A wrt B"
        ])
        op_row.addWidget(QLabel("Operation:"))
        op_row.addWidget(self.operation)
        lay.addLayout(op_row)

        # Inputs
        lay.addWidget(QLabel("Vector A (comma-separated):"))
        self.a_in = QLineEdit(); lay.addWidget(self.a_in)
        lay.addWidget(QLabel("Vector B (comma-separated):"))
        self.b_in = QLineEdit(); lay.addWidget(self.b_in)

        # Buttons + result
        row2 = QHBoxLayout()
        self.run = QPushButton("Calculate")
        self.clear = QPushButton("Clear")
        self.export_btn = QPushButton("Export View")
        row2.addWidget(self.run); row2.addWidget(self.clear); row2.addWidget(self.export_btn)
        lay.addLayout(row2)

        self.result = QLabel("")
        self.result.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.result)

    def _build_views(self):
        # Fallback 2D view constructed regardless; only displayed if GL fails.
        self.fig = Figure(figsize=(5.6, 3.8), dpi=110)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        if PG_OK:
            try:
                self.view3d = gl.GLViewWidget()
                self.view3d.setBackgroundColor((18, 18, 18))
                self.view3d.setCameraPosition(distance=9.0, elevation=18, azimuth=35)
                # Ensure visibility in dialogs/layouts
                self.view3d.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.view3d.setMinimumHeight(420)

                # Add GL view first, so it gets space
                self.layout().addWidget(self.view3d)

                # Axes & grid
                grid = gl.GLGridItem(); grid.setSize(10, 10, 1); self.view3d.addItem(grid)
                ax = gl.GLAxisItem(); ax.setSize(3, 3, 3); self.view3d.addItem(ax)

                # HUD text (clean overlay)
                self.hud = QLabel(self.view3d)
                self.hud.setStyleSheet("color: white; background: transparent; padding: 0;")
                self.hud.move(8, 8); self.hud.raise_()

            except Exception:
                # Fallback to 2D
                self.view3d = None
                self.layout().addWidget(self.toolbar)
                self.layout().addWidget(self.canvas)
        else:
            self.view3d = None
            self.layout().addWidget(self.toolbar)
            self.layout().addWidget(self.canvas)

    def _wire(self):
        self.run.clicked.connect(self._calc)
        self.clear.clicked.connect(self._clear)
        self.export_btn.clicked.connect(self._export)

    # ----- actions -----

    def _clear(self):
        self.a_in.clear(); self.b_in.clear()
        self.result.setText("")
        if self.view3d is not None:
            self._clear_gl()
        else:
            self.fig.clear(); self.canvas.draw()

    def _calc(self):
        op = self.operation.currentText()
        A_txt = self.a_in.text().strip()
        B_txt = self.b_in.text().strip()

        try:
            A = _parse_vec(A_txt) if A_txt else np.array([])
            B = _parse_vec(B_txt) if B_txt else np.array([])

            # Basic dimension checks
            def same_dim():
                return A.size > 0 and B.size > 0 and A.shape == B.shape

            res = Result(text="")
            if op == "Dot Product":
                if not same_dim(): raise ValueError("Vectors must have same dimension.")
                val = float(np.dot(A, B))
                res.text = f"Dot(A,B) = {val:.6g}"

            elif op == "Cross Product":
                if A.size != 3 or B.size != 3:
                    raise ValueError("Cross product requires two 3D vectors.")
                v = np.cross(A, B)
                res.text = "A×B = [" + ", ".join(f"{x:.6g}" for x in v) + "]"
                res.vector = v

            elif op == "Angle Between":
                if not same_dim(): raise ValueError("Vectors must have same dimension.")
                deg = _angle_deg(A, B)
                res.text = f"∠(A,B) = {deg:.6g}°"

            elif op == "Magnitude of A":
                if A.size == 0: raise ValueError("Vector A required.")
                res.text = f"|A| = {_norm(A):.6g}"

            elif op == "Magnitude of B":
                if B.size == 0: raise ValueError("Vector B required.")
                res.text = f"|B| = {_norm(B):.6g}"

            elif op == "Normalize A":
                if A.size == 0: raise ValueError("Vector A required.")
                u = _safe_unit(A)
                res.text = "Â = [" + ", ".join(f"{x:.6g}" for x in u) + "]"
                res.vector = u

            elif op == "Normalize B":
                if B.size == 0: raise ValueError("Vector B required.")
                u = _safe_unit(B)
                res.text = " B̂ = [" + ", ".join(f"{x:.6g}" for x in u) + "]"
                res.vector = u

            elif op == "Projection of A onto B":
                if not same_dim(): raise ValueError("Vectors must have same dimension.")
                proj, _ = _proj_of_a_on_b(A, B)
                res.text = "proj_B(A) = [" + ", ".join(f"{x:.6g}" for x in proj) + "]"
                res.vector = proj

            elif op == "Components of A wrt B":
                if not same_dim(): raise ValueError("Vectors must have same dimension.")
                proj, perp = _proj_of_a_on_b(A, B)
                res.text = (
                    "A∥ = [" + ", ".join(f"{x:.6g}" for x in proj) + "]\n"
                    "A⟂ = [" + ", ".join(f"{x:.6g}" for x in perp) + "]"
                )
                # No single "result" vector; draw both
                res.vector = None

            # Display text
            self.result.setText(res.text)

            # Draw
            if self.view3d is not None:
                self._draw_gl(A if A.size == 3 else None, B if B.size == 3 else None, res, op)
            else:
                self._draw_matplotlib(A if A.size == 3 else None, B if B.size == 3 else None, res)

            # Log
            add_log_entry(self.TITLE, action="Calculate", data={
                "op": op, "A": A_txt, "B": B_txt, "result": res.text
            })

        except Exception as e:
            self.result.setText(f"Error: {e}")
            if self.view3d is not None:
                self._clear_gl()
            else:
                self.fig.clear(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Error", data={"op": op, "A": A_txt, "B": B_txt, "msg": str(e)})

    # ----- drawing -----

    def _scene_bounds(self, vectors: list[np.ndarray]) -> float:
        vals = [abs(float(x)) for v in vectors if v is not None for x in v]
        return max(3.0, (max(vals) if vals else 1.0) * 1.6)

    def _clear_gl(self):
        for item in getattr(self, "_arrows", []):
            try:
                self.view3d.removeItem(item)
            except Exception:
                pass
        self._arrows = []
        if getattr(self, "hud", None):
            self.hud.setText(""); self.hud.adjustSize()

    def _draw_gl(self, A: Optional[np.ndarray], B: Optional[np.ndarray], res: Result, op: str):
        self._clear_gl()

        # Scale view to fit content
        bound = self._scene_bounds([A, B, (res.vector if res.vector is not None else None)])
        self.view3d.opts['distance'] = bound * 1.8

        # Axes helper (scaled)
        axes = gl.GLAxisItem()
        axes.setSize(bound, bound, bound)
        self.view3d.addItem(axes); self._arrows.append(axes)

        # Draw A, B
        if A is not None:
            sA, hA = _make_arrow(np.zeros(3), A, color=(0.7, 0.9, 1.0, 1.0))
            if sA: self.view3d.addItem(sA); self._arrows.append(sA)
            if hA: self.view3d.addItem(hA); self._arrows.append(hA)
        if B is not None:
            sB, hB = _make_arrow(np.zeros(3), B, color=(0.9, 0.75, 0.75, 1.0))
            if sB: self.view3d.addItem(sB); self._arrows.append(sB)
            if hB: self.view3d.addItem(hB); self._arrows.append(hB)

        # Draw result depending on op
        if op == "Cross Product" and res.vector is not None:
            sR, hR = _make_arrow(np.zeros(3), res.vector, color=(0.8, 0.95, 0.75, 1.0))
            if sR: self.view3d.addItem(sR); self._arrows.append(sR)
            if hR: self.view3d.addItem(hR); self._arrows.append(hR)

        elif op == "Normalize A" and res.vector is not None:
            sR, hR = _make_arrow(np.zeros(3), res.vector, color=(0.8, 0.95, 0.75, 1.0))
            if sR: self.view3d.addItem(sR); self._arrows.append(sR)
            if hR: self.view3d.addItem(hR); self._arrows.append(hR)

        elif op == "Normalize B" and res.vector is not None:
            sR, hR = _make_arrow(np.zeros(3), res.vector, color=(0.8, 0.95, 0.75, 1.0))
            if sR: self.view3d.addItem(sR); self._arrows.append(sR)
            if hR: self.view3d.addItem(hR); self._arrows.append(hR)

        elif op == "Projection of A onto B" and res.vector is not None and A is not None:
            # draw projection vector from origin; and helper from tip(A) to proj
            proj = res.vector
            sP, hP = _make_arrow(np.zeros(3), proj, color=(0.75, 0.95, 0.8, 1.0))
            if sP: self.view3d.addItem(sP); self._arrows.append(sP)
            if hP: self.view3d.addItem(hP); self._arrows.append(hP)
            # helper: A tip to projection tip
            tipA = A
            tipP = proj
            seg = np.vstack([tipA, tipP]).astype(float)
            connector = gl.GLLinePlotItem(pos=seg, width=1.5, antialias=True)
            self.view3d.addItem(connector); self._arrows.append(connector)

        elif op == "Components of A wrt B" and A is not None and B is not None:
            proj, perp = _proj_of_a_on_b(A, B)
            # A∥
            sQ, hQ = _make_arrow(np.zeros(3), proj, color=(0.75, 0.95, 0.8, 1.0))
            if sQ: self.view3d.addItem(sQ); self._arrows.append(sQ)
            if hQ: self.view3d.addItem(hQ); self._arrows.append(hQ)
            # A⟂
            sP, hP = _make_arrow(proj, perp, color=(0.85, 0.85, 0.95, 1.0))
            if sP: self.view3d.addItem(sP); self._arrows.append(sP)
            if hP: self.view3d.addItem(hP); self._arrows.append(hP)

        # HUD
        if getattr(self, "hud", None):
            txt = []
            if A is not None: txt.append(f"A = [{', '.join(f'{x:.3g}' for x in A)}]")
            if B is not None: txt.append(f"B = [{', '.join(f'{x:.3g}' for x in B)}]")
            if op == "Angle Between" and A is not None and B is not None:
                txt.append(f"Angle = {_angle_deg(A,B):.4g}°")
            self.hud.setText("\n".join(txt))
            self.hud.adjustSize()
            self.hud.move(8, 8)

    def _draw_matplotlib(self, A: Optional[np.ndarray], B: Optional[np.ndarray], res: Result):
        # Fallback: draw simple quivers in mpl 3D
        self.fig.clear()
        ax = self.fig.add_subplot(111, projection='3d')
        ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
        bound = self._scene_bounds([A, B, res.vector])
        for lim in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
            lim(-bound, bound)
        if A is not None: ax.quiver(0,0,0, *A.tolist(), label='A')
        if B is not None: ax.quiver(0,0,0, *B.tolist(), label='B')
        if res.vector is not None: ax.quiver(0,0,0, *res.vector.tolist(), label='Result')
        if any(v is not None for v in (A, B, res.vector)): ax.legend(loc='upper left')
        self.fig.tight_layout(); self.canvas.draw()

    # ----- export -----

    def _export(self):
        try:
            if self.view3d is not None:
                arr = self.view3d.renderToArray((1400, 900))
                import imageio.v2 as iio
                from pathlib import Path
                p = Path(IMAGES_DIR) if IMAGES_DIR else Path(".")
                p.mkdir(parents=True, exist_ok=True)
                out = p / "vector_calc_3d.png"
                iio.imwrite(out.as_posix(), arr)
                QMessageBox.information(self, "Export", f"3D snapshot saved to:\n{out}")
                add_log_entry(self.TITLE, action="Export3D", data={"path": str(out)})
            else:
                path = export_figure(self.fig, out_dir=IMAGES_DIR)
                QMessageBox.information(self, "Export", f"Plot exported to:\n{path}")
                add_log_entry(self.TITLE, action="Export2D", data={"path": str(path)})
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))
            add_log_entry(self.TITLE, action="ExportError", data={"msg": str(e)})
