from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QGuiApplication

class VarChip(QFrame):
    removeRequested = pyqtSignal(str)

    def __init__(self, name: str, value):
        super().__init__()
        self._name = name
        self._value = value
        self.setObjectName("VarChip")
        l = QHBoxLayout(self)
        l.setContentsMargins(8,4,6,4)
        l.setSpacing(6)
        self.lbl = QLabel(f"{name} = {self._fmt(value)}")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        btnCopy = QPushButton("Copy")
        btnDel = QPushButton("×")
        btnCopy.clicked.connect(self._copy)
        btnDel.clicked.connect(self._remove)
        l.addWidget(self.lbl, 1)
        l.addWidget(btnCopy, 0)
        l.addWidget(btnDel, 0)
        self.setStyleSheet("""
#VarChip {
    border: 1px solid #2a2a2f;
    border-radius: 10px;
    background-color: #1a1a1f;
    color: #e6e6e9;
}
QPushButton {
    padding: 2px 8px;
    border: 1px solid #2d2d35;
    border-radius: 8px;
    background-color: #222228;
    color: #e6e6e9;
}
QPushButton:hover { background-color: #2a2a31; }
""")

    def _fmt(self, v):
        try:
            return f"{float(v):.12g}"
        except Exception:
            return str(v)

    def _copy(self):
        QGuiApplication.clipboard().setText(str(self._value))

    def _remove(self):
        self.removeRequested.emit(self._name)
