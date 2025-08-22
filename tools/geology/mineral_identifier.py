
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.geo_utils import load_minerals
from core.data.functions.log import add_log_entry

# Flexible schema keys
NAME_KEYS = ("Name", "Mineral", "Mineral Name")
FORMULA_KEYS = ("Formula", "Chemical Formula", "Composition")
SYSTEM_KEYS = ("System", "Crystal System", "Crystal Structure")
HARDNESS_KEYS = ("Hardness", "Mohs Hardness", "HardnessMin", "HardnessMax")
SG_KEYS = ("SG", "Specific Gravity", "Density", "Calculated Density")

def _first_nonempty(row: Dict[str, Any], keys) -> Optional[str]:
    for k in keys:
        if k in row and str(row[k]).strip() not in ("", "NA", "N/A", "None"):
            return str(row[k]).strip()
    return None

def _num_from_keys(row: Dict[str, Any], keys) -> Optional[float]:
    s = _first_nonempty(row, keys)
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return None

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

class Tool(QDialog):
    TITLE = "Mineral Identifier"

    def __init__(self):
        super().__init__()
        self.setMinimumSize(920, 600)
        self.data = load_minerals()

        root = QVBoxLayout(self)

        # Inputs
        row = QHBoxLayout()
        self.hard = QLineEdit(); self.hard.setPlaceholderText("Hardness (Mohs)")
        self.sg = QLineEdit(); self.sg.setPlaceholderText("SG / Density")
        self.sys = QLineEdit(); self.sys.setPlaceholderText("Crystal system (e.g., hexagonal)")
        self.run = QPushButton("Find matches")
        row.addWidget(QLabel("Filters:")); row.addWidget(self.hard); row.addWidget(self.sg); row.addWidget(self.sys); row.addWidget(self.run)
        root.addLayout(row)

        # Table
        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(["Name","Formula","Hardness","SG","System"])
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl.setSortingEnabled(True)
        root.addWidget(self.tbl, 1)

        # Plot
        self.fig = Figure(figsize=(5,3), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        root.addWidget(NavigationToolbar(self.canvas, self))
        root.addWidget(self.canvas, 1)

        self.run.clicked.connect(self._run)

        # First draw: show all numeric points so it's never "empty"
        self._run(initial=True)

    def _parse_float(self, s: str) -> Optional[float]:
        s = s.strip().replace(",", ".")
        if not s:
            return None
        try:
            return float(s)
        except Exception:
            return None

    def _fill_table(self, items: List[Dict[str, Any]]):
        was_sorting = self.tbl.isSortingEnabled()
        self.tbl.setSortingEnabled(False)
        self.tbl.blockSignals(True)
        try:
            self.tbl.setRowCount(len(items))
            for i, r in enumerate(items):
                name = _first_nonempty(r, NAME_KEYS) or ""
                formula = _first_nonempty(r, FORMULA_KEYS) or ""
                system = _first_nonempty(r, SYSTEM_KEYS) or ""
                h = _num_from_keys(r, HARDNESS_KEYS)
                sg = _num_from_keys(r, SG_KEYS)

                self.tbl.setItem(i, 0, QTableWidgetItem(name))
                self.tbl.setItem(i, 1, QTableWidgetItem(formula))

                it_h = QTableWidgetItem()
                if h is not None:
                    it_h.setData(Qt.ItemDataRole.DisplayRole, float(h))
                    if h >= 7: it_h.setForeground(QBrush(QColor("#d9534f")))
                self.tbl.setItem(i, 2, it_h)

                it_s = QTableWidgetItem()
                if sg is not None:
                    it_s.setData(Qt.ItemDataRole.DisplayRole, float(sg))
                    if sg >= 4: it_s.setForeground(QBrush(QColor("#5bc0de")))
                self.tbl.setItem(i, 3, it_s)

                self.tbl.setItem(i, 4, QTableWidgetItem(system))
        finally:
            self.tbl.blockSignals(False)
            self.tbl.setSortingEnabled(was_sorting)
            if was_sorting:
                self.tbl.sortItems(0, Qt.SortOrder.AscendingOrder)

    def _plot_points(self, items: List[Dict[str, Any]], highlight_mask: Optional[List[bool]] = None):
        xs, ys = [], []
        hs, sgs = [], []
        for r in items:
            h = _num_from_keys(r, HARDNESS_KEYS)
            sg = _num_from_keys(r, SG_KEYS)
            if h is not None and sg is not None:
                xs.append(h); ys.append(sg)
                hs.append(h); sgs.append(sg)

        self.fig.clear(); ax = self.fig.add_subplot(111)
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
        self.fig.tight_layout(); self.canvas.draw()

    def _run(self, initial: bool = False):
        # Parse filters
        h = self._parse_float(self.hard.text())
        sg = self._parse_float(self.sg.text())
        sys = self.sys.text().strip()

        # If no filters -> show all rows with at least one numeric value so it's never blank
        if h is None and sg is None and not sys:
            items = [r for r in self.data if (_num_from_keys(r, HARDNESS_KEYS) is not None) or (_num_from_keys(r, SG_KEYS) is not None)]
            self._fill_table(items)
            self._plot_points(items)
            add_log_entry(self.TITLE, action="BrowseAll", data={"rows": len(items)})
            return

        # Scored filtering
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for r in self.data:
            s = _score_row(r, h, sg, sys)
            if s > 0:
                scored.append((s, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [r for _, r in scored[:200]]

        # Build highlight mask aligned with plotted points
        # We'll mark top-10% (at least 1) as highlighted in the scatter.
        n = max(1, len(top) // 10) if top else 0
        top_set = set(id(r) for r in top[:n]) if n else set()
        items = top if top else []

        self._fill_table(items)

        # For highlight mask, we need to align with items that have numeric points
        numeric_items = [r for r in items if (_num_from_keys(r, HARDNESS_KEYS) is not None and _num_from_keys(r, SG_KEYS) is not None)]
        hi_mask = [id(r) in top_set for r in numeric_items] if numeric_items else None

        self._plot_points(numeric_items, hi_mask)

        add_log_entry(self.TITLE, action="Identify", data={
            "filters": {"hard": h, "sg": sg, "sys": sys},
            "matched": len(items)
        })
