from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QDoubleValidator, QRegularExpressionValidator

class DecimalTimeConverterWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._updating = False
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.dec_input = QLineEdit()
        self.dec_input.setPlaceholderText("Decimal hours")
        dv = QDoubleValidator(0.0, 1e9, 6)
        dv.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.dec_input.setValidator(dv)
        self.dec_input.setFixedHeight(20)
        form.addRow(QLabel("Decimal Time"), self.dec_input)

        self.hms_input = QLineEdit()
        self.hms_input.setPlaceholderText("HH:MM(:SS)") 
        rx = QRegularExpression(r"^\d{1,6}:\d{2}(:\d{2})?$")
        self.hms_input.setValidator(QRegularExpressionValidator(rx))
        self.hms_input.setFixedHeight(20)
        form.addRow(QLabel("HH:MM:SS"), self.hms_input)

        root.addLayout(form)

        self.dec_input.textEdited.connect(self._on_decimal_edited)
        self.hms_input.textEdited.connect(self._on_hms_edited)

    def _on_decimal_edited(self, text: str):
        if self._updating:
            return
        if not text:
            self._set_hms("")
            return
        try:
            dec_hours = float(text)
            if dec_hours < 0:
                self._set_hms("")
                return
        except ValueError:
            self._set_hms("")
            return
        total_seconds = int(round(dec_hours * 3600))
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        self._set_hms(f"{h:02}:{m:02}:{s:02}")

    def _on_hms_edited(self, text: str):
        if self._updating:
            return
        if not text:
            self._set_dec("")
            return
        parts = text.split(":")
        if len(parts) == 2:
            h, m = parts
            s = "00"
        elif len(parts) == 3:
            h, m, s = parts
        else:
            self._set_dec("")
            return
        try:
            h = int(h)
            m = int(m)
            s = int(s)
            if h < 0 or not (0 <= m < 60) or not (0 <= s < 60):
                self._set_dec("")
                return
        except ValueError:
            self._set_dec("")
            return
        total_seconds = h * 3600 + m * 60 + s
        dec = total_seconds / 3600.0
        self._set_dec(f"{dec:.6f}".rstrip("0").rstrip(".") if "." in f"{dec:.6f}" else f"{dec:.6f}")

    def _set_hms(self, value: str):
        self._updating = True
        try:
            self.hms_input.blockSignals(True)
            self.hms_input.setText(value)
        finally:
            self.hms_input.blockSignals(False)
            self._updating = False

    def _set_dec(self, value: str):
        self._updating = True
        try:
            self.dec_input.blockSignals(True)
            self.dec_input.setText(value)
        finally:
            self.dec_input.blockSignals(False)
            self._updating = False
