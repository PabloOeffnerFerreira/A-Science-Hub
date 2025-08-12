from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt

class ToolWindow(QMainWindow):
    def __init__(self, window_id: str, title: str, central):
        super().__init__()
        self._id = window_id
        self.setWindowTitle(title)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setCentralWidget(central)

    def window_id(self):
        return self._id
