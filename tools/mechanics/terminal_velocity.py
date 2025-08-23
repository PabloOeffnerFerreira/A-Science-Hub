# tools/mechanics/terminal_velocity.py

import math
from dataclasses import dataclass

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QWidget, QTabWidget
)

# 2D stack
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

# 3D stack (optional)
try:
    import numpy as np
    import pyqtgraph as pg
    import pyqtgraph.opengl as gl
    PG_OK = True
except Exception:
    PG_OK = False
    np = None
    pg = None
    gl = None

from core.data.functions.log import add_log_entry
from core.data.functions.image_export import export_figure
try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


# Map physics meters to GL units, so motion is visibly large
SCENE_SCALE = 0.35


@dataclass
class SimParams:
    mass: float        # kg
    area: float        # m^2
    height: float      # m
    rho: float         # kg/m^3
    Cd: float          # dimensionless
    g: float = 9.81    # m/s^2
    dt: float = 0.01   # s


class Tool(QDialog):
    TITLE = "Terminal Velocity"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(840)
        self.resize(980, 720)

        # Simulation state
        self.timer = QTimer(self)
        self.timer.setInterval(16)  # ~60 FPS
        self.timer.timeout.connect(self._tick)

        self._running = False
        self._t = 0.0
        self._y = 0.0
        self._v = 0.0
        self._vt = 0.0  # terminal velocity cached
        self._params: SimParams | None = None
        self._trail_pts = []

        self._build_ui()
        self._wire_signals()

    # ---------- UI ----------
    def _build_ui(self):
        main = QVBoxLayout(self)

        def row(label_text, default_text="", combo_items=None):
            hb = QHBoxLayout()
            hb.addWidget(QLabel(label_text))
            edit = QLineEdit(default_text) if default_text != "" else None
            combo = QComboBox() if combo_items else None
            if edit:
                hb.addWidget(edit)
            if combo:
                combo.addItems(combo_items)
                hb.addWidget(combo)
            return hb, edit, combo

        # Mass
        row_mass, self.mass_edit, self.mass_unit = row("Mass:", "1.0", ["kg", "lb"])
        main.addLayout(row_mass)

        # Area
        row_area, self.area_edit, self.area_unit = row("Cross-sectional Area:", "0.5", ["m²", "cm²", "in²"])
        main.addLayout(row_area)

        # Height
        row_height, self.height_edit, self.height_unit = row("Height:", "100", ["m", "ft"])
        main.addLayout(row_height)

        # Air density / altitude
        hb_air = QHBoxLayout()
        hb_air.addWidget(QLabel("Air Density (kg/m³) or Altitude (m):"))
        self.air_mode = QComboBox()
        self.air_mode.addItems(["Air Density", "Altitude", "Custom"])
        self.air_value = QLineEdit("1.225")
        hb_air.addWidget(self.air_mode)
        hb_air.addWidget(self.air_value)
        main.addLayout(hb_air)

        # Drag coefficient
        hb_cd = QHBoxLayout()
        hb_cd.addWidget(QLabel("Drag Coefficient:"))
        self.cd_preset = QComboBox()
        self.cd_preset.addItems([
            "Sphere (0.47)",
            "Flat Plate (1.28)",
            "Cylinder (1.2)",
            "Streamlined Body (0.04)",
            "Custom",
        ])
        self.cd_edit = QLineEdit("1.0")
        hb_cd.addWidget(self.cd_preset)
        hb_cd.addWidget(self.cd_edit)
        main.addLayout(hb_cd)

        # Options
        opts = QHBoxLayout()
        self.chk_compare_no_drag = QCheckBox("Compare with no drag")
        self.chk_trail = QCheckBox("Show trail")
        self.chk_trail.setChecked(True)

        self.sim_speed = QComboBox()
        self.sim_speed.addItems(["1x", "2x", "5x", "10x"])
        self.sim_speed.setCurrentIndex(2)  # 5x

        opts.addWidget(self.chk_compare_no_drag)
        opts.addWidget(self.chk_trail)
        opts.addWidget(QLabel("Sim speed:"))
        opts.addWidget(self.sim_speed)
        main.addLayout(opts)

        # Controls
        ctrls = QHBoxLayout()
        self.btn_calc = QPushButton("Calculate")
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_export = QPushButton("Export Current View")
        ctrls.addWidget(self.btn_calc)
        ctrls.addWidget(self.btn_start)
        ctrls.addWidget(self.btn_stop)
        ctrls.addWidget(self.btn_export)
        main.addLayout(ctrls)

        self.result_label = QLabel("")
        main.addWidget(self.result_label)

        # Tabs
        self.tabs = QTabWidget()
        main.addWidget(self.tabs)

        # 2D tab
        tab2d = QWidget(); v2d = QVBoxLayout(tab2d)
        self.fig = Figure(figsize=(6, 4), dpi=110)
        self.canvas = FigureCanvas(self.fig)
        v2d.addWidget(NavigationToolbar(self.canvas, self))
        v2d.addWidget(self.canvas)
        self.tabs.addTab(tab2d, "2D")

        # 3D tab
        if PG_OK:
            tab3d = QWidget(); v3d = QVBoxLayout(tab3d)
            self.view3d = gl.GLViewWidget()
            self.view3d.setBackgroundColor((18, 18, 18))
            self.view3d.setCameraPosition(distance=85, elevation=18, azimuth=25)
            v3d.addWidget(self.view3d)

            # HUD label (Qt, not GL)
            self.hud_label = QLabel(self.view3d)
            self.hud_label.setStyleSheet("color: white; background: transparent; padding: 0;")
            font = self.hud_label.font()
            font.setPointSize(10)
            self.hud_label.setFont(font)
            self.hud_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.hud_label.move(8, 8)
            self.hud_label.raise_()

            self.tabs.addTab(tab3d, "3D")

            # Ground grid
            grid = gl.GLGridItem()
            grid.scale(5, 5, 1)
            self.view3d.addItem(grid)

            # Falling body
            e_mesh = gl.MeshData.sphere(rows=16, cols=16, radius=1.2)
            self.body = gl.GLMeshItem(meshdata=e_mesh, smooth=True, color=(0.8, 0.85, 0.95, 1.0), shader='shaded')
            self.view3d.addItem(self.body)

            # No-drag comparator
            self.body_nodrag = gl.GLMeshItem(meshdata=e_mesh, smooth=True, color=(0.9, 0.6, 0.6, 0.55), shader='shaded')
            self.body_nodrag.setVisible(False)
            self.view3d.addItem(self.body_nodrag)

            # Trail
            self.trail = gl.GLLinePlotItem(pos=np.zeros((1, 3)), width=2.0, antialias=True)
            self.trail.setVisible(self.chk_trail.isChecked())
            self.view3d.addItem(self.trail)
        else:
            self.view3d = None
            self.hud_label = None
            self.body = None
            self.body_nodrag = None
            self.trail = None

    def _wire_signals(self):
        self.btn_calc.clicked.connect(self.calculate)
        self.btn_start.clicked.connect(self.start_sim)
        self.btn_stop.clicked.connect(self.stop_sim)
        self.btn_export.clicked.connect(self._export_current_view)

        self.air_mode.currentTextChanged.connect(self._update_air_mode)
        self.cd_preset.currentTextChanged.connect(self._update_cd_preset)
        self.chk_trail.toggled.connect(self._toggle_trail)
        self._update_air_mode()
        self._update_cd_preset()

    # ---------- helpers ----------
    def _gl_item_visible(self, item) -> bool:
        try:
            return bool(item is not None and getattr(item, "opts", {}).get("visible", True))
        except Exception:
            return False

    def _toggle_trail(self, checked: bool):
        if self.trail is not None:
            self.trail.setVisible(checked)

    def _update_air_mode(self):
        mode = self.air_mode.currentText()
        if mode == "Air Density":
            self.air_value.setText("1.225")
            self.air_value.setEnabled(False)
        elif mode == "Altitude":
            self.air_value.setText("0")
            self.air_value.setEnabled(True)
        else:
            self.air_value.setEnabled(True)

    def _update_cd_preset(self):
        preset = self.cd_preset.currentText()
        mapping = {
            "Sphere (0.47)": "0.47",
            "Flat Plate (1.28)": "1.28",
            "Cylinder (1.2)": "1.2",
            "Streamlined Body (0.04)": "0.04",
        }
        if preset in mapping:
            self.cd_edit.setText(mapping[preset])
            self.cd_edit.setEnabled(False)
        else:
            self.cd_edit.setEnabled(True)

    def _rho_from_altitude(self, h_m: float) -> float:
        if h_m < 0:
            h_m = 0
        if h_m < 11000:
            T0 = 288.15
            L = 0.0065
            p0 = 101325.0
            R = 8.31447
            M = 0.0289644
            g = 9.80665
            T = T0 - L * h_m
            p = p0 * (T / T0) ** (g * M / (R * L))
            rho = p * M / (R * T)
        else:
            rho = 0.364
        return rho

    def _parse_inputs_to_params(self) -> SimParams:
        # mass
        mass = float(self.mass_edit.text())
        if self.mass_unit.currentText() == "lb":
            mass *= 0.45359237
        # area
        area = float(self.area_edit.text())
        aunit = self.area_unit.currentText()
        if aunit == "cm²":
            area *= 1e-4
        elif aunit == "in²":
            area *= 0.00064516
        # height
        height = float(self.height_edit.text())
        if self.height_unit.currentText() == "ft":
            height *= 0.3048
        # air density
        mode = self.air_mode.currentText()
        aval = float(self.air_value.text())
        if mode == "Altitude":
            rho = self._rho_from_altitude(aval)
        elif mode == "Air Density":
            rho = 1.225
        else:
            rho = aval
        # drag
        Cd = float(self.cd_edit.text())
        return SimParams(mass=mass, area=area, height=height, rho=rho, Cd=Cd)

    # ---------- physics ----------
    @staticmethod
    def _terminal_velocity(params: SimParams) -> float:
        # v_t = sqrt((2mg)/(rho*A*Cd))
        denom = max(1e-12, params.rho * params.area * params.Cd)
        return math.sqrt((2 * params.mass * params.g) / denom)

    def _integrate_descent(self, params: SimParams, include_drag=True):
        # Euler integration to ground (for 2D plotting)
        t = 0.0
        y = params.height
        v = 0.0
        times, velocities, heights = [], [], []
        while y > 0.0:
            Fg = params.mass * params.g
            if include_drag:
                Fd = 0.5 * params.rho * v * v * params.Cd * params.area
                a = (Fg - Fd) / params.mass if v >= 0 else (Fg + Fd) / params.mass
            else:
                a = params.g
            v += a * params.dt
            y = max(0.0, y - max(v, 0.0) * params.dt)
            t += params.dt
            times.append(t)
            velocities.append(v)
            heights.append(y)
            if t > 36000:
                break
        return t, times, velocities, heights

    def _analytic_state(self, params: SimParams, t: float):
        vt = self._vt if self._vt > 0 else self._terminal_velocity(params)
        # x is dimensionless
        x = params.g * t / max(1e-12, vt)
        v = vt * math.tanh(x)  # v(t)
        y = params.height - (vt * vt / params.g) * math.log(math.cosh(x))  # y(t) from rest at height h
        return max(0.0, v), max(0.0, y)

    def _steps_per_frame(self) -> int:
        mapping = {"1x": 1, "2x": 2, "5x": 5, "10x": 10}
        return mapping.get(self.sim_speed.currentText(), 5)

    # ---------- actions ----------
    def calculate(self):
        try:
            params = self._parse_inputs_to_params()
        except Exception:
            self.result_label.setText("Please enter valid numbers.")
            add_log_entry("Terminal Velocity", action="invalid_input")
            return

        vt = self._terminal_velocity(params)
        t_drag, times, v_euler, heights = self._integrate_descent(params, include_drag=True)
        t_nodrag = math.sqrt(2 * max(params.height, 0.0) / params.g)

        # 2D: Velocity vs Time
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(times, v_euler, label="With drag (Euler)")

        # Analytic overlay for verification
        if times:
            t_ana = [i * params.dt for i in range(len(times))]
            v_ana = [vt * math.tanh(params.g * t / vt) for t in t_ana]
            ax.plot(t_ana, v_ana, linestyle=":", label="With drag (analytic)")
        if self.chk_compare_no_drag.isChecked():
            t_line = [i * params.dt for i in range(int(t_nodrag / params.dt) + 1)]
            v_line = [params.g * t for t in t_line]
            ax.plot(t_line, v_line, linestyle="--", label="No drag")

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Velocity (m/s)")
        ax.set_title("Velocity vs Time")
        ax.grid(True)
        ax.legend(loc="best")
        self.canvas.draw()

        msg = (
            f"Terminal Velocity ≈ {vt:.2f} m/s\n"
            f"Fall Time with drag (Euler) ≈ {t_drag:.2f} s\n"
            f"Fall Time without drag ≈ {t_nodrag:.2f} s"
        )
        self.result_label.setText(msg)

        # Save 2D plot
        try:
            img_path = export_figure(self.fig, out_dir=IMAGES_DIR)
            self.result_label.setText(msg + f"\nPlot saved to {img_path}")
        except Exception:
            pass

        add_log_entry(
            "Terminal Velocity",
            action="Compute",
            data={
                "inputs": {
                    "mass_kg": params.mass,
                    "area_m2": params.area,
                    "height_m": params.height,
                    "Cd": params.Cd,
                    "rho": params.rho,
                },
                "results": {
                    "v_terminal_m_s": vt,
                    "fall_time_with_drag_s": t_drag,
                    "fall_time_no_drag_s": t_nodrag,
                },
            },
            tags=["physics", "mechanics", "drag"],
        )

        # Seed 3D state
        self._params = params
        self._vt = vt
        self._reset_anim_state()

    def start_sim(self):
        if self.view3d is None:
            self.result_label.setText("3D view not available on this system.")
            return
        if self._params is None:
            self.calculate()
            if self._params is None:
                return

        if self.chk_compare_no_drag.isChecked() and self.body_nodrag is not None:
            self.body_nodrag.setVisible(True)
        else:
            if self.body_nodrag is not None:
                self.body_nodrag.setVisible(False)

        self._running = True
        self.timer.start()

    def stop_sim(self):
        self._running = False
        self.timer.stop()

    def _reset_anim_state(self):
        if self.view3d is None or self._params is None:
            return
        self._t = 0.0
        self._v = 0.0
        self._y = float(self._params.height)
        self._trail_pts = []

        if self.body is not None:
            self.body.resetTransform()
            self.body.translate(0.0, 0.0, self._y * SCENE_SCALE)
        if self.body_nodrag is not None:
            self.body_nodrag.resetTransform()
            self.body_nodrag.translate(3.5, 0.0, self._y * SCENE_SCALE)
        if self.trail is not None:
            self.trail.setData(pos=np.zeros((1, 3)))

        if self.hud_label is not None:
            self.hud_label.setText("")

    def _tick(self):
        if not self._running or self._params is None or self.view3d is None:
            return

        p = self._params
        steps = self._steps_per_frame()

        # Analytic integration for the 3D animation (forces a visible ramp-up)
        for _ in range(steps):
            self._t += p.dt
            self._v, self._y = self._analytic_state(p, self._t)
            if self._y <= 0.0:
                break

        # Update body transforms
        if self.body is not None:
            self.body.resetTransform()
            self.body.translate(0.0, 0.0, self._y * SCENE_SCALE)

        if self._gl_item_visible(self.body_nodrag):
            y_nd = max(0.0, p.height - 0.5 * p.g * self._t * self._t)  # no-drag comparator
            self.body_nodrag.resetTransform()
            self.body_nodrag.translate(3.5, 0.0, y_nd * SCENE_SCALE)

        # Trail
        if self.trail is not None and self.chk_trail.isChecked():
            self._trail_pts.append([0.0, 0.0, self._y * SCENE_SCALE])
            if len(self._trail_pts) > 4000:
                self._trail_pts = self._trail_pts[-4000:]
            arr = np.array(self._trail_pts, dtype=float) if self._trail_pts else np.zeros((1, 3))
            self.trail.setData(pos=arr)

        # HUD numbers — will start near 0 and grow toward vt
        if self.hud_label is not None:
            self.hud_label.setText(f"t={self._t:5.2f} s   v={self._v:6.2f} m/s   y={self._y:7.2f} m")
            self.hud_label.adjustSize()

        # Stop at ground
        if self._y <= 0.0:
            self.stop_sim()

        # Subtle camera drift
        az = (self.view3d.opts.get('azimuth', 0.0) + 0.08) % 360
        self.view3d.opts['azimuth'] = az
        self.view3d.update()

    def _export_current_view(self):
        try:
            if self.tabs.currentIndex() == 0:
                export_figure(self.fig, out_dir=IMAGES_DIR)
                add_log_entry("Terminal Velocity", action="Export2D")
                self.result_label.setText("2D plot exported.")
            else:
                if self.view3d is None:
                    self.result_label.setText("3D view is not available.")
                    return
                img = self.view3d.renderToArray((1400, 900))
                import imageio.v2 as iio
                from pathlib import Path
                p = Path(IMAGES_DIR) if IMAGES_DIR else Path(".")
                p.mkdir(parents=True, exist_ok=True)
                out = p / "terminal_velocity_3d.png"
                iio.imwrite(out.as_posix(), img)
                add_log_entry("Terminal Velocity", action="Export3D", data={"image": str(out)})
                self.result_label.setText(f"3D snapshot saved to {out}")
        except Exception as e:
            self.result_label.setText(f"Export failed: {e}")
            add_log_entry("Terminal Velocity", action="export_failed", data={"error": str(e)})
