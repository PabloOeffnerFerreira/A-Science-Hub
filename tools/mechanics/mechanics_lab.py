from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Dict

import numpy as np

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTabWidget, QWidget, QSizePolicy
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


# ---------------- Shared units helpers ----------------

def _safe_float(s: str) -> Optional[float]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def _to_meters(x: float, unit: str) -> float:
    if unit == "m": return x
    if unit == "km": return x * 1000.0
    if unit == "mile": return x * 1609.344
    if unit == "ft": return x * 0.3048
    return x

def _to_seconds(x: float, unit: str) -> float:
    if unit == "s": return x
    if unit == "min": return x * 60.0
    if unit == "hr": return x * 3600.0
    return x

def _speed_to_mps(v: float, unit: str) -> float:
    if unit == "m/s": return v
    if unit == "km/h": return v / 3.6
    if unit == "mph": return v * 0.44704
    return v

def _speed_from_mps(v: float, unit: str) -> float:
    if unit == "m/s": return v
    if unit == "km/h": return v * 3.6
    if unit == "mph": return v / 0.44704
    return v

def _area_to_m2(A: float, unit: str) -> float:
    if unit == "m²": return A
    if unit == "cm²": return A / 1e4
    if unit == "ft²": return A * 0.09290304
    return A

def _mass_to_kg(m: float, unit: str) -> float:
    if unit == "kg": return m
    if unit == "g": return m / 1000.0
    if unit == "lb": return m * 0.45359237
    return m

def _rho_to_kg_m3(rho: float, unit: str) -> float:
    if unit == "kg/m³": return rho
    if unit == "g/cm³": return rho * 1000.0
    return rho

def _height_to_m(h: float, unit: str) -> float:
    if unit == "m": return h
    if unit == "ft": return h * 0.3048
    return h

def _angle_to_rad(theta: float, unit: str) -> float:
    if unit == "degrees": return math.radians(theta)
    return theta


# ---------------- Shared state model ----------------

@dataclass
class Inputs:
    distance: Optional[float] = None
    distance_unit: str = "m"
    time: Optional[float] = None
    time_unit: str = "s"
    v0: Optional[float] = None
    v0_unit: str = "m/s"
    dv: Optional[float] = None
    dv_unit: str = "m/s"
    mass: Optional[float] = None
    mass_unit: str = "kg"
    area: Optional[float] = None
    area_unit: str = "m²"
    rho: Optional[float] = None
    rho_unit: str = "kg/m³"
    Cd: Optional[float] = None
    height0: Optional[float] = None
    height0_unit: str = "m"
    theta: Optional[float] = None
    theta_unit: str = "degrees"


# ---------------- Main Tool ----------------

