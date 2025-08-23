from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

import numpy as np

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QCheckBox, QComboBox, QTabWidget,
    QWidget, QSizePolicy
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import FancyArrow, Rectangle

from core.data.functions.log import add_log_entry
from core.data.functions.image_export import export_figure
from core.data.functions.geo_utils import (
    load_minerals, load_favs, save_favs,
    half_life_decay, estimate_age_from_remaining
)

try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


# ------------------- Mineral schema helpers -------------------

NAME_KEYS = ("Name", "Mineral", "Mineral Name")
FORMULA_KEYS = ("Formula", "Chemical Formula", "Composition")
SYSTEM_KEYS = ("System", "Crystal System", "Crystal Structure")
HARDNESS_KEYS = ("Hardness", "Mohs Hardness", "HardnessMin", "HardnessMax")
SG_KEYS = ("SG", "Specific Gravity", "Density", "Calculated Density")
TYPE_KEYS = ("Type", "Category", "Group")

def _first_nonempty(row: Dict[str, Any], keys) -> Optional[str]:
    for k in keys:
        if k in row and str(row[k]).strip() not in ("", "NA", "N/A", "None"):
            return str(row[k]).strip()
    return None

def _num_from_keys(row: Dict[str, Any], keys) -> Optional[float]:
    s = _first_nonempty(row, keys)
    if s is None: return None
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return None

def _type_value(row: Dict[str, Any]) -> str:
    return _first_nonempty(row, TYPE_KEYS) or ""

def _score_row(row: Dict[str, Any], h: Optional[float], sg: Optional[float], sys: str) -> float:
    score = 0.0
    if h is not None:
        rh = _num_from_keys(row, HARDNESS_KEYS)
        if rh is not None:
            score += 1.0 / (1.0 + abs(rh - h))
    if sg is not None:
        rsg = _num_from_keys(row, SG_KEYS)
        if rsg is not None:
            score += 1.0 / (1.0 + abs(rsg - sg))
    if sys:
        r_sys = (_first_nonempty(row, SYSTEM_KEYS) or "").lower()
        if r_sys.startswith(sys.lower()[:4]):
            score += 0.5
    return score


# ------------------- Main Tool -------------------

