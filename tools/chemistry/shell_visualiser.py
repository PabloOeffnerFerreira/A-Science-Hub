import math, random, re, numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QSizePolicy, QTabWidget, QWidget, QHBoxLayout
)

# --- 2D stack ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Circle

# --- 3D stack (optional) ---
try:
    import pyqtgraph as pg
    import pyqtgraph.opengl as gl
    PG_OK = True
except Exception:
    PG_OK = False

from core.data.functions.chemistry_utils import load_element_data
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry
try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


# ----------------- helpers -----------------
def adjust_shells_for_charge(shells, charge):
    shells = shells.copy()
    if charge > 0:  # cation
        for _ in range(charge):
            if not shells:
                break
            shells[-1] -= 1
            if shells[-1] <= 0:
                shells.pop()
    elif charge < 0:  # anion
        for _ in range(-charge):
            if shells:
                shells[-1] += 1
            else:
                shells = [1]
    return shells


def format_ion_label(symbol, charge):
    if charge == 0:
        return symbol
    sign = "⁺" if charge > 0 else "⁻"
    magnitude = abs(charge)
    return f"{symbol}{magnitude if magnitude > 1 else ''}{sign}"


def neutron_count(atomic_mass, atomic_number):
    return max(0, round(atomic_mass) - atomic_number)


# --- robust getters for JSON variants ---
def get_shells(el):
    for k in ("shells", "Shells", "NumberofShells"):
        v = el.get(k)
        if v is not None:
            return [int(x) for x in v]
    raise KeyError("No shell data")


def get_protons(el):
    for k in ("atomicNumber", "AtomicNumber", "number", "Z"):
        v = el.get(k)
        if v is not None:
            return int(v)
    raise KeyError("No atomic number")


def get_atomic_mass(el):
    for k in ("atomicMass", "atomic_mass", "AtomicMass", "standard_atomic_weight", "AtomicWeight"):
        v = el.get(k)
        if v is None:
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            m = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', str(v))
            if m:
                return float(m.group(0))
    return float(get_protons(el))


