
from __future__ import annotations
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QCheckBox, QComboBox
)
from core.data.functions.geo_utils import load_minerals, load_favs, save_favs

# Preferred key options per field (robust to varying CSV schemas)
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

def _num(row: Dict[str, Any], keys) -> Optional[float]:
    s = _first_nonempty(row, keys)
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return None

def _type_value(row: Dict[str, Any]) -> str:
    return _first_nonempty(row, TYPE_KEYS) or ""

class Tool(QDialog):
    TITLE = "Mineral Explorer"

    def __init__(self):
        super().__init__()
        self.setMinimumSize(960, 640)

        # Data
        self.data: List[Dict[str, Any]] = load_minerals()
        self.favs = load_favs()

        # UI
        root = QVBoxLayout(self)

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

        # Debounce to avoid lag
        self._debounce = QTimer(self); self._debounce.setSingleShot(True); self._debounce.setInterval(200)
        self._debounce.timeout.connect(self._rebuild)

        # Signals
        self.refresh_btn.clicked.connect(self._rebuild)
        self.q.textChanged.connect(lambda _=None: self._debounce.start())
        self.only_favs.stateChanged.connect(self._rebuild)
        self.type_box.currentIndexChanged.connect(self._rebuild)
        self.toggle_fav.clicked.connect(self._toggle_fav)
        self.copy_row.clicked.connect(self._copy_row)

        self._rebuild(initial=True)

    def _match(self, row: dict, q: str) -> bool:
        pieces = [
            _first_nonempty(row, NAME_KEYS) or "",
            _first_nonempty(row, FORMULA_KEYS) or "",
            _first_nonempty(row, SYSTEM_KEYS) or "",
            str(row.get("Notes","")),
            _type_value(row),
        ]
        return q in " ".join(pieces).lower()

    def _rebuild(self, initial: bool = False):
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
            if q and not self._match(r, q):
                continue
            items.append(r)

        # Populate table (sorting off during fill)
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

                h = _num(r, HARDNESS_KEYS)
                sg = _num(r, SG_KEYS)

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
        # Update star without rebuilding everything
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
