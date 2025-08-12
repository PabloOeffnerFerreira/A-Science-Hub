from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

class DnDPlaceholderPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("DnDPanel")
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        label = QLabel("Drag & Drop Here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; color: rgba(80,80,80,200);")
        layout.addWidget(label)

        self.setStyleSheet("""
#DnDPanel {
    border: 2px dashed rgba(120,120,120,120);
    border-radius: 10px;
}
""")

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        # Placeholder: no logic yet
        event.acceptProposedAction()