class Tool(QDialog):
    TITLE = "Geo Lab"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.TITLE)
        self.setMinimumSize(1080, 720)

        self._build_ui()
        self._wire()

    # ----- UI -----
    def _build_ui(self):
        root = QVBoxLayout(self)

        # Header actions (Prefill & Export All)
        header = QHBoxLayout()
        self.prefill = QPushButton("Prefill (debug)")
        header.addWidget(self.prefill)
        header.addStretch(1)
        root.addLayout(header)

        # Top-level tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        # Minerals tab (explore & identify subtabs)
        self.tab_minerals = QWidget()
        self.tabs.addTab(self.tab_minerals, "Minerals")
        self._build_minerals_tab()

        # Radioactivity tab
        self.tab_radio = QWidget()
        self.tabs.addTab(self.tab_radio, "Radioactivity")
        self._build_radio_tab()

        # Tectonics tab
        self.tab_tect = QWidget()
        self.tabs.addTab(self.tab_tect, "Tectonics")
        self._build_tectonics_tab()

    # ----- Minerals -----
    def _build_minerals_tab(self):
        w = self.tab_minerals
        lay = QVBoxLayout(w)

        self.mineral_tabs = QTabWidget()
        lay.addWidget(self.mineral_tabs, 1)

        # Explorer subtab
        self.tab_explore = QWidget()
        self.mineral_tabs.addTab(self.tab_explore, "Explorer")
        self._build_explorer_subtab()

        # Identifier subtab
        self.tab_ident = QWidget()
        self.mineral_tabs.addTab(self.tab_ident, "Identifier")
        self._build_identifier_subtab()

    def _build_explorer_subtab(self):
        w = self.tab_explore
        root = QVBoxLayout(w)

        # Data
        self.data: List[Dict[str, Any]] = load_minerals()
        self.favs = load_favs()

        # Filter bar
        bar = QHBoxLayout()
        self.q = QLineEdit(); self.q.setPlaceholderText("Search name, formula, system, notes…")
        self.only_favs = QCheckBox("Favourites only")
        self.type_box = QComboBox(); self.type_box.addItem("All Types")
        types = sorted({ _type_value(r) for r in self.data if _type_value(r) })
        for t in types:
            self.type_box.addItem(t)
        self.refresh_btn = QPushButton("Refresh")
        bar.addWidget(QLabel("Filter:")); bar.addWidget(self.q, 1); bar.addWidget(self.type_box); bar.addWidget(self.only_favs); bar.addWidget(self.refresh_btn)
        root.addLayout(bar)

        # Table
        self.tbl = QTableWidget(0, 6)
        self.tbl.setHorizontalHeaderLabels(["★","Name","Formula","Hardness","SG","System"])
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl.setSortingEnabled(True)
        root.addWidget(self.tbl, 1)

        foot = QHBoxLayout()
        self.toggle_fav = QPushButton("Toggle Favourite")
        self.copy_row = QPushButton("Copy Row")
        self.status = QLabel("")
        foot.addWidget(self.toggle_fav); foot.addWidget(self.copy_row); foot.addStretch(1); foot.addWidget(self.status)
        root.addLayout(foot)

        # Debounce search
        self._debounce = QTimer(self); self._debounce.setSingleShot(True); self._debounce.setInterval(200)
        self._debounce.timeout.connect(self._rebuild_explorer)

        # First build
        self._rebuild_explorer(initial=True)

    def _match_explorer(self, row: dict, q: str) -> bool:
        pieces = [
            _first_nonempty(row, NAME_KEYS) or "",
            _first_nonempty(row, FORMULA_KEYS) or "",
            _first_nonempty(row, SYSTEM_KEYS) or "",
            str(row.get("Notes","")),
            _type_value(row),
        ]
        return q in " ".join(pieces).lower()

    def _rebuild_explorer(self, initial: bool = False):
        q = self.q.text().strip().lower()
        typ = self.type_box.currentText()
        only_favs = self.only_favs.isChecked()

        # Filter
        items: List[Dict[str, Any]] = []
        for r in self.data or []:
            name = _first_nonempty(r, NAME_KEYS) or ""
            if not name:
                continue
            if only_favs and name not in self.favs:
                continue
            if typ != "All Types" and _type_value(r) != typ:
                continue
            if q and not self._match_explorer(r, q):
                continue
            items.append(r)

        was_sorting = self.tbl.isSortingEnabled()
        self.tbl.setSortingEnabled(False)
        self.tbl.blockSignals(True)
        try:
            self.tbl.setRowCount(len(items))
            for i, r in enumerate(items):
                name = _first_nonempty(r, NAME_KEYS) or ""
                formula = _first_nonempty(r, FORMULA_KEYS) or ""
                system = _first_nonempty(r, SYSTEM_KEYS) or ""

                fav = "★" if name in self.favs else "☆"
                self.tbl.setItem(i, 0, QTableWidgetItem(fav))
                self.tbl.setItem(i, 1, QTableWidgetItem(name))
                self.tbl.setItem(i, 2, QTableWidgetItem(formula))

                h = _num_from_keys(r, HARDNESS_KEYS)
                sg = _num_from_keys(r, SG_KEYS)

                it_h = QTableWidgetItem()
                it_s = QTableWidgetItem()
                if h is not None:
                    it_h.setData(Qt.ItemDataRole.DisplayRole, float(h))
                    if h >= 7: it_h.setForeground(QBrush(QColor("#d9534f")))
                else:
                    it_h.setText("")
                if sg is not None:
                    it_s.setData(Qt.ItemDataRole.DisplayRole, float(sg))
                    if sg >= 4: it_s.setForeground(QBrush(QColor("#5bc0de")))
                else:
                    it_s.setText("")

                self.tbl.setItem(i, 3, it_h)
                self.tbl.setItem(i, 4, it_s)
                self.tbl.setItem(i, 5, QTableWidgetItem(system))
        finally:
            self.tbl.blockSignals(False)
            self.tbl.setSortingEnabled(was_sorting)
            if was_sorting:
                self.tbl.sortItems(1, Qt.SortOrder.AscendingOrder)

        self.status.setText(f"{len(items)} / {len(self.data)} rows")

    def _toggle_fav(self):
        row = self.tbl.currentRow()
        if row < 0:
            return
        name_item = self.tbl.item(row, 1)
        if not name_item:
            return
        name = name_item.text()
        if name in self.favs:
            self.favs.remove(name)
        else:
            self.favs.add(name)
        save_favs(self.favs)
        star_item = self.tbl.item(row, 0)
        if star_item:
            star_item.setText("★" if name in self.favs else "☆")

    def _copy_row(self):
        row = self.tbl.currentRow()
        if row < 0:
            return
        vals = [self.tbl.item(row, j).text() if self.tbl.item(row, j) else "" for j in range(self.tbl.columnCount())]
        text = "\t".join(vals)
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    def _build_identifier_subtab(self):
        w = self.tab_ident
        root = QVBoxLayout(w)

        # Inputs
        row = QHBoxLayout()
        self.in_hard = QLineEdit(); self.in_hard.setPlaceholderText("Hardness (Mohs)")
        self.in_sg = QLineEdit(); self.in_sg.setPlaceholderText("SG / Density")
        self.in_sys = QLineEdit(); self.in_sys.setPlaceholderText("Crystal system (e.g., hexagonal)")
        self.btn_ident = QPushButton("Find matches")
        row.addWidget(QLabel("Filters:")); row.addWidget(self.in_hard); row.addWidget(self.in_sg); row.addWidget(self.in_sys); row.addWidget(self.btn_ident)
        root.addLayout(row)

        # Table
        self.tbl_ident = QTableWidget(0, 5)
        self.tbl_ident.setHorizontalHeaderLabels(["Name","Formula","Hardness","SG","System"])
        self.tbl_ident.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_ident.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_ident.setSortingEnabled(True)
        root.addWidget(self.tbl_ident, 1)

        # Plot
        self.fig_ident = Figure(figsize=(5,3), dpi=100)
        self.canvas_ident = FigureCanvas(self.fig_ident)
        root.addWidget(NavigationToolbar(self.canvas_ident, self))
        root.addWidget(self.canvas_ident, 1)

        # First run shows numeric points
        self._run_identifier(initial=True)

    def _parse_float(self, s: str) -> Optional[float]:
        s = s.strip().replace(",", ".")
        if not s:
            return None
        try:
            return float(s)
        except Exception:
            return None

    def _fill_identifier_table(self, items: List[Dict[str, Any]]):
        was_sorting = self.tbl_ident.isSortingEnabled()
        self.tbl_ident.setSortingEnabled(False)
        self.tbl_ident.blockSignals(True)
        try:
            self.tbl_ident.setRowCount(len(items))
            for i, r in enumerate(items):
                name = _first_nonempty(r, NAME_KEYS) or ""
                formula = _first_nonempty(r, FORMULA_KEYS) or ""
                system = _first_nonempty(r, SYSTEM_KEYS) or ""
                h = _num_from_keys(r, HARDNESS_KEYS)
                sg = _num_from_keys(r, SG_KEYS)

                self.tbl_ident.setItem(i, 0, QTableWidgetItem(name))
                self.tbl_ident.setItem(i, 1, QTableWidgetItem(formula))

                it_h = QTableWidgetItem()
                if h is not None:
                    it_h.setData(Qt.ItemDataRole.DisplayRole, float(h))
                    if h >= 7: it_h.setForeground(QBrush(QColor("#d9534f")))
                self.tbl_ident.setItem(i, 2, it_h)

                it_s = QTableWidgetItem()
                if sg is not None:
                    it_s.setData(Qt.ItemDataRole.DisplayRole, float(sg))
                    if sg >= 4: it_s.setForeground(QBrush(QColor("#5bc0de")))
                self.tbl_ident.setItem(i, 3, it_s)

                self.tbl_ident.setItem(i, 4, QTableWidgetItem(system))
        finally:
            self.tbl_ident.blockSignals(False)
            self.tbl_ident.setSortingEnabled(was_sorting)
            if was_sorting:
                self.tbl_ident.sortItems(0, Qt.SortOrder.AscendingOrder)

    def _plot_identifier_points(self, items: List[Dict[str, Any]], highlight_mask: Optional[List[bool]] = None):
        xs, ys = [], []
        for r in items:
            h = _num_from_keys(r, HARDNESS_KEYS)
            sg = _num_from_keys(r, SG_KEYS)
            if h is not None and sg is not None:
                xs.append(h); ys.append(sg)

        self.fig_ident.clear(); ax = self.fig_ident.add_subplot(111)
        if xs:
            if highlight_mask and any(highlight_mask):
                base_x = [x for x, m in zip(xs, highlight_mask) if not m]
                base_y = [y for y, m in zip(ys, highlight_mask) if not m]
                hi_x = [x for x, m in zip(xs, highlight_mask) if m]
                hi_y = [y for y, m in zip(ys, highlight_mask) if m]
                if base_x:
                    ax.scatter(base_x, base_y, s=28, alpha=0.6)
                if hi_x:
                    ax.scatter(hi_x, hi_y, s=64, edgecolors="k", linewidths=0.8)
            else:
                ax.scatter(xs, ys, s=28, alpha=0.8)
            ax.set_xlabel("Hardness (Mohs)"); ax.set_ylabel("Specific Gravity / Density")
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, "No numeric hardness/SG points to plot", transform=ax.transAxes, ha="center", va="center")
        self.fig_ident.tight_layout(); self.canvas_ident.draw()

    def _run_identifier(self, initial: bool = False):
        h = self._parse_float(self.in_hard.text())
        sg = self._parse_float(self.in_sg.text())
        sys = self.in_sys.text().strip()

        if h is None and sg is None and not sys:
            items = [r for r in self.data if (_num_from_keys(r, HARDNESS_KEYS) is not None) or (_num_from_keys(r, SG_KEYS) is not None)]
            self._fill_identifier_table(items)
            self._plot_identifier_points(items)
            add_log_entry("Mineral Identifier", action="BrowseAll", data={"rows": len(items)})
            return

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for r in self.data:
            s = _score_row(r, h, sg, sys)
            if s > 0:
                scored.append((s, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [r for _, r in scored[:200]]

        self._fill_identifier_table(top)

        # highlight top-10% in scatter
        n = max(1, len(top) // 10) if top else 0
        top_set = set(id(r) for r in top[:n]) if n else set()
        numeric_items = [r for r in top if (_num_from_keys(r, HARDNESS_KEYS) is not None and _num_from_keys(r, SG_KEYS) is not None)]
        hi_mask = [id(r) in top_set for r in numeric_items] if numeric_items else None

        self._plot_identifier_points(numeric_items, hi_mask)
        add_log_entry("Mineral Identifier", action="Identify", data={
            "filters": {"hard": h, "sg": sg, "sys": sys},
            "matched": len(top)
        })

    # ----- Radioactivity -----
    def _build_radio_tab(self):
        w = self.tab_radio
        lay = QVBoxLayout(w)

        # Inputs grid
        g = QGridLayout()
        # Half-life / decay plot
        g.addWidget(QLabel("Initial quantity N₀:"), 0, 0)
        self.rad_N0 = QLineEdit(); self.rad_N0.setPlaceholderText("e.g., 100"); g.addWidget(self.rad_N0, 0, 1)

        g.addWidget(QLabel("Half-life t½:"), 1, 0)
        self.rad_hl = QLineEdit(); self.rad_hl.setPlaceholderText("e.g., 5730"); g.addWidget(self.rad_hl, 1, 1)

        g.addWidget(QLabel("Time span T (for plot):"), 2, 0)
        self.rad_T = QLineEdit(); self.rad_T.setPlaceholderText("e.g., 50000"); g.addWidget(self.rad_T, 2, 1)

        # Dating (remaining %)
        g.addWidget(QLabel("Remaining (%) [0–100]:"), 3, 0)
        self.rad_rem = QLineEdit(); self.rad_rem.setPlaceholderText("e.g., 25"); g.addWidget(self.rad_rem, 3, 1)

        lay.addLayout(g)

        # Buttons
        r = QHBoxLayout()
        self.btn_rad_compute = QPushButton("Compute & Plot")
        self.btn_rad_export = QPushButton("Export Plot")
        r.addWidget(self.btn_rad_compute); r.addWidget(self.btn_rad_export)
        lay.addLayout(r)

        # Result text
        self.rad_result = QLabel("")
        self.rad_result.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.rad_result)

        # Figure
        self.rad_fig = Figure(figsize=(7.2, 3.8), dpi=110)
        self.rad_canvas = FigureCanvas(self.rad_fig)
        lay.addWidget(NavigationToolbar(self.rad_canvas, self))
        lay.addWidget(self.rad_canvas, 1)

        # Presets row
        presets = [("Carbon-14", 5730.0), ("Potassium-40", 1.248e9),
                   ("Uranium-235", 7.038e8), ("Uranium-238", 4.468e9),
                   ("Rubidium-87", 4.88e10)]
        p_row = QHBoxLayout(); p_row.addWidget(QLabel("Presets:"))
        for name, hl in presets:
            b = QPushButton(name); b.clicked.connect(lambda _, v=hl: self.rad_hl.setText(str(v))); p_row.addWidget(b)
        lay.addLayout(p_row)

    def _compute_radio(self):
        # Decay curve
        try:
            N0 = float(self.rad_N0.text())
            hl = float(self.rad_hl.text())
            T = float(self.rad_T.text())
        except Exception:
            self.rad_result.setText("Enter valid N₀, t½, and T to plot.")
            self.rad_fig.clear(); self.rad_canvas.draw()
            return

        if hl <= 0 or T <= 0:
            self.rad_result.setText("Half-life and time span must be > 0.")
            self.rad_fig.clear(); self.rad_canvas.draw()
            return

        t = np.linspace(0, T, 400)
        y = [half_life_decay(N0, ti, hl) for ti in t]
        self.rad_fig.clear(); ax = self.rad_fig.add_subplot(111)
        ax.plot(t, y)
        ax.set_xlabel("Time"); ax.set_ylabel("Quantity")
        ax.grid(True, alpha=0.3)
        self.rad_fig.tight_layout(); self.rad_canvas.draw()

        # Dating from remaining%
        try:
            rem = float(self.rad_rem.text())
            age = estimate_age_from_remaining(rem/100.0, hl)
            age_txt = f"Estimated age (from {rem:.3g}% remaining): {age:,.6g} years"
        except Exception:
            age_txt = "Enter a valid remaining % to estimate age."

        self.rad_result.setText(f"N(T) = {y[-1]:.6g} | t½ = {hl:g}\n{age_txt}")

        add_log_entry("Radioactivity", action="Compute",
                      data={"N0": N0, "hl": hl, "T": T, "N_T": y[-1]})

    # ----- Tectonics -----
    def _build_tectonics_tab(self):
        w = self.tab_tect
        lay = QVBoxLayout(w)

        # Plate velocity
        r = QHBoxLayout()
        r.addWidget(QLabel("Distance (km):"))
        self.tect_dist = QLineEdit(); self.tect_dist.setPlaceholderText("e.g., 100"); r.addWidget(self.tect_dist)
        r.addWidget(QLabel("Time (Myr):"))
        self.tect_time = QLineEdit(); self.tect_time.setPlaceholderText("e.g., 2"); r.addWidget(self.tect_time)
        self.btn_tect_compute = QPushButton("Compute velocity")
        r.addWidget(self.btn_tect_compute)
        self.tect_result = QLabel("")
        r.addWidget(self.tect_result, 1)
        lay.addLayout(r)

        # Boundary diagram
        row = QHBoxLayout()
        row.addWidget(QLabel("Boundary Type:"))
        self.kind = QComboBox(); self.kind.addItems(["Convergent", "Divergent", "Transform"])
        row.addWidget(self.kind)
        self.btn_tect_draw = QPushButton("Draw diagram"); row.addWidget(self.btn_tect_draw)
        self.btn_tect_export = QPushButton("Export Diagram…"); row.addWidget(self.btn_tect_export)
        lay.addLayout(row)

        self.tect_fig = Figure(figsize=(7.2, 3.8), dpi=110)
        self.tect_canvas = FigureCanvas(self.tect_fig); self.tect_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.tect_canvas, self))
        lay.addWidget(self.tect_canvas, 1)

    def _compute_plate_velocity(self):
        try:
            d_km = float(self.tect_dist.text())
            t_ma = float(self.tect_time.text())
            v_mm_yr = (d_km / t_ma) if t_ma != 0 else float("inf")  # 1 km / 1 Myr = 1 mm/yr
            if math.isfinite(v_mm_yr):
                self.tect_result.setText(f"Velocity: {v_mm_yr:.6g} mm/yr")
            else:
                self.tect_result.setText("Velocity: ∞ (t=0)")
            add_log_entry("Plate Velocity", action="Compute", data={"d_km": d_km, "t_ma": t_ma, "v_mm_yr": v_mm_yr})
        except Exception as e:
            self.tect_result.setText("Invalid input.")

    def _draw_boundary(self):
        kind = self.kind.currentText()
        self.tect_fig.clear(); ax = self.tect_fig.add_subplot(111)
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

        self.tect_fig.tight_layout(); self.tect_canvas.draw()
        add_log_entry("Plate Boundary Diagram", action="Draw", data={"kind": kind})

    # ----- wiring & prefill -----
    def _wire(self):
        # Minerals
        self.refresh_btn.clicked.connect(self._rebuild_explorer)
        self.q.textChanged.connect(lambda _=None: self._debounce.start())
        self.only_favs.stateChanged.connect(self._rebuild_explorer)
        self.type_box.currentIndexChanged.connect(self._rebuild_explorer)
        self.toggle_fav.clicked.connect(self._toggle_fav)
        self.copy_row.clicked.connect(self._copy_row)
        self.btn_ident.clicked.connect(self._run_identifier)

        # Radioactivity
        self.btn_rad_compute.clicked.connect(self._compute_radio)
        self.btn_rad_export.clicked.connect(lambda: export_figure(self.rad_fig, out_dir=IMAGES_DIR))

        # Tectonics
        self.btn_tect_compute.clicked.connect(self._compute_plate_velocity)
        self.btn_tect_draw.clicked.connect(self._draw_boundary)
        self.btn_tect_export.clicked.connect(lambda: export_figure(self.tect_fig, out_dir=IMAGES_DIR))

        # Prefill
        self.prefill.clicked.connect(self._do_prefill)

    def _do_prefill(self):
        # Minerals: leave as-is (dataset-driven)
        # Radioactivity
        self.rad_N0.setText("100")
        self.rad_hl.setText("5730")
        self.rad_T.setText("50000")
        self.rad_rem.setText("25")
        self._compute_radio()

        # Tectonics
        self.tect_dist.setText("100")
        self.tect_time.setText("2")
        self._compute_plate_velocity()
        self._draw_boundary()
