from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from core.data.units.conversion_data import conversion_data
from core.data.units.si_prefixes import si_prefixes

class SiPrefixCombinerSplitter(QWidget):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 140)

        self._si_prefixes = si_prefixes
        self._si_units = self._collect_si_units()
        self._unit_factor = self._build_unit_factors()

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)

        in_row = QHBoxLayout()
        self.val_in = QLineEdit()
        self.val_in.setFixedHeight(20)
        dv = QDoubleValidator(-1e300, 1e300, 12)
        dv.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.val_in.setValidator(dv)

        self.pref_in = QComboBox()
        for p in ["", "k","h","da","d","c","m","μ","n","M","G","T","p","f"]:
            if p in self._si_prefixes:
                self.pref_in.addItem(p)

        self.unit_in = QComboBox()
        self.unit_in.addItems(self._si_units)

        in_row.addWidget(self.val_in, 2)
        in_row.addWidget(self.pref_in, 1)
        in_row.addWidget(self.unit_in, 2)
        form.addRow(QLabel("Input"), in_row)

        out_row = QHBoxLayout()
        self.val_out = QLineEdit()
        self.val_out.setReadOnly(True)
        self.val_out.setFixedHeight(20)

        self.pref_out = QComboBox()
        for p in ["", "k","h","da","d","c","m","μ","n","M","G","T","p","f"]:
            if p in self._si_prefixes:
                self.pref_out.addItem(p)

        out_row.addWidget(self.val_out, 2)
        out_row.addWidget(self.pref_out, 1)
        form.addRow(QLabel("Output"), out_row)

        self.base_out = QLineEdit()
        self.base_out.setReadOnly(True)
        self.base_out.setFixedHeight(20)
        form.addRow(QLabel("Base Value"), self.base_out)

        root.addLayout(form)

        self.val_in.textEdited.connect(self._recompute)
        self.pref_in.currentTextChanged.connect(self._recompute)
        self.unit_in.currentTextChanged.connect(self._recompute)
        self.pref_out.currentTextChanged.connect(self._recompute)

    def _collect_si_units(self):
        ordered = []
        seen = set()
        for _, data in conversion_data.items():
            for u in data.get("SI", []):
                if u not in seen:
                    ordered.append(u); seen.add(u)
        return ordered

    def _build_unit_factors(self):
        m = {}
        for _, data in conversion_data.items():
            units = data.get("units", {})
            for u in data.get("SI", []):
                if u in units:
                    m[u] = units[u]
        return m

    def _recompute(self):
        t = self.val_in.text().strip()
        if not t:
            self.val_out.clear(); self.base_out.clear(); return
        try:
            v = float(t)
        except ValueError:
            self.val_out.clear(); self.base_out.clear(); return

        pin = self.pref_in.currentText()
        uin = self.unit_in.currentText()
        pout = self.pref_out.currentText()

        fin = float(self._si_prefixes.get(pin, 1.0))
        fout = float(self._si_prefixes.get(pout, 1.0))
        ufac = float(self._unit_factor.get(uin, 1.0))

        base_val = v * fin * ufac
        out_val = base_val / fout

        self.base_out.setText(f"{base_val:.12g} {uin}")
        self.val_out.setText(f"{out_val:.12g}")