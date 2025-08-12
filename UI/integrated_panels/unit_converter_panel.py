from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt
from tools.panel_tools.unit_converter import convert_value
from core.data.functions import units

class UnitConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        cat_row = QHBoxLayout()
        cat_row.addWidget(QLabel("Category:"))
        self.category = QComboBox()
        self.category.addItems(sorted(units.units_for_category.__globals__['conversion_data'].keys()))
        cat_row.addWidget(self.category)
        layout.addLayout(cat_row)

        from_row = QHBoxLayout()
        from_row.addWidget(QLabel("From:"))
        self.from_input = QLineEdit()
        self.from_input.setPlaceholderText("Value")
        self.from_prefix = QComboBox()
        self.from_unit = QComboBox()
        from_row.addWidget(self.from_input, 2)
        from_row.addWidget(self.from_prefix, 1)
        from_row.addWidget(self.from_unit, 2)
        layout.addLayout(from_row)

        to_row = QHBoxLayout()
        to_row.addWidget(QLabel("To:"))
        self.to_output = QLineEdit()
        self.to_output.setReadOnly(True)
        self.to_prefix = QComboBox()
        self.to_unit = QComboBox()
        to_row.addWidget(self.to_output, 2)
        to_row.addWidget(self.to_prefix, 1)
        to_row.addWidget(self.to_unit, 2)
        layout.addLayout(to_row)

        self.result = QLabel("")
        self.result.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.result)

        self.category.currentTextChanged.connect(self._on_category_changed)
        self.from_unit.currentTextChanged.connect(self._on_unit_changed)
        self.to_unit.currentTextChanged.connect(self._on_unit_changed)
        self.from_prefix.currentTextChanged.connect(self._update_preview)
        self.to_prefix.currentTextChanged.connect(self._update_preview)
        self.from_input.textChanged.connect(self._update_preview)

        self._on_category_changed(self.category.currentText())

    def _refill(self, combo, items):
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(items)
        combo.blockSignals(False)

    def _on_category_changed(self, cat: str):
        bases = units.units_for_category(cat)
        self._refill(self.from_unit, bases)
        self._refill(self.to_unit, bases)
        prefs = [""] + units.ordered_prefixes()
        self._refill(self.from_prefix, prefs)
        self._refill(self.to_prefix, prefs)
        self._toggle_prefix_enabled()
        self._update_preview()

    def _toggle_prefix_enabled(self):
        cat = self.category.currentText()
        self.from_prefix.setEnabled(units.supports_si(cat, self.from_unit.currentText()))
        self.to_prefix.setEnabled(units.supports_si(cat, self.to_unit.currentText()))

    def _on_unit_changed(self):
        self._toggle_prefix_enabled()
        self._update_preview()

    def _update_preview(self):
        base_out, formatted = convert_value(
            self.category.currentText(),
            self.from_unit.currentText(),
            self.from_prefix.currentText(),
            self.to_unit.currentText(),
            self.to_prefix.currentText(),
            self.from_input.text()
        )
        if formatted:
            self.to_output.setText(f"{base_out:.6g}")
            self.result.setText(formatted)
        else:
            self.to_output.setText("")
            self.result.setText("")
