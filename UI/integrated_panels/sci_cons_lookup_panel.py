from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt
from core.data.databases.constants_data import constants_data

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
        self.category.addItems(list(constants_data.keys()))

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

        # Labels with explicit alignment
        form.addRow(self._aligned_label("Category"), self.category)
        form.addRow(self._aligned_label("Constant"), self.constant)
        form.addRow(self._aligned_label("Value"), self.value)
        form.addRow(self._aligned_label("Unit"), self.unit)
        form.addRow(self._aligned_label("About"), self.desc)

        root.addLayout(form)

        self.category.currentTextChanged.connect(self._on_category_changed)
        self.constant.currentTextChanged.connect(self._on_constant_changed)

        self._on_constant_changed(self.constant.currentText())

    def _aligned_label(self, text):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return lbl

    def _refill_constants(self, cat: str):
        self.constant.blockSignals(True)
        self.constant.clear()
        self.constant.addItems(list(constants_data.get(cat, {}).keys()))
        self.constant.blockSignals(False)

    def _on_category_changed(self, cat: str):
        self._refill_constants(cat)
        self._on_constant_changed(self.constant.currentText())

    def _on_constant_changed(self, name: str):
        cat = self.category.currentText()
        d = constants_data.get(cat, {}).get(name, None)
        if not d:
            self.value.clear()
            self.unit.clear()
            self.desc.clear()
            return
        val = d.get("value", "")
        try:
            sval = f"{float(val):.12g}"
        except Exception:
            sval = str(val)
        self.value.setText(sval)
        self.unit.setText(d.get("unit", ""))
        exact = "Yes" if d.get("exact", False) else "No"
        self.desc.setText(f"{d.get('description','')} — Exact: {exact}")
