from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QWidget, QSizePolicy, QToolTip
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from core.data.chemistry_utils import _PROP_KEYS, _COLOUR_BY_CATEGORY
from core.data.functions.log import add_log_entry


# ---- Data loading (shared first, local fallback) ----
def _load_elements_fallback() -> Dict[str, dict]:
    try:
        from core.data.functions.chemistry_utils import load_element_data  # type: ignore
        data = load_element_data()
        if data:
            return data
    except Exception:
        pass
    local = Path(__file__).with_name("ptable.json")
    if not local.exists():
        for c in [
            Path.cwd() / "data" / "databases" / "PeriodicTableJSON.json",
            Path.cwd() / "databases" / "PeriodicTableJSON.json",
            Path.cwd() / "ptable.json",
        ]:
            if c.exists():
                local = c
                break
    if not local.exists():
        raise FileNotFoundError(
            "No periodic table JSON available (core.data.paths.PTABLE_JSON_PATH not set and no local ptable.json)."
        )
    obj = json.loads(local.read_text(encoding="utf-8"))
    return {el.get("symbol"): el for el in obj.get("elements", []) if el.get("symbol")}

def _coerce_float(x) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    try:
        return float(re.sub(r"[^0-9.eE+-]", "", str(x)))
    except Exception:
        return None


def _get_numeric(el: dict, keys: List[str]) -> Optional[float]:
    for k in keys:
        if k in el and el[k] is not None:
            v = _coerce_float(el[k])
            if v is not None:
                return v
    return None


def _category(el: dict) -> str:
    return (el.get("category") or el.get("Type") or "unknown").strip().lower()


def _colour_for(el: dict) -> str:
    return _COLOUR_BY_CATEGORY.get(_category(el), "#1f77b4")


def _name_sym(el: dict) -> Tuple[str, str]:
    return (el.get("name") or el.get("Element") or "Unknown", el.get("symbol") or "?")


# ---- Matplotlib canvas with Qt-native tooltips and highlight ----
class _ScatterCanvas(FigureCanvas):
    """Matplotlib canvas that uses Qt mouse events for precise hover tooltips, plus a red highlight ring."""
    def __init__(self, parent: QWidget = None):
        self.figure = Figure(figsize=(5, 4), dpi=100, tight_layout=True)
        super().__init__(self.figure)
        self.setParent(parent)

        self.ax = self.figure.add_subplot(111)

        self._offsets = np.empty((0, 2))        # Nx2 data coords
        self._labels: List[dict] = []           # same length as offsets
        self._last_i: Optional[int] = None

        # Marker / selection parameters
        self._marker_size = 42                  # scatter "s" in points^2
        self._min_threshold_px = 5.0            # minimum hit radius
        self._highlight = None                  # scatter used to ring active point

        # Allow continuous mouse move events
        self.setMouseTracking(True)

    def set_titles(self, xlab: str, ylab: str, title: str):
        self.ax.set_xlabel(xlab)
        self.ax.set_ylabel(ylab)
        self.ax.set_title(title, pad=8, fontsize=11)

    def plot(self, xs, ys, colours, labels):
        self.ax.clear()

        # Main scatter
        self.ax.scatter(
            xs, ys, s=self._marker_size, c=colours, alpha=0.95,
            edgecolors="k", linewidths=0.4, zorder=2
        )

        # Highlight ring (initially empty)
        self._highlight = self.ax.scatter(
            [], [], s=self._marker_size * 1.6, facecolors="none",
            edgecolors="red", linewidths=1.2, zorder=4
        )

        self.ax.grid(True, linewidth=0.4, alpha=0.4, zorder=1)

        self._labels = labels
        self._offsets = np.column_stack([xs, ys]) if len(xs) else np.empty((0, 2))

        self.figure.canvas.draw_idle()

    # ---- Qt events ----
    def leaveEvent(self, _):
        self._hide_tooltip()

    def mouseMoveEvent(self, event):
        if self._offsets.size == 0:
            self._hide_tooltip(); return

        # Qt (logical px) → physical px + flip Y to match Matplotlib display coords
        pos = event.position() if hasattr(event, "position") else event.pos()
        dpr = float(self.devicePixelRatioF())
        mx_phys = float(pos.x()) * dpr
        my_phys = float(pos.y()) * dpr
        canvas_h_phys = float(self.height()) * dpr
        my_phys = canvas_h_phys - my_phys  # invert Y

        # Marker radius in physical pixels (s is points^2)
        diameter_pts = float(np.sqrt(self._marker_size))
        px_per_pt = self.figure.dpi / 72.0
        radius_px = 0.5 * diameter_pts * px_per_pt  # EXACT radius, no extra threshold

        # Data → physical pixel coords
        trans = self.ax.transData.transform
        pts_px = trans(self._offsets)  # shape (N, 2), in physical px with origin at bottom-left
        if pts_px.size == 0:
            self._hide_tooltip(); return

        dx = pts_px[:, 0] - mx_phys
        dy = pts_px[:, 1] - my_phys
        d2 = dx*dx + dy*dy
        i = int(np.argmin(d2))

        # Only show when the cursor is INSIDE the marker disk (no added tolerance)
        if d2[i] <= (radius_px * radius_px):
            if self._last_i != i:
                self._last_i = i
                meta = self._labels[i] if i < len(self._labels) else {}
                text = meta.get("tooltip", "")
                x, y = self._offsets[i]

                if self._highlight is not None:
                    self._highlight.set_offsets([[x, y]])

                # Show tooltip exactly at cursor (Qt uses logical coords here)
                gp = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
                QToolTip.showText(gp, text, self)

                self.figure.canvas.draw_idle()
        else:
            self._hide_tooltip()


    def _hide_tooltip(self):
        if self._last_i is not None:
            self._last_i = None
            QToolTip.hideText()
            if self._highlight is not None:
                import numpy as np
                self._highlight.set_offsets(np.empty((0, 2), dtype=float))
                self.figure.canvas.draw_idle()



