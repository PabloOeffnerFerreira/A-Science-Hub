from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import Qt
from UI.integrated_panels.category_sidebar import CategorySidebar
from UI.integrated_panels.log_panel import LogPanel
from UI.integrated_panels.simple_tools_panel import SimpleToolsPanel
from UI.integrated_panels.window_manager_panel import WindowManagerPanel
from tools.panel_tools.wm.window_manager import WM

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._build_dashboard()
        self.setWindowState(Qt.WindowState.WindowMaximized)  # start maximized

    def _build_ui(self):
        w = QWidget()
        self.setCentralWidget(w)
        self.layout = QGridLayout(w)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(8)
        self._floating_windows = []
        
    def _build_dashboard(self):
        self.sidebar = CategorySidebar()
        self.layout.addWidget(self.sidebar, 0, 0, 2, 1)
        self.sidebar.openTool.connect(self._open_tool)

        wm_panel = WindowManagerPanel()
        wm_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        log = LogPanel()
        log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        middle_stack = QWidget()
        middle_layout = QVBoxLayout(middle_stack)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(8)
        middle_layout.addWidget(wm_panel, 3)
        middle_layout.addWidget(log, 2)
        self.layout.addWidget(middle_stack, 0, 1, 2, 1)

        simple_tools = SimpleToolsPanel()
        simple_tools.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(simple_tools, 0, 2, 2, 1)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 3)
        self.layout.setColumnStretch(2, 4)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

    def _open_tool(self, category: str, key: str):
        from core.data.functions.tool_loader import create_tool_factory
        factory, title = create_tool_factory(category, key)

        try:
            from tools.panel_tools.wm.window_manager import WM
        except Exception:
            w = factory()
            w.setWindowTitle(title)
            w.show()
            self._floating_windows.append(w)
            w.destroyed.connect(lambda *_, win=w: self._floating_windows.remove(win))
            return

        try:
            WM.open(widget_factory=factory, title=title)
            return
        except Exception:
            pass
        try:
            WM.open(factory, title)
            return
        except Exception:
            pass

        if hasattr(WM, "open_window"):
            w = factory()
            WM.open_window(w, title)
            self._floating_windows.append(w)
            w.destroyed.connect(lambda *_, win=w: self._floating_windows.remove(win))
            return

        if hasattr(WM, "register_window"):
            w = factory()
            WM.register_window(w, title)
            self._floating_windows.append(w)
            w.destroyed.connect(lambda *_, win=w: self._floating_windows.remove(win))
            return

        w = factory()
        w.setWindowTitle(title)
        w.show()
        self._floating_windows.append(w)
        w.destroyed.connect(lambda *_, win=w: self._floating_windows.remove(win))