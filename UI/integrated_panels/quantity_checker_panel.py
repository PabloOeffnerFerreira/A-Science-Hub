from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt
from tools.panel_tools import quantity_checker as qc

class ScientificQuantityChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 200)
        self._region = "EU"
        self._mode = "Quantity"
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)
        form = QFormLayout()
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)
        self.region = QComboBox()
        self.region.addItems(qc.regions())
        self.search_mode = QComboBox()
        self.search_mode.addItems(["Quantity", "Q Symbol", "Unit Symbol"])
        self.selector = QComboBox()
        self._refill_selector()
        self.q_name = QLineEdit(); self.q_name.setReadOnly(True); self.q_name.setFixedHeight(20)
        self.q_sym  = QLineEdit(); self.q_sym.setReadOnly(True);  self.q_sym.setFixedHeight(20)
        self.u_name = QLineEdit(); self.u_name.setReadOnly(True); self.u_name.setFixedHeight(20)
        self.u_sym  = QLineEdit(); self.u_sym.setReadOnly(True);  self.u_sym.setFixedHeight(20)
        form.addRow(self._lbl("Region"), self.region)
        form.addRow(self._lbl("Search by"), self.search_mode)
        form.addRow(self._lbl("Select"), self.selector)
        form.addRow(self._lbl("Q.Name"), self.q_name)
        form.addRow(self._lbl("Q.Symbol"), self.q_sym)
        form.addRow(self._lbl("U.Name"), self.u_name)
        form.addRow(self._lbl("U.Symbol"), self.u_sym)
        root.addLayout(form)
        self.region.currentTextChanged.connect(self._on_region_changed)
        self.search_mode.currentTextChanged.connect(self._on_mode_changed)
        self.selector.currentTextChanged.connect(self._on_select_changed)
        self._on_select_changed(self.selector.currentText())

    def _lbl(self, t):
        l = QLabel(t)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return l

    def _refill_selector(self):
        self.selector.blockSignals(True)
        self.selector.clear()
        self.selector.addItems(qc.options_for(self._region, self._mode))
        self.selector.blockSignals(False)

    def _on_region_changed(self, r):
        self._region = r
        self._refill_selector()
        self._on_select_changed(self.selector.currentText())

    def _on_mode_changed(self, mode):
        self._mode = mode
        self._refill_selector()
        self._on_select_changed(self.selector.currentText())

    def _on_select_changed(self, key):
        if not key:
            self.q_name.clear(); self.q_sym.clear(); self.u_name.clear(); self.u_sym.clear()
            return
        d = qc.describe(self._region, self._mode, key)
        if not d:
            self.q_name.clear(); self.q_sym.clear(); self.u_name.clear(); self.u_sym.clear()
            return
        self.q_name.setText(d["q_name"])
        self.q_sym.setText(d["q_sym"])
        self.u_name.setText(d["u_name"])
        self.u_sym.setText(d["u_sym"])
