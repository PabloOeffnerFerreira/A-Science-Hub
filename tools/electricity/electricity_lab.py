from __future__ import annotations

from typing import Callable, Dict

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QSplitter, QStackedWidget,
    QFrame, QToolBar, QMessageBox
)

# -------- Explicit imports of your existing tools --------
from labs.electricty.ohms_law import Tool as OhmsLawTool
from labs.electricty.rc_circuit_helper import Tool as RcCircuitHelperTool
from labs.electricty.coulomb_force_calculator import Tool as CoulombForceTool
from labs.electricty.electric_field_visualiser import Tool as ElectricFieldTool
from labs.electricty.magnetic_field_calculator import Tool as MagFieldCalcTool
from labs.electricty.magnetic_flux_induction import Tool as MagFluxInductionTool
from labs.electricty.magnoline_tool import Tool as MagnolineTool
from labs.electricty.ferromagnetism_helper import Tool as FerromagnetismTool

from core.data.paths import NOTES_PATH

class _Embedded(QWidget):

    """Wrap a QDialog subclass so it behaves as an embeddable widget (same as DNA/Element labs)."""
    def __init__(self, dialog_cls: Callable[[], QDialog], parent: QWidget | None = None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.inner = dialog_cls()
        # Present dialog as a child widget (no window chrome)
        self.inner.setParent(self)
        self.inner.setWindowFlag(Qt.WindowType.Widget, True)
        lay.addWidget(self.inner)


class Tool(QDialog):
    TITLE = "Electricity Lab"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(self.TITLE)
        self.resize(1200, 760)

        # ----- Build pages (right stack) first -----
        self.stack = QStackedWidget()
        self.pages: Dict[str, _Embedded] = {
            "Ohm's Law":                 _Embedded(OhmsLawTool),
            "RC Circuit Helper":         _Embedded(RcCircuitHelperTool),
            "Coulomb Force":             _Embedded(CoulombForceTool),
            "Electric Field Visualiser": _Embedded(ElectricFieldTool),
            "Magnetic Field Calculator": _Embedded(MagFieldCalcTool),
            "Magnetic Flux Induction":   _Embedded(MagFluxInductionTool),
            "Magnoline (B-field lines)": _Embedded(MagnolineTool),
            "Ferromagnetism Helper":     _Embedded(FerromagnetismTool),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        # ----- Root layout with splitter (left sidebar | right stack) -----
        root = QVBoxLayout(self)
        split = QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)
        root.addWidget(split, 1)

        # Left sidebar (kept simple, like other labs)
        self.sidebar = self._build_sidebar()
        split.addWidget(self.sidebar)

        # Right side (toolbar + stack)
        right = QFrame()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        self.toolbar = self._build_toolbar()
        right_lay.addWidget(self.toolbar)
        right_lay.addWidget(self.stack, 1)
        split.addWidget(right)

        # Default page
        self.nav_select("Ohm's Law")

    # ----------------- Toolbar -----------------
    def _build_toolbar(self) -> QToolBar:
        tb = QToolBar(self)
        tb.setMovable(False)
        tb.setFloatable(False)

        def add_nav(label: str, icon_name: str = "applications-science"):
            act = QAction(QIcon.fromTheme(icon_name), label, self)
            act.triggered.connect(lambda _, L=label: self.nav_select(L))
            tb.addAction(act)

        # Add actions in a logical order (Basics → Fields → Circuits → Materials)
        add_nav("Ohm's Law", "accessories-calculator")
        add_nav("Coulomb Force", "help-about")
        tb.addSeparator()
        add_nav("Electric Field Visualiser", "view-media-visualization")
        add_nav("Magnetic Field Calculator", "view-media-equalizer")
        add_nav("Magnetic Flux Induction", "preferences-system-power")
        add_nav("Magnoline (B-field lines)", "preferences-desktop-magnet")
        tb.addSeparator()
        add_nav("RC Circuit Helper", "media-playlist-repeat")
        tb.addSeparator()
        add_nav("Ferromagnetism Helper", "preferences-desktop")

        return tb

    # ----------------- Sidebar -----------------
    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setMinimumWidth(320)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        title = QLabel("Tools")
        title.setStyleSheet("font-weight:600; font-size:16px;")
        lay.addWidget(title)

        # Quick list of tools (double-click to switch)
        self.tool_list = QListWidget()
        for label in self.pages.keys():
            self.tool_list.addItem(QListWidgetItem(label))
        self.tool_list.itemDoubleClicked.connect(lambda it: self.nav_select(it.text()))
        lay.addWidget(self.tool_list, 1)

        # Small notes pad (matches DNA Lab idea of having a sidebar workspace)
        lay.addWidget(QLabel("Notes"))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Write experiment notes, quick derivations, or TODOs…")
        self.notes.setFixedHeight(130)
        lay.addWidget(self.notes)
        self.btn_save_notes = QPushButton("Save Notes")
        self.btn_save_notes.clicked.connect(self._save_notes)
        lay.addWidget(self.btn_save_notes)

        # Quick constants (read-only, informational)
        lay.addWidget(QLabel("Reference constants (read-only)"))
        consts = QFrame()
        cl = QVBoxLayout(consts)
        cl.setContentsMargins(6, 6, 6, 6)
        self.eps0 = QLineEdit("ε₀ = 8.854187817e-12 F/m"); self.eps0.setReadOnly(True)
        self.mu0  = QLineEdit("μ₀ = 4π×1e-7 H/m  (≈ 1.256637062e-6)"); self.mu0.setReadOnly(True)
        self.c0   = QLineEdit("c ≈ 2.99792458e8 m/s"); self.c0.setReadOnly(True)
        cl.addWidget(self.eps0)
        cl.addWidget(self.mu0)
        cl.addWidget(self.c0)
        lay.addWidget(consts)   

        return side

    # Saving notes

    def _save_notes(self):
        text = self.notes.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Save Notes", "Notes are empty.")
            return
        try:
            NOTES_PATH.mkdir(parents=True, exist_ok=True)
            file = NOTES_PATH / "electricity_lab_notes.txt"  # single file, append
            with file.open("a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(text + "\n\n")
            # Show absolute path so you know exactly where it saved
            QMessageBox.information(self, "Save Notes", f"Appended to:\n{file.resolve()}")
        except Exception as e:
            QMessageBox.critical(self, "Save Notes", f"Failed to save notes:\n{e}")


    # ----------------- Navigation -----------------
    def nav_select(self, label: str):
        page = self.pages.get(label)
        if not page:
            QMessageBox.warning(self, "Unknown tool", f"No view named “{label}”.")
            return
        self.stack.setCurrentWidget(page)
        self.setWindowTitle(f"{self.TITLE} — {label}")

        # Sync list selection
        matches = self.tool_list.findItems(label, Qt.MatchFlag.MatchExactly)
        if matches:
            self.tool_list.setCurrentItem(matches[0])