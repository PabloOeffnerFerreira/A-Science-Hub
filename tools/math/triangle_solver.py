from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QComboBox, QMessageBox
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Arc

from core.data.functions.log import add_log_entry
from core.data.functions.image_export import export_figure
try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


# ---------- helpers ----------

def _safe_float(text: str) -> Optional[float]:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None

def _deg2rad(x: float, mode: str) -> float:
    return math.radians(x) if mode == "Degrees" else x

def _rad2deg(x: float, mode: str) -> float:
    return math.degrees(x) if mode == "Degrees" else x

def _law_of_cosines_side(b: float, c: float, A: float) -> float:
    val = b*b + c*c - 2*b*c*math.cos(A)
    return math.sqrt(max(val, 0.0))

def _law_of_cosines_angle(a: float, b: float, c: float) -> float:
    denom = max(1e-12, 2*b*c)
    x = (b*b + c*c - a*a) / denom
    x = max(-1.0, min(1.0, x))
    return math.acos(x)

def _law_of_sines_side(known_side: float, known_ang: float, target_ang: float) -> float:
    denom = max(1e-12, math.sin(known_ang))
    return known_side * math.sin(target_ang) / denom

def _heron_area(a: float, b: float, c: float) -> float:
    s = 0.5 * (a + b + c)
    val = max(0.0, s * (s - a) * (s - b) * (s - c))
    return math.sqrt(val)


@dataclass
class Triangle:
    a: float; b: float; c: float  # sides opposite A,B,C
    A: float; B: float; C: float  # angles in radians


