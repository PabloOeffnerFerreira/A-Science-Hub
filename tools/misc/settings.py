from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from tools.panel_tools.wm.window_manager import WM
from core.data.functions.log import log_event

class Settings(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings tool loaded"))

        # Example: Register with Window Manager
        WM.register_window(self, "Settings")

        # Example: Log opening
        log_event("Settings", "Tool opened")

    # Example action
    def run_example(self):
        log_event("Settings", "Example action executed")
