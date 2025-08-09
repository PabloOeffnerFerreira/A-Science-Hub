from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QCheckBox, QSizePolicy, QFormLayout
)
from PyQt6.QtCore import Qt


class NotationConverterWidget(QWidget):
    """Decimal ↔ scientific notation converter panel"""
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(340, 120)

        self._updating = False

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(2)

        top = QHBoxLayout()
        top.setSpacing(4)
        top.addWidget(QLabel("Sig figs:"))
        self.sigfigs = QComboBox()
        self.sigfigs.addItems(["auto", "3", "4", "5", "6", "8", "10"])
        self.sigfigs.setFixedHeight(20)
        top.addWidget(self.sigfigs)
        self.upper_e = QCheckBox("Uppercase E")
        self.upper_e.setFixedHeight(20)
        top.addWidget(self.upper_e)
        top.addStretch(1)
        root.addLayout(top)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.dec_input = QLineEdit()
        self.dec_input.setPlaceholderText("e.g., 12345.678 or 0.00123")
        self.dec_input.setFixedHeight(20)
        form.addRow(QLabel("Decimal"), self.dec_input)

        self.sci_input = QLineEdit()
        self.sci_input.setPlaceholderText("e.g., 1.2345678E+4 or 1.23e-3")
        self.sci_input.setFixedHeight(20)
        form.addRow(QLabel("Scientific"), self.sci_input)

        root.addLayout(form)

        self.dec_input.textEdited.connect(self._from_decimal)
        self.sci_input.textEdited.connect(self._from_scientific)
        self.sigfigs.currentTextChanged.connect(self._reformat_both)
        self.upper_e.toggled.connect(self._reformat_both)

    def _parse_float(self, text: str):
        """Parse float"""
        if not text:
            return None
        t = text.strip().replace("−", "-").replace(",", ".")
        try:
            return float(t)
        except Exception:
            return None

    def _sci_format(self, value: float, sig: str, upper: bool) -> str:
        """Format to scientific"""
        if value == 0.0:
            mant, exp = 0.0, 0
        else:
            import math
            exp = int(math.floor(math.log10(abs(value))))
            mant = value / (10 ** exp)
            if sig != "auto":
                n = int(sig)
                mant = round(mant, max(0, n - 1))
                if mant >= 10:
                    mant /= 10.0
                    exp += 1
        e = "E" if upper else "e"
        return f"{mant:.15g}{e}{exp:+d}"

    def _sigfig_round(self, value: float, sig: str) -> float:
        """Round to significant figures"""
        if sig == "auto" or value == 0.0:
            return value
        import math
        n = int(sig)
        exp = int(math.floor(math.log10(abs(value))))
        factor = 10 ** (exp - n + 1)
        return round(value / factor) * factor

    def _from_decimal(self):
        """Update scientific from decimal"""
        if self._updating:
            return
        self._updating = True
        try:
            v = self._parse_float(self.dec_input.text())
            if v is None:
                self.sci_input.setText("")
            else:
                v2 = self._sigfig_round(v, self.sigfigs.currentText())
                self.sci_input.setText(self._sci_format(v2, self.sigfigs.currentText(), self.upper_e.isChecked()))
        finally:
            self._updating = False

    def _from_scientific(self):
        """Update decimal from scientific"""
        if self._updating:
            return
        self._updating = True
        try:
            v = self._parse_float(self.sci_input.text())
            if v is None:
                self.dec_input.setText("")
            else:
                v2 = self._sigfig_round(v, self.sigfigs.currentText())
                self.dec_input.setText("{:.15g}".format(v2))
        finally:
            self._updating = False

    def _reformat_both(self):
        """Reformat both sides"""
        if self._updating:
            return
        if self.dec_input.hasFocus() or (self.dec_input.text() and not self.sci_input.text()):
            self._from_decimal()
        elif self.sci_input.hasFocus() or self.sci_input.text():
            self._from_scientific()
        else:
            self.dec_input.clear()
            self.sci_input.clear()
