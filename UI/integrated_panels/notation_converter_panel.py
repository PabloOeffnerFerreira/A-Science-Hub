from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox
from PyQt6.QtCore import Qt
from tools.panel_tools.notation_converter import convert

class NotationConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(6,6,6,6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.input_dec = QLineEdit()
        self.input_dec.setPlaceholderText("e.g., 12345.678 or 0.00123")
        form.addRow(QLabel("Decimal"), self.input_dec)

        self.input_sci = QLineEdit()
        self.input_sci.setPlaceholderText("e.g., 1.2345678e+4 or 1.23e-3")
        form.addRow(QLabel("Scientific"), self.input_sci)

        self.digits = QComboBox()
        self.digits.addItems(["auto"] + [str(i) for i in range(1, 16)])
        form.addRow(QLabel("Sig digits"), self.digits)

        self.output_dec = QLineEdit(); self.output_dec.setReadOnly(True)
        form.addRow(QLabel("→ Decimal"), self.output_dec)

        self.output_sci = QLineEdit(); self.output_sci.setReadOnly(True)
        form.addRow(QLabel("→ Scientific"), self.output_sci)

        root.addLayout(form)

        self.input_dec.textEdited.connect(self._from_dec)
        self.input_sci.textEdited.connect(self._from_sci)
        self.digits.currentTextChanged.connect(self._refresh_from_active)

        self._active = "dec"

    def _digits(self):
        t = self.digits.currentText()
        return None if t == "auto" else int(t)

    def _from_dec(self):
        self._active = "dec"
        dec, sci = convert(self.input_dec.text(), self._digits())
        self.output_dec.setText("" if dec is None else dec)
        self.output_sci.setText("" if sci is None else sci)

    def _from_sci(self):
        self._active = "sci"
        dec, sci = convert(self.input_sci.text(), self._digits())
        self.output_dec.setText("" if dec is None else dec)
        self.output_sci.setText("" if sci is None else sci)

    def _refresh_from_active(self):
        if self._active == "dec":
            self._from_dec()
        else:
            self._from_sci()
