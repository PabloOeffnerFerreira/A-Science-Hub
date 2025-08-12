from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt
from tools.panel_tools import scientific_constants_lookup as scl

class ScientificConstantsLookupWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 200)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.category = QComboBox()
        self.category.addItems(scl.list_categories())

        self.constant = QComboBox()
        self._refill_constants(self.category.currentText())

        self.value = QLineEdit()
        self.value.setReadOnly(True)
        self.value.setFixedHeight(20)

        self.unit = QLineEdit()
        self.unit.setReadOnly(True)
        self.unit.setFixedHeight(20)

        self.desc = QLabel("")
        self.desc.setWordWrap(True)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        form.addRow(self._lbl("Category"), self.category)
        form.addRow(self._lbl("Constant"), self.constant)
        form.addRow(self._lbl("Value"), self.value)
        form.addRow(self._lbl("Unit"), self.unit)
        form.addRow(self._lbl("About"), self.desc)

        root.addLayout(form)

        self.category.currentTextChanged.connect(self._on_category_changed)
        self.constant.currentTextChanged.connect(self._on_constant_changed)

        self._on_constant_changed(self.constant.currentText())

    def _lbl(self, text):
        l = QLabel(text)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return l

    def _refill_constants(self, cat: str):
        names = [r["name"] for r in scl.list_constants(cat)]
        self.constant.blockSignals(True)
        self.constant.clear()
        self.constant.addItems(names)
        self.constant.blockSignals(False)

    def _on_category_changed(self, cat: str):
        self._refill_constants(cat)
        self._on_constant_changed(self.constant.currentText())

    def _fmt_val(self, v):
        try:
            return f"{float(v):.12g}"
        except Exception:
            return str(v)

    def _on_constant_changed(self, name: str):
        cat = self.category.currentText()
        rec = scl.get(cat, name)
        if not rec:
            self.value.clear()
            self.unit.clear()
            self.desc.clear()
            return
        self.value.setText(self._fmt_val(rec["value"]))
        self.unit.setText(rec.get("unit") or "")
        exact = "Yes" if rec.get("exact") else "No"
        self.desc.setText(f"{rec.get('description') or ''} — Exact: {exact}")
