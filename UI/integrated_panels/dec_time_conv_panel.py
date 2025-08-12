from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from tools.panel_tools.decimal_time_converter import to_decimal, from_decimal

class DecimalTimeConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(6,6,6,6)
        root.setSpacing(6)

        form1 = QFormLayout()
        form1.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form1.setHorizontalSpacing(6)
        form1.setVerticalSpacing(2)

        self.h_in = QLineEdit(); self.h_in.setPlaceholderText("Hours")
        self.m_in = QLineEdit(); self.m_in.setPlaceholderText("Minutes")
        self.s_in = QLineEdit(); self.s_in.setPlaceholderText("Seconds")
        form1.addRow(QLabel("H:M:S"), self._row(self.h_in, self.m_in, self.s_in))

        self.dec_out = QLineEdit(); self.dec_out.setReadOnly(True)
        form1.addRow(QLabel("→ Decimal hours"), self.dec_out)

        root.addLayout(form1)

        form2 = QFormLayout()
        form2.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form2.setHorizontalSpacing(6)
        form2.setVerticalSpacing(2)

        self.dec_in = QLineEdit(); self.dec_in.setPlaceholderText("Decimal hours")
        form2.addRow(QLabel("Decimal"), self.dec_in)

        self.h_out = QLineEdit(); self.h_out.setReadOnly(True)
        self.m_out = QLineEdit(); self.m_out.setReadOnly(True)
        self.s_out = QLineEdit(); self.s_out.setReadOnly(True)
        form2.addRow(QLabel("→ H:M:S"), self._row(self.h_out, self.m_out, self.s_out))

        root.addLayout(form2)

        self.h_in.textEdited.connect(self._recompute_dec)
        self.m_in.textEdited.connect(self._recompute_dec)
        self.s_in.textEdited.connect(self._recompute_dec)
        self.dec_in.textEdited.connect(self._recompute_hms)

    def _row(self, a, b, c):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(6)
        l.addWidget(a); l.addWidget(b); l.addWidget(c)
        return w

    def _recompute_dec(self):
        r = to_decimal(self.h_in.text(), self.m_in.text(), self.s_in.text())
        self.dec_out.setText("" if r is None else r)

    def _recompute_hms(self):
        r = from_decimal(self.dec_in.text())
        if r is None:
            self.h_out.clear(); self.m_out.clear(); self.s_out.clear(); return
        h, m, s = r
        self.h_out.setText(h); self.m_out.setText(m); self.s_out.setText(s)
