from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import Qt

class TitledCard(QFrame):
    def __init__(self, title: str, child: QWidget | None = None):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(8)
        t = QLabel(title)
        t.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        t.setObjectName("CardTitle")
        lay.addWidget(t, 0, Qt.AlignmentFlag.AlignTop)
        if child is not None:
            lay.addWidget(child, 1)
        self.setStyleSheet("""
#Card {
    border: 1px solid rgba(120,120,120,80);
    border-radius: 12px;
}
#CardTitle {
    font-weight: 600;
    padding-bottom: 2px;
}
""")
