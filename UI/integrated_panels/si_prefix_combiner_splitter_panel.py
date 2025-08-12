from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from tools.panel_tools import si_prefix_combiner_splitter
from core.data.units.si_prefixes import si_prefixes
from core.data.functions import si_prefix_tools

class SiPrefixCombinerSplitter(QWidget):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 140)

        self._si_units = si_prefix_tools.collect_si_units()

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
        self.pref_in.addItems([""] + list(si_prefixes.keys()))
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
        self.pref_out.addItems([""] + list(si_prefixes.keys()))

        out_row.addWidget(self.val_out, 2)
        out_row.addWidget(self.pref_out, 1)
        form.addRow(QLabel("Output"), out_row)

        self.base_out = QLineEdit()
        self.base_out.setReadOnly(True)
        self.base_out.setFixedHeight(20)
        form.addRow(QLabel("Base Value"), self.base_out)

        root.addLayout(form)

        self.val_in.textEdited.connect(self._update_output)
        self.pref_in.currentTextChanged.connect(self._update_output)
        self.unit_in.currentTextChanged.connect(self._update_output)
        self.pref_out.currentTextChanged.connect(self._update_output)

    def _update_output(self):
        out_val, base_val = si_prefix_combiner_splitter.combine_split(
            self.val_in.text().strip(),
            self.pref_in.currentText(),
            self.unit_in.currentText(),
            self.pref_out.currentText()
        )
        if out_val is None:
            self.val_out.clear()
            self.base_out.clear()
            return
        self.val_out.setText(out_val)
        self.base_out.setText(base_val)