# ---- Tool wrapper ----
class Tool(QDialog):
    TITLE = "Element Property Grapher"

    def __init__(self):
        super().__init__()
        self.setMinimumSize(760, 560)
        self.setWindowTitle(self.TITLE)

        self.elements = _load_elements_fallback()

        root = QVBoxLayout(self)

        # Controls (dropdowns, no typing)
        ctrls = QHBoxLayout()
        ctrls.addWidget(QLabel("X property:"))
        self.xprop = QComboBox(); ctrls.addWidget(self.xprop)
        ctrls.addSpacing(16)
        ctrls.addWidget(QLabel("Y property:"))
        self.yprop = QComboBox(); ctrls.addWidget(self.yprop)
        ctrls.addSpacing(16)
        ctrls.addWidget(QLabel("Category filter:"))
        self.cat = QComboBox(); ctrls.addWidget(self.cat)
        ctrls.addStretch(1)
        root.addLayout(ctrls)

        # Canvas
        self.canvas = _ScatterCanvas(self)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self.canvas, 1)

        # Populate dropdowns
        for nice in _PROP_KEYS.keys():
            self.xprop.addItem(nice)
            self.yprop.addItem(nice)
        self.xprop.setCurrentText("Atomic mass (u)")
        self.yprop.setCurrentText("Boiling point (K)")

        cats = sorted({(e.get("category") or e.get("Type") or "unknown").lower() for e in self.elements.values()})
        self.cat.addItem("All")
        for c in cats:
            self.cat.addItem(c.title())

        # Auto-update + log on change
        self.xprop.currentIndexChanged.connect(lambda _: self._replot(log_reason="x-change"))
        self.yprop.currentIndexChanged.connect(lambda _: self._replot(log_reason="y-change"))
        self.cat.currentIndexChanged.connect(lambda _: self._replot(log_reason="category-change"))

        self._replot(initial=True)

    def _replot(self, initial: bool = False, log_reason: Optional[str] = None):
        xnice = self.xprop.currentText()
        ynice = self.yprop.currentText()
        catf = self.cat.currentText()
        kx = _PROP_KEYS[xnice]
        ky = _PROP_KEYS[ynice]
        catf_l = catf.lower()

        xs: List[float] = []
        ys: List[float] = []
        colours: List[str] = []
        labels: List[dict] = []

        for sym, el in self.elements.items():
            if catf != "All":
                if (el.get("category") or el.get("Type") or "unknown").lower() != catf_l:
                    continue
            xv = _get_numeric(el, kx)
            yv = _get_numeric(el, ky)
            if xv is None or yv is None:
                continue
            xs.append(xv)
            ys.append(yv)
            colours.append(_colour_for(el))
            name, sym = _name_sym(el)
            labels.append({"name": name, "symbol": sym, "tooltip": f"{name} ({sym})\n{xnice}: {xv}\n{ynice}: {yv}"})

        title = f"{ynice} vs {xnice}" + ("" if catf == "All" else f" — {catf}")
        self.canvas.set_titles(xnice, ynice, title)
        self.canvas.plot(xs, ys, colours, labels)

        if log_reason is not None:
            add_log_entry(
                "Element Property Grapher",
                action="Change",
                data={"reason": log_reason, "x": xnice, "y": ynice, "filter": catf, "n": len(xs)},
            )
