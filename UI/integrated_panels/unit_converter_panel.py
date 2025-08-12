from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from tools.panel_tools.unit_converter import UnitConverter
from core.data.units import conversion_data, si_prefixes


class UnitConverterWidget(QWidget):
    """Unit converter panel widget"""
    CATEGORIES_ORDER = [
        "Length", "Mass", "Area", "Volume", "Time",
        "Speed", "Acceleration", "Force", "Pressure",
        "Energy", "Power", "Temperature", "Frequency",
        "Angle", "Electric Current", "Voltage", "Resistance",
        "Charge", "Capacitance", "Inductance", "Luminous Intensity"
    ]

    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 120)

        self.converter = UnitConverter()
        self._categories = getattr(conversion_data, "conversion_data", {})
        self._si_prefixes = getattr(si_prefixes, "si_prefixes", {"": 1.0})
        self._si_bases = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        cat_row = QHBoxLayout()
        cat_row.addWidget(QLabel("Category:"))
        self.category = QComboBox()
        self._fill_categories()
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

    def _fill_categories(self) -> None:
        """Fill categories by usefulness order"""
        present = set(self._categories.keys())
        ordered = [c for c in self.CATEGORIES_ORDER if c in present]
        leftover = [c for c in self._categories.keys() if c not in ordered]
        self.category.addItems(ordered + leftover)

    def _si_bases_from(self, data: dict) -> set[str]:
        """Get SI-base list from category data"""
        return set(
            data.get("SI")
            or data.get("si")
            or data.get("si_units")
            or data.get("SI_UNITS")
            or []
        )

    def _ordered_prefixes(self) -> list[str]:
        """Return ordered prefix list"""
        order = ["", "k", "h", "da", "d", "c", "m", "μ", "n", "M", "G", "T", "p", "f"]
        return [p for p in order if p in self._si_prefixes]

    def _refill(self, combo: QComboBox, items: list[str]) -> None:
        """Refill a QComboBox with items"""
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(items)
        combo.blockSignals(False)

    def _order_units_si_first(self, bases: list[str]) -> list[str]:
        """Reorder units putting SI base first"""
        if not self._si_bases:
            return bases
        return sorted(bases, key=lambda u: (0 if u in self._si_bases else 1, bases.index(u)))

    def _on_category_changed(self, cat: str) -> None:
        """Handle category change"""
        data = self._categories.get(cat, {})
        bases = list(data.get("units", {}).keys())
        self._si_bases = self._si_bases_from(data)

        bases = self._order_units_si_first(bases)

        self._refill(self.from_unit, bases)
        self._refill(self.to_unit, bases)

        pref_items = self._ordered_prefixes()
        self._refill(self.from_prefix, pref_items)
        self._refill(self.to_prefix, pref_items)

        if self.from_unit.count(): self.from_unit.setCurrentIndex(0)
        if self.to_unit.count():   self.to_unit.setCurrentIndex(0)
        if self.from_prefix.count(): self.from_prefix.setCurrentIndex(0)
        if self.to_prefix.count():   self.to_prefix.setCurrentIndex(0)

        self._toggle_prefix_enabled()
        self._update_preview()

    def _unit_supports_si(self, unit: str) -> bool:
        """Check if base unit supports SI prefix"""
        return unit in self._si_bases

    def _toggle_prefix_enabled(self) -> None:
        """Enable/disable prefix boxes"""
        self.from_prefix.setEnabled(self._unit_supports_si(self.from_unit.currentText()))
        self.to_prefix.setEnabled(self._unit_supports_si(self.to_unit.currentText()))

    def _prefix_factor(self, prefix_combo: QComboBox, unit_combo: QComboBox) -> float:
        """Get prefix factor for a unit"""
        unit = unit_combo.currentText().strip()
        if not self._unit_supports_si(unit):
            return 1.0
        p = prefix_combo.currentText().strip()
        return float(self._si_prefixes.get(p, 1.0))

    def _composed_unit_label(self, prefix_combo: QComboBox, unit_combo: QComboBox) -> str:
        """Compose display unit with prefix if valid"""
        u = unit_combo.currentText().strip()
        if not self._unit_supports_si(u):
            return u
        p = prefix_combo.currentText().strip()
        return f"{p}{u}"

    def _on_unit_changed(self) -> None:
        """Handle unit combo changes"""
        self._toggle_prefix_enabled()
        self._update_preview()

    def _read_value(self):
        """Read numeric value"""
        txt = self.from_input.text().strip().replace(",", ".")
        try:
            return float(txt)
        except Exception:
            return None

    def _update_preview(self) -> None:
        """Recompute and update UI"""
        v = self._read_value()
        if v is None:
            self.to_output.setText("")
            self.result.setText("")
            return

        cat = self.category.currentText()
        f_unit = self.from_unit.currentText().strip()
        t_unit = self.to_unit.currentText().strip()

        f_factor = self._prefix_factor(self.from_prefix, self.from_unit)
        t_factor = self._prefix_factor(self.to_prefix, self.to_unit)

        try:
            base_out = self.converter.convert(v * f_factor, f_unit, t_unit, cat)
            out = base_out / t_factor
            self.to_output.setText(f"{out:.6g}")
            left = f"{v:g} {self._composed_unit_label(self.from_prefix, self.from_unit)}"
            right = f"{out:.6g} {self._composed_unit_label(self.to_prefix, self.to_unit)}"
            self.result.setText(f"{left} = {right}")
        except Exception:
            self.to_output.setText("")
            self.result.setText("")