# ----------------- main tool -----------------
class Tool(QDialog):
    TITLE = "Shell Visualiser"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        self.resize(900, 700)

        self.data = load_element_data()
        self._anim_on = False
        self._theta = 0.0

        main = QVBoxLayout(self)
        main.addWidget(QLabel("Element Symbol:"))
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("e.g., H, He, Fe")
        main.addWidget(self.entry)

        main.addWidget(QLabel("Charge:"))
        self.charge_entry = QLineEdit()
        self.charge_entry.setPlaceholderText("e.g., -2, +3")
        main.addWidget(self.charge_entry)

        controls = QHBoxLayout()
        self.draw_btn = QPushButton("Draw")
        self.save_btn = QPushButton("Export Image")
        self.anim_btn = QPushButton("Start Animation")
        controls.addWidget(self.draw_btn)
        controls.addWidget(self.save_btn)
        controls.addWidget(self.anim_btn)
        main.addLayout(controls)

        self.status_label = QLabel("")
        main.addWidget(self.status_label)

        # Tabs: 2D and 3D
        self.tabs = QTabWidget()
        main.addWidget(self.tabs)

        # --- 2D tab ---
        self.fig = Figure(figsize=(5, 5), dpi=110)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tab2d = QWidget(); v2d = QVBoxLayout(tab2d)
        v2d.addWidget(NavigationToolbar(self.canvas, self))
        v2d.addWidget(self.canvas)
        self.tabs.addTab(tab2d, "2D")

        # --- 3D tab (if available) ---
        if PG_OK:
            tab3d = QWidget(); v3d = QVBoxLayout(tab3d)
            self.view3d = gl.GLViewWidget()
            self.view3d.setCameraPosition(distance=18, elevation=12, azimuth=35)
            self.view3d.setBackgroundColor((18, 18, 18))
            v3d.addWidget(self.view3d)
            self.tabs.addTab(tab3d, "3D")
        else:
            self.view3d = None

        # Animation timer
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._tick)

        # Connections
        self.draw_btn.clicked.connect(self._draw)
        self.save_btn.clicked.connect(self._save_current_tab)
        self.anim_btn.clicked.connect(self._toggle_anim)

        self._nucleus = []
        self._rings = []
        self._electrons = []

    # ---------- rendering ----------
    def _draw(self):
        sym = self.entry.text().strip().capitalize()
        charge_text = self.charge_entry.text().strip()
        charge = int(charge_text) if charge_text else 0

        element = self.data.get(sym)
        if not element:
            QMessageBox.warning(self, "Not found", f"No data for '{sym}'")
            return

        try:
            shells = get_shells(element)
        except KeyError:
            QMessageBox.warning(self, "Missing data", f"No shell data for '{sym}'")
            return

        adj_shells = adjust_shells_for_charge(shells, charge)

        try:
            protons = get_protons(element)
        except KeyError:
            QMessageBox.warning(self, "Missing data", f"No atomic number for '{sym}'")
            return

        mass = get_atomic_mass(element)
        neutrons = neutron_count(mass, protons)

        self._render_2d(sym, adj_shells, charge)
        if self.view3d:
            self._render_3d(sym, adj_shells, protons, neutrons, charge)

        label = format_ion_label(sym, charge)
        self.status_label.setText(f"Rendered {label} with shells {adj_shells}")
        add_log_entry("Shell Visualiser", action="Draw", data={"symbol": sym, "charge": charge, "shells": adj_shells})

    def _render_2d(self, sym, shells, charge):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')

        base_radius = 1.5
        radii = np.array([base_radius + math.sqrt(i+1) * 1.1 for i in range(len(shells))], float)
        max_r = radii[-1] if len(radii) else base_radius

        colours = ["#9ec5fe", "#74c0fc", "#63e6be", "#ffe066", "#faa2c1", "#e599f7", "#ffc9c9"]

        for i, cnt in enumerate(shells):
            r = float(radii[i])
            ax.add_artist(Circle((0, 0), r, fill=False, edgecolor=colours[i % len(colours)], linewidth=2.4))
            for j in range(max(1, cnt)):
                ang = 2 * math.pi * j / max(1, cnt)
                ex = r * math.cos(ang)
                ey = r * math.sin(ang)
                ax.add_artist(Circle((ex, ey), 0.11, facecolor="#121212", edgecolor="#e9ecef", linewidth=0.8))

        label = format_ion_label(sym, charge)
        ax.text(0, 0, label, fontsize=16, fontweight="bold", ha='center', va='center', color="#e9ecef")
        pad = max_r * 0.25 + 0.8
        ax.set_xlim(-max_r - pad, max_r + pad)
        ax.set_ylim(-max_r - pad, max_r + pad)
        self.canvas.draw()

    def _render_3d(self, sym, shells, protons, neutrons, charge):
        self.view3d.clear()
        self._rings.clear(); self._electrons.clear(); self._nucleus.clear()

        # nucleus cluster
        g_p = gl.MeshData.sphere(rows=12, cols=12, radius=0.25)
        g_n = gl.MeshData.sphere(rows=12, cols=12, radius=0.25)
        for i in range(protons):
            x, y, z = (random.uniform(-0.7,0.7) for _ in range(3))
            p = gl.GLMeshItem(meshdata=g_p, smooth=True, color=(0.9, 0.3, 0.3, 1.0), shader='shaded')
            p.translate(x, y, z)
            self.view3d.addItem(p)
            self._nucleus.append(p)
        for i in range(neutrons):
            x, y, z = (random.uniform(-0.7,0.7) for _ in range(3))
            n = gl.GLMeshItem(meshdata=g_n, smooth=True, color=(0.7, 0.7, 0.7, 1.0), shader='shaded')
            n.translate(x, y, z)
            self.view3d.addItem(n)
            self._nucleus.append(n)

        # rings
        base_radius = 2.0
        radii = [base_radius + math.sqrt(i+1) * 1.3 for i in range(len(shells))]
        for r in radii:
            theta = np.linspace(0, 2*np.pi, 256)
            x = r * np.cos(theta); y = r * np.sin(theta); z = np.zeros_like(theta)
            ring = gl.GLLinePlotItem(pos=np.vstack([x, y, z]).T, width=1.5, antialias=True)
            self.view3d.addItem(ring)
            self._rings.append((ring, r))

        # electrons
        e_mesh = gl.MeshData.sphere(rows=12, cols=12, radius=0.25)
        for cnt, r in zip(shells, radii):
            cnt = max(1, cnt)
            for j in range(cnt):
                ang = 2*np.pi * j / cnt
                x, y, z = r*np.cos(ang), r*np.sin(ang), 0.0
                e = gl.GLMeshItem(meshdata=e_mesh, smooth=True, color=(0.85, 0.85, 0.9, 1.0), shader='shaded')
                e.translate(x, y, z)
                self.view3d.addItem(e)
                self._electrons.append((e, r, ang))

        label = format_ion_label(sym, charge)
        label_item = gl.GLTextItem(pos=(0, 0, radii[-1] + 1.5 if radii else 3.0), text=label,
                                   color=(1,1,1,1), font=pg.QtGui.QFont("Arial", 16))
        self.view3d.addItem(label_item)

    def _tick(self):
        if not self._electrons:
            return
        self._theta += 0.02
        for e, r, phase in self._electrons:
            x = r * math.cos(phase + self._theta)
            y = r * math.sin(phase + self._theta)
            e.resetTransform()
            e.translate(x, y, 0.0)
        if self.view3d is not None:
            az = (self.view3d.opts['azimuth'] + 0.2) % 360
            self.view3d.opts['azimuth'] = az
            self.view3d.update()

    def _toggle_anim(self):
        self._anim_on = not self._anim_on
        if self._anim_on:
            self.anim_btn.setText("Stop Animation")
            self.timer.start()
        else:
            self.anim_btn.setText("Start Animation")
            self.timer.stop()

    def _save_current_tab(self):
        sym = self.entry.text().strip().capitalize() or "element"
        try:
            if self.tabs.currentIndex() == 0:
                path = export_figure(self.fig, out_dir=IMAGES_DIR) if IMAGES_DIR else export_figure(self.fig)
            else:
                if self.view3d is None:
                    QMessageBox.information(self, "Unavailable", "3D view is not available on this system.")
                    return
                img = self.view3d.renderToArray((1200, 900))
                import imageio.v2 as iio
                from pathlib import Path
                p = Path(IMAGES_DIR) if IMAGES_DIR else Path(".")
                p.mkdir(parents=True, exist_ok=True)
                path = p / f"shell_{sym}.png"
                iio.imwrite(path.as_posix(), img)
            self.status_label.setText(f"Saved: {path}")
            add_log_entry("Shell Visualiser", action="Export", data={"symbol": sym, "image": str(path)})
        except Exception as e:
            self.status_label.setText(f"Save failed: {e}")
