
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QFont, QBrush, QColor
from core.data.functions.chemistry_utils import load_element_data

# We persist favorites via central path if available
try:
    from core.data.paths import ELEMENT_FAVS_PATH as FAVS_PATH
except Exception:
    FAVS_PATH = None

def _load_favs():
    if not FAVS_PATH:
        return set()
    try:
        import json, os
        if not os.path.exists(FAVS_PATH):
            return set()
        with open(FAVS_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def _save_favs(favs):
    if not FAVS_PATH:
        return
    try:
        import json, os
        os.makedirs(os.path.dirname(FAVS_PATH), exist_ok=True)
        with open(FAVS_PATH, "w", encoding="utf-8") as f:
            json.dump(list(favs), f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _flatten_elements(mapping):
    els = []
    for el in mapping.values():
        e = dict(el)
        e["search_blob"] = " ".join([
            str(e.get("name", "")),
            str(e.get("symbol", "")),
            str(e.get("number", "")),
            str(e.get("category", "")),
            str(e.get("shells", "")),
            str(e.get("electron_configuration", "")),
            str(e.get("appearance", "")),
            str(e.get("summary", "")),
        ]).lower()
        els.append(e)
    # sort by atomic number if available
    try:
        els.sort(key=lambda d: int(d.get("number") or d.get("AtomicNumber") or 0))
    except Exception:
        pass
    return els

class Tool(QDialog):
    TITLE = "Element Viewer"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(720)
        self.setMinimumHeight(450)

        self.elements_map = load_element_data()
        self.elements = _flatten_elements(self.elements_map)
        self.favs = _load_favs()
        self.filtered = list(self.elements)

        main = QVBoxLayout(self)

        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search name, symbol, number, etc...")
        self.fav_cb = QCheckBox("Show Favorites Only")
        self.refresh_btn = QPushButton("Refresh")
        bar.addWidget(QLabel("Search:"))
        bar.addWidget(self.search)
        bar.addWidget(self.fav_cb)
        bar.addWidget(self.refresh_btn)
        main.addLayout(bar)

        self.list = QListWidget()
        main.addWidget(self.list)

        self.fav_btn = QPushButton("Toggle Favorite")
        main.addWidget(self.fav_btn)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        font = QFont("Consolas", 10)
        self.details.setFont(font)
        main.addWidget(self.details, 1)

        self.search.textChanged.connect(self.update_list)
        self.fav_cb.stateChanged.connect(self.update_list)
        self.refresh_btn.clicked.connect(self.update_list)
        self.list.currentItemChanged.connect(self.show_details)
        self.fav_btn.clicked.connect(self.toggle_favorite)

        self.update_list()

    def update_list(self):
        text = self.search.text().lower().strip()
        show_favs = self.fav_cb.isChecked()
        self.list.clear()
        self.filtered = []
        for el in self.elements:
            if show_favs and el.get("symbol") not in self.favs:
                continue
            if text and text not in el["search_blob"]:
                continue
            self.filtered.append(el)
            label = f"{el.get('symbol',''):>3}  {el.get('name',''):<12} ({el.get('number','?')})"
            item = QListWidgetItem(label)
            if el.get("symbol") in self.favs:
                item.setForeground(QBrush(QColor("#d4af37")))  # gold
                item.setFont(QFont("", 10, QFont.Weight.Bold))
            else:
                item.setFont(QFont("", 10))
            item.setData(32, el)  # store dict
            self.list.addItem(item)
        if self.filtered:
            self.list.setCurrentRow(0)
        else:
            self.details.clear()

    def show_details(self, item):
        if not item:
            self.details.clear()
            return
        el = item.data(32)
        out = [
            f"<b>{el.get('name','?')} ({el.get('symbol','?')})</b>",
            f"Atomic Number: <b>{el.get('number','?')}</b>",
            f"Category: {el.get('category','—')}",
            f"Atomic Mass: {el.get('atomic_mass','—')} g/mol",
            f"Shells: {', '.join(str(x) for x in el.get('shells', []))}",
            f"Electron Config: {el.get('electron_configuration','—')}",
            f"Density: {el.get('density','—')} g/cm³",
            f"Melting Point: {el.get('melt','—')} K",
            f"Boiling Point: {el.get('boil','—')} K",
            f"Appearance: {el.get('appearance','—')}",
            f"Summary: <br>{el.get('summary','')}",
        ]
        self.details.setHtml("<br><br>".join(out))

    def toggle_favorite(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.information(self, "No Selection", "Select an element first.")
            return
        el = item.data(32)
        symbol = el.get("symbol")
        if not symbol:
            return
        if symbol in self.favs:
            self.favs.remove(symbol)
        else:
            self.favs.add(symbol)
        _save_favs(self.favs)
        self.update_list()
