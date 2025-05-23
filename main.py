import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QListWidget, QGridLayout
)
from utils import (
    LastUsedPanel, FavoritesPanel, WindowManagerPanel, CalculatorPanel)
class ScienceHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A Science Hub")
        self.setObjectName("main_science_hub")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow { background: #23272E; }
            QLabel, QListWidget, QPushButton {
                color: #EEE;
                font-size: 14px;
            }
            QPushButton {
                background: #444; 
                border-radius: 8px;
                padding: 10px 18px;
                margin: 4px 0;
            }
            QPushButton:hover {
                background: #333;
            }
            QListWidget {
                background: #1A1A1A;
                border: none;
                min-width: 160px;
        """)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Sidebar (unchanged)
        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("Categories"))
        self.category_list = QListWidget()
        self.category_list.addItems([
    "Chemistry", "Biology", "Physics", "Geology", "Math",
    "Placeholder 1", "Placeholder 2", "Placeholder 3", "Placeholder 4", "Placeholder 5",
    "Placeholder 6", "Placeholder 7", "Placeholder 8", "Placeholder 9", "Placeholder 10"
])

        sidebar.addWidget(self.category_list)

        self.launch_btn = QPushButton("Launch Toolkit")
        self.launch_btn.setEnabled(False)
        sidebar.addWidget(self.launch_btn)

        self.category_list.itemSelectionChanged.connect(self.update_launch_btn_state)
        self.launch_btn.clicked.connect(self.launch_toolkit)
        sidebar.addStretch()

        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFixedWidth(200)
   
        central_panel_layout = QGridLayout()

        headline = QLabel("Welcome to Science Hub")
        headline.setStyleSheet("font-size: 28px; font-weight: bold;")
        central_panel_layout.addWidget(headline, 0, 0, 1, 2)

        self.calculator_panel = CalculatorPanel()
        self.last_used_panel = LastUsedPanel()
        self.favorites_panel = FavoritesPanel()
        self.window_manager_panel = WindowManagerPanel()
        central_panel_layout.addWidget(self.last_used_panel,      1, 0)
        central_panel_layout.addWidget(self.favorites_panel,      1, 1)
        central_panel_layout.addWidget(self.window_manager_panel, 2, 0)
        central_panel_layout.addWidget(self.calculator_panel,     2, 1)

        credits = QLabel("Science Hub by Pablo Oeffner Ferreira")
        credits.setStyleSheet("color: #bbb; font-size: 12px; margin-top: 40px;")
        central_panel_layout.addWidget(credits, 3, 0, 1, 2)


        central_panel_frame = QFrame()
        central_panel_frame.setLayout(central_panel_layout)
        central_panel_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(central_panel_frame)
    def update_launch_btn_state(self):
        selected_items = self.category_list.selectedItems()
        self.launch_btn.setEnabled(len(selected_items) > 0)
    def launch_toolkit(self):
        selected_items = self.category_list.selectedItems()
        if selected_items:
            selected_category = selected_items[0].text()
            print(f"Launching toolkit for {selected_category}...")

def main():
    app = QApplication(sys.argv)
    win = ScienceHub()
    win.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()