from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QListWidget

class CalculatorPanel(QWidget): 
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter expression:"))
        self.expr = QLineEdit()
        layout.addWidget(self.expr)
        self.result = QLabel()
        layout.addWidget(self.result)
        btn = QPushButton("Calculate")
        btn.clicked.connect(self.compute)
        layout.addWidget(btn)

    def compute(self):
        try:
            res = eval(self.expr.text())
            self.result.setText(f"Result: {res}")
        except:
            self.result.setText("Invalid expression.")

class LastUsedPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #2C2F33; border-radius: 12px; padding: 16px;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Last Used Tool"))
        self.msg_label = QLabel("No usage data (demo).")
        self.msg_label.setWordWrap(True)
        layout.addWidget(self.msg_label)

class WindowManagerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #2C2F33; border-radius: 12px; padding: 16px;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Window Manager"))
        self.list_widget = QListWidget()
        self.list_widget.addItems([
            "Window 1 (demo)",
            "Window 2 (demo)",
            "Window 3 (demo)",
        ])
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        btn_row.addWidget(QPushButton("Focus"))
        btn_row.addWidget(QPushButton("Close"))
        btn_row.addWidget(QPushButton("Refresh"))
        layout.addLayout(btn_row)

class FavoritesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #2C2F33; border-radius: 12px; padding: 16px;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Favorites"))
        fav_list = QListWidget()
        fav_list.addItems([
            "Favorite 1 (demo)",
            "Favorite 2 (demo)",
            "Favorite 3 (demo)",
        ])
        layout.addWidget(fav_list)
