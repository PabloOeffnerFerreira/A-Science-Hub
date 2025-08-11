from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt
from decimal import Decimal, getcontext, ROUND_HALF_UP

class SignificantFiguresWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 160)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Number (e.g. 0.00340, 1.20e3)")
        self.value_input.setFixedHeight(20)
        form.addRow(QLabel("Value"), self.value_input)

        self.sig_figs_input = QComboBox()
        self.sig_figs_input.addItems(["auto"] + [str(i) for i in range(1, 13)])
        self.sig_figs_input.setFixedHeight(20)
        form.addRow(QLabel("Sig figs"), self.sig_figs_input)

        self.count_output = QLineEdit()
        self.count_output.setReadOnly(True)
        self.count_output.setFixedHeight(20)
        form.addRow(QLabel("Count"), self.count_output)

        self.round_output = QLineEdit()
        self.round_output.setReadOnly(True)
        self.round_output.setFixedHeight(20)
        form.addRow(QLabel("Rounded"), self.round_output)

        root.addLayout(form)

        self.value_input.textEdited.connect(self._recompute)
        self.sig_figs_input.currentTextChanged.connect(self._recompute)

    def _count_sigfigs(self, s: str) -> int:
        t = s.strip().replace("+", "")
        if not t:
            return 0
        if "e" in t or "E" in t:
            t = t.split("e")[0].split("E")[0]
        neg = t.startswith("-")
        if neg:
            t = t[1:]
        if t.startswith("."):
            t = "0" + t
        if "." in t:
            left, right = t.split(".", 1)
            left = left.lstrip("0")
            digits = left + right
            digits = digits.lstrip("0")
            return len(digits)
        else:
            t = t.lstrip("0")
            if not t:
                return 0
            t = t.rstrip("0")
            return len(t)

    def _round_sigfigs(self, s: str, n: int) -> str:
        try:
            d = Decimal(s.strip())
        except Exception:
            return ""
        if d == 0:
            return "0"
        getcontext().rounding = ROUND_HALF_UP
        q = f".{n}g"
        out = format(d, q)
        return out

    def _recompute(self):
        s = self.value_input.text()
        if not s.strip():
            self.count_output.clear()
            self.round_output.clear()
            return
        count = self._count_sigfigs(s)
        self.count_output.setText(str(count) if count else "")
        choice = self.sig_figs_input.currentText()
        if choice == "auto":
            n = count if count else 0
        else:
            n = int(choice)
        if n <= 0:
            self.round_output.clear()
            return
        rounded = self._round_sigfigs(s, n)
        self.round_output.setText(rounded)
