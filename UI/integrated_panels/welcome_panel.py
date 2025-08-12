from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QFrame, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
from tools.panel_tools.welcome import get_welcome_stats
from core.data.info import APP_NAME

class StatChip(QFrame):
    def __init__(self, k: str, v):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("Chip")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 10)
        lay.setSpacing(2)
        a = QLabel(k)
        a.setObjectName("ChipKey")
        b = QLabel(str(v))
        b.setObjectName("ChipVal")
        lay.addWidget(a)
        lay.addWidget(b)
        self.setStyleSheet("""
#Chip { border: 1px solid rgba(120,120,120,80); border-radius: 10px; }
#ChipKey { font-size: 11px; color: rgba(120,120,120,200); }
#ChipVal { font-size: 14px; font-weight: 600; }
""")

class WelcomePanel(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(8)

        # Welcome sentence
        welcome_label = QLabel(f"Welcome to {APP_NAME} — your science hub for exploration and discovery.")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        welcome_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        outer.addWidget(welcome_label)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("color: rgba(120,120,120,100);")
        outer.addWidget(divider)

        # Scrollable stats
        area = QScrollArea()
        area.setWidgetResizable(True)
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)
        area.setWidget(self.container)
        outer.addWidget(area)

        # Timer for auto-refresh
        self.timer = QTimer(self)
        self.timer.setInterval(1500)
        self.timer.timeout.connect(self._reload)
        self.timer.start()
        self._reload()

    def _reload(self):
        stats = get_welcome_stats()
        while self.grid.count():
            it = self.grid.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
        row = 0
        for section, kv in stats.items():
            s = QLabel(section)
            s.setStyleSheet("font-weight: 700;")
            self.grid.addWidget(s, row, 0, 1, 4)
            row += 1
            col = 0
            for k, v in kv.items():
                chip = StatChip(k, v)
                self.grid.addWidget(chip, row, col, 1, 1)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
            if col != 0:
                row += 1
