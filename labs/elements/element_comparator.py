
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QCheckBox, QLineEdit, QMessageBox, QWidget, QTabWidget, QAbstractItemView
)
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtCore import Qt
from core.data.functions.chemistry_utils import load_element_data, CATEGORIES, PROPERTY_METADATA

class Tool(QDialog):
    TITLE = "Element Comparator"

    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 600)
        self.data = load_element_data()

        main = QVBoxLayout(self)

        elem_row = QHBoxLayout()
        elem_row.addWidget(QLabel("Select Elements:"))
        self.element_boxes = []
        for i in range(3):
            box = QComboBox()
            box.setEditable(True)
            box.addItems(sorted(self.data.keys()))
            box.setCurrentIndex(i)
            box.setFixedWidth(150)
            self.element_boxes.append(box)
            elem_row.addWidget(box)
        main.addLayout(elem_row)

        self.tabs = QTabWidget()
        self.prop_checkboxes = {}
        for category in CATEGORIES:
            tab = QWidget(); tlay = QVBoxLayout(tab)
            sel = QHBoxLayout()
            select_all = QPushButton("Select All")
            select_none = QPushButton("Select None")
            sel.addWidget(select_all); sel.addWidget(select_none)
            tlay.addLayout(sel)

            checks = []
            for key, meta in PROPERTY_METADATA.items():
                if meta["category"] == category:
                    chk = QCheckBox(meta["label"]); chk.key = key; chk.setChecked(True); chk.setToolTip(meta["desc"])
                    checks.append(chk); tlay.addWidget(chk)
            self.prop_checkboxes[category] = checks
            select_all.clicked.connect(lambda _, c=category: self._set_all(c, True))
            select_none.clicked.connect(lambda _, c=category: self._set_all(c, False))
            self.tabs.addTab(tab, category)
        main.addWidget(self.tabs)

        flt = QHBoxLayout()
        flt.addWidget(QLabel("Filter properties:")); self.filter_input = QLineEdit(); flt.addWidget(self.filter_input)
        self.filter_input.textChanged.connect(self._filter)
        main.addLayout(flt)

        self.compare_btn = QPushButton("Compare"); main.addWidget(self.compare_btn)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        main.addWidget(self.table)

        self.compare_btn.clicked.connect(self._compare)

    def _set_all(self, category, checked):
        for chk in self.prop_checkboxes.get(category, []):
            chk.setChecked(checked)

    def _filter(self, text):
        t = text.lower()
        for chks in self.prop_checkboxes.values():
            for chk in chks:
                chk.setVisible(t in chk.text().lower() or t in chk.toolTip().lower())

    def _fmt(self, key, val):
        if val is None:
            return "—"
        unit = PROPERTY_METADATA.get(key, {}).get("unit", "")
        if isinstance(val, (int, float)):
            return f"{val:,.3f} {unit}".strip()
        if isinstance(val, list):
            return ", ".join(str(x) for x in val)
        return str(val)

    def _compare(self):
        elements = [b.currentText().strip() for b in self.element_boxes]
        if len(set(elements)) != len(elements):
            QMessageBox.warning(self, "Invalid Selection", "Select different elements."); return
        for el in elements:
            if el not in self.data:
                QMessageBox.warning(self, "Invalid Element", f"'{el}' not found."); return

        keys = []
        for chks in self.prop_checkboxes.values():
            keys.extend(chk.key for chk in chks if chk.isChecked())

        self.table.clear()
        self.table.setRowCount(len(keys))
        self.table.setColumnCount(len(elements) + 1)
        self.table.setHorizontalHeaderLabels(["Property"] + elements)

        for i, key in enumerate(keys):
            meta = PROPERTY_METADATA.get(key, {})
            prop_label = meta.get("label", key)
            it = QTableWidgetItem(prop_label); it.setToolTip(meta.get("desc","")); self.table.setItem(i, 0, it)
            vals = []
            for col, el in enumerate(elements, start=1):
                v = self.data[el].get(key)
                self.table.setItem(i, col, QTableWidgetItem(self._fmt(key, v)))
                vals.append(v)

            numeric_vals = [v for v in vals if isinstance(v, (int, float))]
            if numeric_vals:
                mx, mn = max(numeric_vals), min(numeric_vals)
                for col, v in enumerate(vals, start=1):
                    if v is None or not isinstance(v, (int, float)):
                        continue
                    item = self.table.item(i, col); font = item.font()
                    if v == mx:
                        font.setBold(True); item.setForeground(QBrush(QColor("blue")))
                    elif v == mn:
                        font.setItalic(True); item.setForeground(QBrush(QColor("red")))
                    item.setFont(font)
            else:
                non_null = [v for v in vals if v is not None]
                if len(set(non_null)) > 1:
                    for col, v in enumerate(vals, start=1):
                        if v is None: continue
                        item = self.table.item(i, col); f = item.font(); f.setItalic(True); item.setFont(f)