class Tool(QDialog):
    TITLE = "Mechanics Lab"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.TITLE)
        self.setMinimumWidth(940)
        self.inputs = Inputs()

        self._build_ui()
        self._wire()

    # ----- UI -----
    def _build_ui(self):
        root = QVBoxLayout(self)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # Tab 1: Shared Inputs
        self.tab_inputs = QWidget(); self.tabs.addTab(self.tab_inputs, "Inputs")
        self._build_inputs_tab()

        # Tab 2: Speed & Acceleration
        self.tab_sa = QWidget(); self.tabs.addTab(self.tab_sa, "Speed & Acceleration")
        self._build_speed_accel_tab()

        # Tab 3: Kinetic Energy
        self.tab_ke = QWidget(); self.tabs.addTab(self.tab_ke, "Kinetic Energy")
        self._build_ke_tab()

        # Tab 4: Drag Force
        self.tab_drag = QWidget(); self.tabs.addTab(self.tab_drag, "Drag Force")
        self._build_drag_tab()

        # Tab 5: Projectile Motion
        self.tab_proj = QWidget(); self.tabs.addTab(self.tab_proj, "Projectile Motion")
        self._build_projectile_tab()

    def _build_inputs_tab(self):
        lay = QGridLayout(self.tab_inputs)

        # Distance & time (average speed)
        lay.addWidget(QLabel("Distance:"), 0, 0)
        self.in_dist = QLineEdit(); self.in_dist.setPlaceholderText("e.g., 100")
        lay.addWidget(self.in_dist, 0, 1)
        self.in_dist_u = QComboBox(); self.in_dist_u.addItems(["m", "km", "mile", "ft"])
        lay.addWidget(self.in_dist_u, 0, 2)

        lay.addWidget(QLabel("Time:"), 1, 0)
        self.in_time = QLineEdit(); self.in_time.setPlaceholderText("e.g., 10")
        lay.addWidget(self.in_time, 1, 1)
        self.in_time_u = QComboBox(); self.in_time_u.addItems(["s", "min", "hr"])
        lay.addWidget(self.in_time_u, 1, 2)

        # Speed (for KE/Drag/Projectile)
        lay.addWidget(QLabel("Speed v or v₀:"), 2, 0)
        self.in_v0 = QLineEdit(); self.in_v0.setPlaceholderText("e.g., 20")
        lay.addWidget(self.in_v0, 2, 1)
        self.in_v0_u = QComboBox(); self.in_v0_u.addItems(["m/s", "km/h", "mph"])
        lay.addWidget(self.in_v0_u, 2, 2)

        # Δv (for acceleration)
        lay.addWidget(QLabel("Δv:"), 3, 0)
        self.in_dv = QLineEdit(); self.in_dv.setPlaceholderText("e.g., 10")
        lay.addWidget(self.in_dv, 3, 1)
        self.in_dv_u = QComboBox(); self.in_dv_u.addItems(["m/s", "km/h", "mph"])
        lay.addWidget(self.in_dv_u, 3, 2)

        # Mass
        lay.addWidget(QLabel("Mass m:"), 4, 0)
        self.in_m = QLineEdit(); self.in_m.setPlaceholderText("e.g., 1")
        lay.addWidget(self.in_m, 4, 1)
        self.in_m_u = QComboBox(); self.in_m_u.addItems(["kg", "g", "lb"])
        lay.addWidget(self.in_m_u, 4, 2)

        # Fluid density
        lay.addWidget(QLabel("Fluid density ρ:"), 5, 0)
        self.in_rho = QLineEdit(); self.in_rho.setPlaceholderText("e.g., 1.225")
        lay.addWidget(self.in_rho, 5, 1)
        self.in_rho_u = QComboBox(); self.in_rho_u.addItems(["kg/m³", "g/cm³"])
        lay.addWidget(self.in_rho_u, 5, 2)

        # Drag coeff & area
        lay.addWidget(QLabel("Drag coefficient C_d:"), 6, 0)
        self.in_Cd = QLineEdit(); self.in_Cd.setPlaceholderText("e.g., 1.0")
        lay.addWidget(self.in_Cd, 6, 1)

        lay.addWidget(QLabel("Reference area A:"), 7, 0)
        self.in_A = QLineEdit(); self.in_A.setPlaceholderText("e.g., 0.5")
        lay.addWidget(self.in_A, 7, 1)
        self.in_A_u = QComboBox(); self.in_A_u.addItems(["m²", "cm²", "ft²"])
        lay.addWidget(self.in_A_u, 7, 2)

        # Projectile: initial height & angle
        lay.addWidget(QLabel("Initial height h₀:"), 8, 0)
        self.in_h0 = QLineEdit(); self.in_h0.setPlaceholderText("e.g., 0")
        lay.addWidget(self.in_h0, 8, 1)
        self.in_h0_u = QComboBox(); self.in_h0_u.addItems(["m", "ft"])
        lay.addWidget(self.in_h0_u, 8, 2)

        lay.addWidget(QLabel("Launch angle θ:"), 9, 0)
        self.in_theta = QLineEdit(); self.in_theta.setPlaceholderText("e.g., 45")
        lay.addWidget(self.in_theta, 9, 1)
        self.in_theta_u = QComboBox(); self.in_theta_u.addItems(["degrees", "radians"])
        lay.addWidget(self.in_theta_u, 9, 2)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_apply = QPushButton("Apply to Tabs")
        self.btn_prefill = QPushButton("Prefill (debug)")
        btn_row.addWidget(self.btn_apply)
        btn_row.addWidget(self.btn_prefill)
        lay.addLayout(btn_row, 10, 0, 1, 3)

    def _build_speed_accel_tab(self):
        w = self.tab_sa
        lay = QVBoxLayout(w)

        # Controls row
        r = QHBoxLayout()
        r.addWidget(QLabel("Output speed unit:"))
        self.sa_speed_out_u = QComboBox(); self.sa_speed_out_u.addItems(["m/s", "km/h", "mph"])
        r.addWidget(self.sa_speed_out_u)
        r.addWidget(QLabel("Time unit for Δv/t:"))
        self.sa_time_u = QComboBox(); self.sa_time_u.addItems(["s", "min", "hr"])
        r.addWidget(self.sa_time_u)
        lay.addLayout(r)

        # Results
        self.sa_out = QLabel("")
        self.sa_out.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.sa_out)

        # Simple figure: velocity-time line from v0, a over t (if inputs allow)
        self.sa_fig = Figure(figsize=(7.4, 3.8), dpi=110)
        self.sa_canvas = FigureCanvas(self.sa_fig)
        lay.addWidget(NavigationToolbar(self.sa_canvas, self))
        self.sa_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(self.sa_canvas)

    def _build_ke_tab(self):
        w = self.tab_ke
        lay = QVBoxLayout(w)

        r = QHBoxLayout()
        self.btn_export_ke = QPushButton("Export Plot")
        r.addWidget(self.btn_export_ke)
        lay.addLayout(r)

        self.ke_out = QLabel("")
        self.ke_out.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.ke_out)

        # Figure: E_k(v) curve over a range around v0
        self.ke_fig = Figure(figsize=(7.4, 3.8), dpi=110)
        self.ke_canvas = FigureCanvas(self.ke_fig)
        lay.addWidget(NavigationToolbar(self.ke_canvas, self))
        self.ke_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(self.ke_canvas)

    def _build_drag_tab(self):
        w = self.tab_drag
        lay = QVBoxLayout(w)

        r = QHBoxLayout()
        self.btn_export_drag = QPushButton("Export Plot")
        r.addWidget(self.btn_export_drag)
        lay.addLayout(r)

        self.drag_out = QLabel("")
        self.drag_out.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.drag_out)

        # Figure: Drag vs speed
        self.drag_fig = Figure(figsize=(7.4, 3.8), dpi=110)
        self.drag_canvas = FigureCanvas(self.drag_fig)
        lay.addWidget(NavigationToolbar(self.drag_canvas, self))
        self.drag_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(self.drag_canvas)

    def _build_projectile_tab(self):
        w = self.tab_proj
        lay = QVBoxLayout(w)

        r = QHBoxLayout()
        self.btn_export_proj = QPushButton("Export Plot")
        r.addWidget(self.btn_export_proj)
        lay.addLayout(r)

        self.proj_out = QLabel("")
        self.proj_out.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.proj_out)

        # Figure: trajectory
        self.proj_fig = Figure(figsize=(7.4, 4.2), dpi=110)
        self.proj_canvas = FigureCanvas(self.proj_fig)
        lay.addWidget(NavigationToolbar(self.proj_canvas, self))
        self.proj_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(self.proj_canvas)

    # ----- wire -----
    def _wire(self):
        self.btn_apply.clicked.connect(self._apply_and_compute_all)
        self.btn_prefill.clicked.connect(self._prefill_and_apply)

        # Exports
        self.btn_export_ke.clicked.connect(lambda: export_figure(self.ke_fig, out_dir=IMAGES_DIR))
        self.btn_export_drag.clicked.connect(lambda: export_figure(self.drag_fig, out_dir=IMAGES_DIR))
        self.btn_export_proj.clicked.connect(lambda: export_figure(self.proj_fig, out_dir=IMAGES_DIR))

        # Optional: live re-compute when units toggled in SA tab
        self.sa_speed_out_u.currentIndexChanged.connect(self._compute_speed_accel)
        self.sa_time_u.currentIndexChanged.connect(self._compute_speed_accel)

    # ----- input helpers -----
    def _gather_inputs_from_widgets(self) -> Inputs:
        return Inputs(
            distance=_safe_float(self.in_dist.text()), distance_unit=self.in_dist_u.currentText(),
            time=_safe_float(self.in_time.text()), time_unit=self.in_time_u.currentText(),
            v0=_safe_float(self.in_v0.text()), v0_unit=self.in_v0_u.currentText(),
            dv=_safe_float(self.in_dv.text()), dv_unit=self.in_dv_u.currentText(),
            mass=_safe_float(self.in_m.text()), mass_unit=self.in_m_u.currentText(),
            rho=_safe_float(self.in_rho.text()), rho_unit=self.in_rho_u.currentText(),
            Cd=_safe_float(self.in_Cd.text()),
            area=_safe_float(self.in_A.text()), area_unit=self.in_A_u.currentText(),
            height0=_safe_float(self.in_h0.text()), height0_unit=self.in_h0_u.currentText(),
            theta=_safe_float(self.in_theta.text()), theta_unit=self.in_theta_u.currentText(),
        )

    def _apply_and_compute_all(self):
        self.inputs = self._gather_inputs_from_widgets()
        add_log_entry(self.TITLE, action="ApplyInputs", data=self.inputs.__dict__)
        # Auto compute on apply
        self._compute_speed_accel()
        self._compute_ke()
        self._compute_drag()
        self._compute_projectile()

    def _prefill_and_apply(self):
        # Prefill common values (debug convenience)
        self.in_dist.setText("100"); self.in_dist_u.setCurrentText("m")
        self.in_time.setText("10");  self.in_time_u.setCurrentText("s")
        self.in_v0.setText("20");    self.in_v0_u.setCurrentText("m/s")
        self.in_dv.setText("10");    self.in_dv_u.setCurrentText("m/s")
        self.in_m.setText("1");      self.in_m_u.setCurrentText("kg")
        self.in_rho.setText("1.225"); self.in_rho_u.setCurrentText("kg/m³")
        self.in_Cd.setText("1.0")
        self.in_A.setText("0.5");    self.in_A_u.setCurrentText("m²")
        self.in_h0.setText("0");     self.in_h0_u.setCurrentText("m")
        self.in_theta.setText("45"); self.in_theta_u.setCurrentText("degrees")

        self._apply_and_compute_all()

    # ----- computations -----
    def _compute_speed_accel(self):
        inp = self.inputs
        # Average speed if distance & time present
        speed_txt = ""
        if inp.distance is not None and inp.time is not None:
            d_m = _to_meters(inp.distance, inp.distance_unit)
            t_s = _to_seconds(inp.time, inp.time_unit)
            if t_s == 0:
                speed_txt = "Average speed: undefined (t=0)."
            else:
                v_mps = d_m / t_s
                v_out = _speed_from_mps(v_mps, self.sa_speed_out_u.currentText())
                speed_txt = f"Average speed = {v_out:.6g} {self.sa_speed_out_u.currentText()}"

        # Acceleration if Δv & time present
        accel_txt = ""
        if inp.dv is not None and inp.time is not None:
            dv_ms = _speed_to_mps(inp.dv, inp.dv_unit)
            t_s = _to_seconds(inp.time, inp.time_unit)
            if t_s == 0:
                accel_txt = "Acceleration: undefined (t=0)."
            else:
                a = dv_ms / t_s
                accel_txt = f"Acceleration a = {a:.6g} m/s²"

        # Velocity-time simple line if v0 & a known
        self.sa_fig.clear()
        ax = self.sa_fig.add_subplot(111)
        if inp.v0 is not None and inp.dv is not None and inp.time is not None:
            v0 = _speed_to_mps(inp.v0, inp.v0_unit)
            dv_ms = _speed_to_mps(inp.dv, inp.dv_unit)
            t_total = _to_seconds(inp.time, inp.time_unit)
            if t_total > 0:
                a = dv_ms / t_total
                ts = np.linspace(0, t_total, 300)
                vs = v0 + a * ts
                ax.plot(ts, vs)
                ax.set_xlabel("t (s)"); ax.set_ylabel("v (m/s)"); ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, "Provide v₀, Δv, and time to draw v(t).",
                    ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()

        self.sa_fig.tight_layout(); self.sa_canvas.draw()

        show_txt = []
        if speed_txt: show_txt.append(speed_txt)
        if accel_txt: show_txt.append(accel_txt)
        if not show_txt: show_txt.append("Provide distance & time for speed, and/or Δv & time for acceleration.")
        self.sa_out.setText("\n".join(show_txt))

        add_log_entry(self.TITLE, action="SpeedAccel",
                      data={"speed_text": speed_txt, "accel_text": accel_txt})

    def _compute_ke(self):
        inp = self.inputs
        if inp.mass is None or inp.v0 is None:
            self.ke_out.setText("Provide mass and speed v.")
            self.ke_fig.clear(); self.ke_canvas.draw()
            return

        m = _mass_to_kg(inp.mass, inp.mass_unit)
        v0 = _speed_to_mps(inp.v0, inp.v0_unit)
        KE0 = 0.5 * m * v0 * v0
        self.ke_out.setText(f"E_k(v₀) = {KE0:.6g} J")

        # Plot E_k vs v around v0
        self.ke_fig.clear()
        ax = self.ke_fig.add_subplot(111)
        vmax = max(1.0, v0 * 2.0)
        vs = np.linspace(0, vmax, 300)
        kes = 0.5 * m * vs * vs
        ax.plot(vs, kes)
        ax.set_xlabel("v (m/s)"); ax.set_ylabel("E_k (J)"); ax.grid(True, alpha=0.3)
        self.ke_fig.tight_layout(); self.ke_canvas.draw()

        add_log_entry(self.TITLE, action="KineticEnergy",
                      data={"m_kg": m, "v0_mps": v0, "KE0_J": KE0})

    def _compute_drag(self):
        inp = self.inputs
        needed = [inp.rho, inp.v0, inp.Cd, inp.area]
        if any(x is None for x in needed):
            self.drag_out.setText("Provide ρ, v, C_d, and A.")
            self.drag_fig.clear(); self.drag_canvas.draw()
            return

        rho = _rho_to_kg_m3(inp.rho, inp.rho_unit)
        v0 = _speed_to_mps(inp.v0, inp.v0_unit)
        Cd = float(inp.Cd or 0.0)
        A = _area_to_m2(inp.area, inp.area_unit)
        F0 = 0.5 * rho * v0 * v0 * Cd * A
        self.drag_out.setText(f"F_d(v₀) = {F0:.6g} N")

        # Plot drag vs speed
        self.drag_fig.clear()
        ax = self.drag_fig.add_subplot(111)
        vmax = max(1.0, v0 * 2.0)
        vs = np.linspace(0, vmax, 300)
        Fd = 0.5 * rho * vs * vs * Cd * A
        ax.plot(vs, Fd)
        ax.set_xlabel("v (m/s)"); ax.set_ylabel("F_d (N)"); ax.grid(True, alpha=0.3)
        self.drag_fig.tight_layout(); self.drag_canvas.draw()

        add_log_entry(self.TITLE, action="DragForce",
                      data={"rho": rho, "v0_mps": v0, "Cd": Cd, "A_m2": A, "Fd_v0": F0})

    def _compute_projectile(self):
        inp = self.inputs
        if inp.v0 is None or inp.theta is None:
            self.proj_out.setText("Provide v₀ and θ (and optional h₀).")
            self.proj_fig.clear(); self.proj_canvas.draw()
            return

        v = _speed_to_mps(inp.v0, inp.v0_unit)
        th = _angle_to_rad(inp.theta, inp.theta_unit)
        h0 = _height_to_m(inp.height0 or 0.0, inp.height0_unit)

        g = 9.81
        a = -0.5 * g; b = v * math.sin(th); c = h0
        disc = b*b - 4*a*c
        self.proj_fig.clear()
        ax = self.proj_fig.add_subplot(111)
        if disc < 0:
            self.proj_out.setText("No real impact (check inputs).")
            self.proj_canvas.draw()
            return
        t1 = (-b + math.sqrt(disc)) / (2*a)
        t2 = (-b - math.sqrt(disc)) / (2*a)
        T = max(t1, t2)
        R = v * math.cos(th) * T
        Hmax = h0 + (v*v) * (math.sin(th)**2) / (2*g)
        vx = v * math.cos(th)
        vy = v * math.sin(th) - g * T
        vimp = math.sqrt(vx*vx + vy*vy)

        xs = np.linspace(0, max(1e-9, R), 600)
        ys = h0 + xs * math.tan(th) - (g * xs * xs) / (2 * (v * math.cos(th))**2)
        ys = np.maximum(ys, 0)

        ax.plot(xs, ys)
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)"); ax.grid(True, alpha=0.3)
        self.proj_fig.tight_layout(); self.proj_canvas.draw()

        msg = (f"Range = {R:.3f} m | Flight time = {T:.3f} s | Max height = {Hmax:.3f} m\n"
               f"Impact speed = {vimp:.3f} m/s (vx={vx:.3f}, vy={vy:.3f})")
        self.proj_out.setText(msg)

        add_log_entry(self.TITLE, action="Projectile",
                      data={"v0_mps": v, "theta_rad": th, "h0_m": h0, "R": R, "T": T, "Hmax": Hmax, "vimp": vimp})
