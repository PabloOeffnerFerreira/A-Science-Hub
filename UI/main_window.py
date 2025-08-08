from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from UI.ui_config import APP_TITLE
from UI.integrated_panels.log_panel import LogPanel
from UI.integrated_panels.simple_tools_panel import SimpleToolsPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.is_fullscreen = False

        # Root widget
        central = QWidget()
        self.setCentralWidget(central)
        self.layout: QGridLayout = QGridLayout(central)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setHorizontalSpacing(8)
        self.layout.setVerticalSpacing(8)

        self._build_dashboard()

    def showEvent(self, event):
        super().showEvent(event)
        if not self.is_fullscreen:
            self.showMaximized()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            if self.is_fullscreen:
                self.showNormal()
                self.showMaximized()
                self.is_fullscreen = False
            else:
                self.showFullScreen()
                self.is_fullscreen = True
        else:
            super().keyPressEvent(event)

    def _build_dashboard(self):
        grid = self.layout

        # Left column: Sidebar
        sidebar = QLabel("Category Sidebar")  # TODO: replace with CategorySidebarPanel()
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sidebar.setMaximumWidth(260)
        grid.addWidget(sidebar, 0, 0, 2, 1)

        # Middle column: Window Manager (top) + Log Viewer (bottom)
        wm = QLabel("Window Manager")  # TODO: replace with WindowManagerPanel()
        wm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        log = LogPanel()
        log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        middle_stack = QWidget()
        middle_layout = QVBoxLayout(middle_stack)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(8)
        middle_layout.addWidget(wm, 3)   # bigger
        middle_layout.addWidget(log, 2)  # slightly smaller
        grid.addWidget(middle_stack, 0, 1, 2, 1)

        # Right column: Simple Tools Panel
        simple_tools = SimpleToolsPanel()
        grid.addWidget(simple_tools, 0, 2, 2, 1)
        simple_tools.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        grid.addWidget(simple_tools, 0, 2, 2, 1)

        # Proportions
        grid.setColumnStretch(0, 1)  # sidebar
        grid.setColumnStretch(1, 3)  # middle stack
        grid.setColumnStretch(2, 4)  # simple tools
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