def _solve_triangle(inputs: Dict[str, Optional[float]], angle_mode: str) -> Tuple[Triangle, str]:
    """Return (Triangle, note). note may include 'SSA ambiguity'."""
    a = inputs.get("a"); b = inputs.get("b"); c = inputs.get("c")
    A = inputs.get("A"); B = inputs.get("B"); C = inputs.get("C")

    if A is not None: A = _deg2rad(A, angle_mode)
    if B is not None: B = _deg2rad(B, angle_mode)
    if C is not None: C = _deg2rad(C, angle_mode)

    known_s = sum(x is not None for x in (a, b, c))
    known_A = sum(x is not None for x in (A, B, C))
    if known_s + known_A < 3 or known_s == 0:
        raise ValueError("Provide at least three values including one side.")

    note = ""

    # SSS
    if known_s == 3:
        assert a is not None and b is not None and c is not None
        if not (a + b > c and a + c > b and b + c > a):
            raise ValueError("Triangle inequality violated.")
        A = _law_of_cosines_angle(a, b, c)
        B = _law_of_cosines_angle(b, a, c)
        C = max(0.0, math.pi - A - B)
        return Triangle(a, b, c, A, B, C), note

    # ASA/AAS (two angles + one side)
    if known_A >= 2 and known_s == 1:
        if A is None: A = math.pi - (B or 0) - (C or 0)
        if B is None: B = math.pi - (A or 0) - (C or 0)
        if C is None: C = math.pi - (A or 0) - (B or 0)
        if A <= 0 or B <= 0 or C <= 0:
            raise ValueError("Angles must be positive and sum to 180°.")

        if a is not None:
            b = _law_of_sines_side(a, A, B)
            c = _law_of_sines_side(a, A, C)
        elif b is not None:
            a = _law_of_sines_side(b, B, A)
            c = _law_of_sines_side(b, B, C)
        else:
            c = c if c is not None else 0.0
            a = _law_of_sines_side(c, C, A)
            b = _law_of_sines_side(c, C, B)
        return Triangle(a, b, c, A, B, C), note

    # SAS (two sides + included angle)
    if known_s == 2 and known_A == 1:
        if A is not None and b is not None and c is not None:
            a = _law_of_cosines_side(b, c, A)
            B = _law_of_cosines_angle(b, a, c)
            C = max(0.0, math.pi - A - B)
            return Triangle(a, b, c, A, B, C), note
        if B is not None and a is not None and c is not None:
            b = _law_of_cosines_side(a, c, B)
            A = _law_of_cosines_angle(a, b, c)
            C = max(0.0, math.pi - A - B)
            return Triangle(a, b, c, A, B, C), note
        if C is not None and a is not None and b is not None:
            c = _law_of_cosines_side(a, b, C)
            A = _law_of_cosines_angle(a, b, c)
            B = max(0.0, math.pi - A - C)
            return Triangle(a, b, c, A, B, C), note

    # SSA (two sides + non-included angle): possible ambiguity
    pairs = [
        ("a", a, "A", A, "b", b),
        ("a", a, "A", A, "c", c),
        ("b", b, "B", B, "a", a),
        ("b", b, "B", B, "c", c),
        ("c", c, "C", C, "a", a),
        ("c", c, "C", C, "b", b),
    ]
    def ssa_try(side_known, ang_known, other_side):
        rhs = other_side * math.sin(ang_known) / max(1e-12, side_known)
        if rhs < -1.0 or rhs > 1.0:
            raise ValueError("No SSA solution.")
        t = math.asin(max(-1.0, min(1.0, rhs)))
        return t, math.pi - t

    for side_name, side_val, ang_name, ang_val, other_side_name, other_side_val in pairs:
        if side_val is not None and ang_val is not None and other_side_val is not None:
            try:
                t1, t2 = ssa_try(side_val, ang_val, other_side_val)
            except ValueError:
                continue

            # Build candidate triangles for both possibilities
            def build(sol_ang):
                A_, B_, C_ = A, B, C
                a_, b_, c_ = a, b, c
                # Assign solved angle
                if ang_name == "A":
                    if other_side_name == "b": B_ = sol_ang
                    else: C_ = sol_ang
                elif ang_name == "B":
                    if other_side_name == "a": A_ = sol_ang
                    else: C_ = sol_ang
                else:
                    if other_side_name == "a": A_ = sol_ang
                    else: B_ = sol_ang
                # complete third angle
                known = [x for x in (A_, B_, C_) if x is not None]
                if len(known) < 2: return None
                third = math.pi - sum(known)
                if third <= 0: return None
                if A_ is None: A_ = third
                elif B_ is None: B_ = third
                elif C_ is None: C_ = third
                # law of sines to fill sides using the known opposite pair
                if a_ is None: a_ = _law_of_sines_side(side_val, ang_val, A_)
                if b_ is None: b_ = _law_of_sines_side(side_val, ang_val, B_)
                if c_ is None: c_ = _law_of_sines_side(side_val, ang_val, C_)
                if not (a_ + b_ > c_ and a_ + c_ > b_ and b_ + c_ > a_):
                    return None
                return Triangle(a_, b_, c_, A_, B_, C_)

            tri1 = build(t1); tri2 = build(t2)
            if tri1 and tri2:
                note = "SSA ambiguity: two solutions; showing the acute-angle branch."
                # pick the one with smaller newly solved angle
                return (tri1 if t1 <= t2 else tri2), note
            if tri1: return tri1, note
            if tri2: return tri2, note

    raise ValueError("Inputs insufficient or inconsistent for a valid triangle.")


# ---------- Tool ----------

