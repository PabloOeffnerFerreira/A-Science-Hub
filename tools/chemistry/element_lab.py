# Unified "Element Lab" that bundles: Viewer, Shells, Isotopes, Properties (scatter), Comparator, Phase predictor
# Pablo — this composes your existing tools without copying their internals 1:1. 
# It embeds each tool in a right-side stack, with a left sidebar for navigation + element selection.
# Drop this file next to your other tools and import/run ElementLab as a dialog or a top-level window.

from __future__ import annotations

from typing import Optional, Dict, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QSplitter, QStackedWidget, QFrame, QToolBar, QMessageBox
)

# --- Import your existing tools ---
# (They are QDialog subclasses; we embed them as child widgets.)
from labs.elements.element_viewer import Tool as ViewerTool
from labs.elements.shell_visualiser import Tool as ShellTool
from labs.elements.isotope_notation import Tool as IsotopeTool
from labs.elements.element_property_grapher import Tool as GrapherTool
from labs.elements.element_comparator import Tool as ComparatorTool
from labs.elements.phase_predictor import Tool as PhaseTool

# Data + helpers
from core.data.functions.chemistry_utils import load_element_data


class _Embedded(QWidget):
    """Wrap a QDialog subclass instance so it behaves as an embeddable widget."""
    def __init__(self, dialog_cls: Callable[[], QDialog], parent: QWidget | None = None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.inner = dialog_cls()
        # Make sure the inner dialog acts like a widget inside our layout
        self.inner.setParent(self)
        self.inner.setWindowFlag(Qt.WindowType.Widget, True)
        lay.addWidget(self.inner)

    def find_child(self, name: str):
        return self.inner.findChild(QWidget, name)


class Tool(QDialog):
    TITLE = "Element Lab"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(self.TITLE)
        self.resize(1200, 760)

        # ---- Data ----
        self.data: Dict[str, dict] = load_element_data()  # symbol -> element json
        # Build a simple list ordered by atomic number if present
        def _num(el):
            try:
                return int(el.get("number") or el.get("AtomicNumber") or 10**9)
            except Exception:
                return 10**9
        self.symbols = [sym for sym, el in sorted(self.data.items(), key=lambda kv: _num(kv[1]))]

        # ---- Layout skeleton ----
        root = QVBoxLayout(self)
        self.toolbar = self._build_toolbar()
        root.addWidget(self.toolbar)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)
        root.addWidget(split, 1)

        # Left pane: sidebar (search + element list + nav buttons)
        self.sidebar = self._build_sidebar()
        split.addWidget(self.sidebar)

        # Right pane: stacked tools
        self.stack = QStackedWidget()
        split.addWidget(self.stack)

        # ---- Tools (embedded) ----
        self.viewer = _Embedded(ViewerTool)
        self.shells = _Embedded(ShellTool)
        self.isotopes = _Embedded(IsotopeTool)
        self.grapher = _Embedded(GrapherTool)
        self.comparator = _Embedded(ComparatorTool)
        self.phase = _Embedded(PhaseTool)

        for w in [self.viewer, self.shells, self.isotopes, self.grapher, self.comparator, self.phase]:
            self.stack.addWidget(w)

        # Default selection
        self.nav_select("Viewer")
        if self.symbols:
            self._select_symbol(self.symbols[0])

    # ----------------- UI builders -----------------
    def _build_toolbar(self) -> QToolBar:
        tb = QToolBar()
        tb.setIconSize(tb.iconSize())

        act_view = QAction(QIcon.fromTheme("view-list-details"), "Viewer", self)
        act_shell = QAction(QIcon.fromTheme("applications-science"), "Shells", self)
        act_iso = QAction(QIcon.fromTheme("view-pie-chart"), "Isotopes", self)
        act_graph = QAction(QIcon.fromTheme("view-scatter-plot"), "Properties", self)
        act_comp = QAction(QIcon.fromTheme("view-column"), "Compare", self)
        act_phase = QAction(QIcon.fromTheme("weather-storm"), "Phase", self)

        for a in [act_view, act_shell, act_iso, act_graph, act_comp, act_phase]:
            tb.addAction(a)

        act_view.triggered.connect(lambda: self.nav_select("Viewer"))
        act_shell.triggered.connect(lambda: self.nav_select("Shells"))
        act_iso.triggered.connect(lambda: self.nav_select("Isotopes"))
        act_graph.triggered.connect(lambda: self.nav_select("Properties"))
        act_comp.triggered.connect(lambda: self.nav_select("Compare"))
        act_phase.triggered.connect(lambda: self.nav_select("Phase"))
        return tb

    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setMinimumWidth(280)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        title = QLabel("Elements")
        title.setStyleSheet("font-weight: 600; font-size: 16px;")
        lay.addWidget(title)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search symbol, name, #...")
        self.search.textChanged.connect(self._filter_list)
        lay.addWidget(self.search)

        self.list = QListWidget()
        self.list.itemSelectionChanged.connect(self._handle_element_click)
        lay.addWidget(self.list, 1)

        # Populate list
        for sym in self.symbols:
            el = self.data.get(sym, {})
            name = el.get("name") or el.get("Element") or "Unknown"
            num = el.get("number") or el.get("AtomicNumber") or "?"
            item = QListWidgetItem(f"{sym:>3}  {name}  ({num})")
            item.setData(Qt.ItemDataRole.UserRole, sym)
            self.list.addItem(item)

        # Quick nav buttons
        nav = QHBoxLayout()
        for label in ["Viewer", "Shells", "Isotopes", "Properties", "Compare", "Phase"]:
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.clicked.connect(lambda _, L=label: self.nav_select(L))
            nav.addWidget(btn)
        lay.addLayout(nav)

        return side

    # ----------------- Interactions -----------------
    def _filter_list(self, text: str):
        t = (text or "").lower().strip()
        for i in range(self.list.count()):
            it = self.list.item(i)
            sym = it.data(Qt.ItemDataRole.UserRole)
            el = self.data.get(sym, {})
            blob = " ".join([
                sym or "", str(el.get("name", "")), str(el.get("number", "")), str(el.get("category", ""))
            ]).lower()
            it.setHidden(t not in blob)

    def _handle_element_click(self):
        it = self.list.currentItem()
        if not it:
            return
        sym = it.data(Qt.ItemDataRole.UserRole)
        if sym:
            self._select_symbol(sym)

    def _select_symbol(self, sym: str):
        """Broadcast selected symbol to all tools that accept it."""
        # Viewer: just set search to symbol and refresh
        try:
            v = self.viewer.inner  # type: ignore[attr-defined]
            if hasattr(v, "search"):
                v.search.setText(sym)
                v.update_list()
        except Exception:
            pass

        # Shells
        try:
            s = self.shells.inner
            if hasattr(s, "entry"):
                s.entry.setText(sym)
                # auto-draw (non-blocking)
                if hasattr(s, "_draw"):
                    s._draw()
        except Exception:
            pass

        # Isotope tool — fill symbol (no mass number auto-guess)
        try:
            iso = self.isotopes.inner
            if hasattr(iso, "symbol_entry"):
                iso.symbol_entry.setText(sym)
        except Exception:
            pass

        # Phase tool
        try:
            ph = self.phase.inner
            if hasattr(ph, "sym"):
                ph.sym.setText(sym)
                # Update preview at default T if you like:
                if hasattr(ph, "_predict"):
                    ph._predict()
        except Exception:
            pass

        # Comparator — set the first combobox to this symbol
        try:
            comp = self.comparator.inner
            if hasattr(comp, "element_boxes") and comp.element_boxes:
                comp.element_boxes[0].setCurrentText(sym)
                # keep others unchanged
                if hasattr(comp, "_compare"):
                    comp._compare()
        except Exception:
            pass

    def nav_select(self, label: str):
        mapping = {
            "Viewer": self.viewer,
            "Shells": self.shells,
            "Isotopes": self.isotopes,
            "Properties": self.grapher,
            "Compare": self.comparator,
            "Phase": self.phase,
        }
        w = mapping.get(label)
        if not w:
            QMessageBox.warning(self, "Unknown", f"No view named '{label}'.")
            return
        self.stack.setCurrentWidget(w)
        self.setWindowTitle(f"{self.TITLE} — {label}")