class Tool(QDialog):
    TITLE = "Triangle Solver & Drawer"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.TITLE)
        self.setMinimumWidth(760)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Inputs grid
        grid = QGridLayout()
        grid.addWidget(QLabel("Side a (BC):"), 0, 0); self.in_a = QLineEdit(); grid.addWidget(self.in_a, 0, 1)
        grid.addWidget(QLabel("Side b (AC):"), 1, 0); self.in_b = QLineEdit(); grid.addWidget(self.in_b, 1, 1)
        grid.addWidget(QLabel("Side c (AB):"), 2, 0); self.in_c = QLineEdit(); grid.addWidget(self.in_c, 2, 1)

        grid.addWidget(QLabel("Angle A (at A):"), 0, 2); self.in_A = QLineEdit(); grid.addWidget(self.in_A, 0, 3)
        grid.addWidget(QLabel("Angle B (at B):"), 1, 2); self.in_B = QLineEdit(); grid.addWidget(self.in_B, 1, 3)
        grid.addWidget(QLabel("Angle C (at C):"), 2, 2); self.in_C = QLineEdit(); grid.addWidget(self.in_C, 2, 3)

        grid.addWidget(QLabel("Angle units:"), 3, 0)
        self.ang_mode = QComboBox(); self.ang_mode.addItems(["Degrees", "Radians"])
        grid.addWidget(self.ang_mode, 3, 1)

        layout.addLayout(grid)

        # Buttons
        hb = QHBoxLayout()
        self.btn_solve = QPushButton("Solve & Draw")
        self.btn_clear = QPushButton("Clear")
        self.btn_export = QPushButton("Export Plot")
        hb.addWidget(self.btn_solve); hb.addWidget(self.btn_clear); hb.addWidget(self.btn_export)
        layout.addLayout(hb)

        # Figure
        self.fig = Figure(figsize=(6.2, 4.2), dpi=110)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)

        # Output label
        self.out_label = QLabel("")
        self.out_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.out_label)

        # Wire up
        self.btn_solve.clicked.connect(self.on_solve)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_export.clicked.connect(self.on_export)

    def _gather_inputs(self) -> Dict[str, Optional[float]]:
        return {
            "a": _safe_float(self.in_a.text()),
            "b": _safe_float(self.in_b.text()),
            "c": _safe_float(self.in_c.text()),
            "A": _safe_float(self.in_A.text()),
            "B": _safe_float(self.in_B.text()),
            "C": _safe_float(self.in_C.text()),
        }

    def on_clear(self):
        for w in (self.in_a, self.in_b, self.in_c, self.in_A, self.in_B, self.in_C):
            w.clear()
        self.out_label.setText("")
        self.fig.clear(); self.canvas.draw()

    def on_export(self):
        try:
            path = export_figure(self.fig, out_dir=IMAGES_DIR)
            QMessageBox.information(self, "Export", f"Plot exported to:\n{path}")
            add_log_entry(self.TITLE, action="Export", data={"image": str(path)})
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))
            add_log_entry(self.TITLE, action="ExportFailed", data={"error": str(e)})

    def on_solve(self):
        inputs = self._gather_inputs()
        mode = self.ang_mode.currentText()

        try:
            tri, note = _solve_triangle(inputs, mode)
        except Exception as e:
            self.out_label.setText(f"Error: {e}")
            add_log_entry(self.TITLE, action="SolveError", data={"error": str(e), "inputs": inputs})
            return

        # Compose textual results
        area = _heron_area(tri.a, tri.b, tri.c)
        txt = (
            f"Sides: a={tri.a:.6g}, b={tri.b:.6g}, c={tri.c:.6g}\n"
            f"Angles: A={_rad2deg(tri.A, mode):.6g}{'°' if mode=='Degrees' else ' rad'}, "
            f"B={_rad2deg(tri.B, mode):.6g}{'°' if mode=='Degrees' else ' rad'}, "
            f"C={_rad2deg(tri.C, mode):.6g}{'°' if mode=='Degrees' else ' rad'}\n"
            f"Perimeter: {tri.a + tri.b + tri.c:.6g}\n"
            f"Area (Heron): {area:.6g}"
        )
        if note:
            txt += f"\nNote: {note}"
        self.out_label.setText(txt)

        # Draw triangle
        self._draw_triangle(tri, mode)

        # Log
        add_log_entry(
            self.TITLE, action="Solve",
            data={
                "inputs": inputs,
                "results": {
                    "a": tri.a, "b": tri.b, "c": tri.c,
                    "A_deg": math.degrees(tri.A),
                    "B_deg": math.degrees(tri.B),
                    "C_deg": math.degrees(tri.C),
                    "area": area
                },
                "note": note
            },
            tags=["geometry", "triangle"]
        )

    def _draw_triangle(self, tri: Triangle, ang_mode: str):
        """
        Place A at (0,0), B at (c,0), compute C via side lengths.
        """

        a, b, c, A, B, C = tri.a, tri.b, tri.c, tri.A, tri.B, tri.C

        Ax, Ay = 0.0, 0.0
        Bx, By = c, 0.0
        denom = max(1e-12, 2.0 * c)
        Cx = (b*b + c*c - a*a) / denom
        temp = b*b - Cx*Cx
        Cy = math.sqrt(max(0.0, temp))

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_aspect("equal", adjustable="datalim")

        # Edges
        xs = [Ax, Bx, Cx, Ax]
        ys = [Ay, By, Cy, Ay]
        ax.plot(xs, ys)

        # Vertices
        ax.scatter([Ax, Bx, Cx], [Ay, By, Cy])

        # Vertex labels
        ax.text(Ax, Ay, " A", ha="left", va="top")
        ax.text(Bx, By, " B", ha="right", va="top")
        ax.text(Cx, Cy, " C", ha="left", va="bottom")

        # Side labels near midpoints
        def mid(p1, p2): return ((p1[0]+p2[0])/2.0, (p1[1]+p2[1])/2.0)
        mBC = mid((Bx, By), (Cx, Cy))  # a
        mAC = mid((Ax, Ay), (Cx, Cy))  # b
        mAB = mid((Ax, Ay), (Bx, By))  # c
        ax.text(mBC[0], mBC[1], f"a={a:.4g}", ha="center", va="bottom")
        ax.text(mAC[0], mAC[1], f"b={b:.4g}", ha="center", va="bottom")
        ax.text(mAB[0], mAB[1], f"c={c:.4g}", ha="center", va="bottom")

        # Angle labels (with small arcs)
        def angle_arc(center, start_vec, theta, radius, label):
            # Draw arc from start_vec direction, spanning +theta
            start = math.degrees(math.atan2(start_vec[1], start_vec[0]))
            arc = Arc(center, 2*radius, 2*radius, angle=0, theta1=start, theta2=start+math.degrees(theta),
                      lw=1.2, alpha=0.6)
            ax.add_patch(arc)
            # place label slightly outside arc
            lx = center[0] + (radius*1.15) * math.cos(math.radians(start) + theta/2)
            ly = center[1] + (radius*1.15) * math.sin(math.radians(start) + theta/2)
            ax.text(lx, ly, label, ha="center", va="center", fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))

        # Scale-based arc radius
        span = max(max(xs)-min(xs), max(ys)-min(ys), 1.0)
        r = 0.12 * span

        # At A: sides AB (to the right) and AC (to C)
        angle_arc((Ax, Ay), (1, 0), A, r,
                  f"A={_rad2deg(A, ang_mode):.3g}{'°' if ang_mode=='Degrees' else ' rad'}")
        # At B: sides BA (to the left) and BC (to C)
        angle_arc((Bx, By), (-1, 0), B, r,
                  f"B={_rad2deg(B, ang_mode):.3g}{'°' if ang_mode=='Degrees' else ' rad'}")
        # At C: use vectors from C toward A and B (we start from CA direction)
        vCA = (Ax - Cx, Ay - Cy)
        angle_arc((Cx, Cy), vCA, C, r,
                  f"C={_rad2deg(C, ang_mode):.3g}{'°' if ang_mode=='Degrees' else ' rad'}")

        # Limits
        margin = 0.18 * span
        ax.set_xlim(min(Ax, Bx, Cx) - margin, max(Ax, Bx, Cx) + margin)
        ax.set_ylim(min(Ay, By, Cy) - margin, max(Ay, By, Cy) + margin)

        ax.set_title("Triangle (sides a,b,c opposite A,B,C)")
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()
