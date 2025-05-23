from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QGroupBox
)
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A Science Hub")
        self.setGeometry(100, 100, 300, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.settopbar = QHBoxLayout()
        self.layout.addLayout(self.settopbar)

        self.body_layout = QHBoxLayout()
        self.layout.addLayout(self.body_layout)

        self.box1_layout = QVBoxLayout()
        self.box1_widget = QWidget()
        self.box1_widget.setLayout(self.box1_layout)
        self.body_layout.addWidget(self.box1_widget)

        nav_group = QGroupBox("Navigation")
        nav_group.setFixedSize(300, 200)
        nav_group.setLayout(QVBoxLayout())
        nav_group.layout().addWidget(QLabel("Tool list here"))
        self.box1_layout.addWidget(nav_group)

        self.box2_layout = QVBoxLayout()
        self.box2_widget = QWidget()
        self.box2_widget.setLayout(self.box2_layout)
        self.body_layout.addWidget(self.box2_widget)

        wm_group = QGroupBox("Window Manager")
        wm_group.setFixedSize(300, 200)
        wm_group.setLayout(QVBoxLayout())
        wm_group.layout().addWidget(QLabel("Open windows here"))
        self.box2_layout.addWidget(wm_group)

        pm_group = QGroupBox("Profile Manager")
        pm_group.setFixedSize(300, 200)
        self.box2_layout.addWidget(pm_group)
        
        self.box3_layout = QVBoxLayout()
        self.box3_widget = QWidget()
        self.box3_widget.setLayout(self.box3_layout)
        self.body_layout.addWidget(self.box3_widget)

        calc_box = QGroupBox("Calculator")
        calc_box.setFixedSize(300, 200)
        calc_layout = QVBoxLayout()
        calc_layout.addWidget(CalcWidget())
        calc_box.setLayout(calc_layout)
        self.box3_layout.addWidget(calc_box)

        lu_group = QGroupBox("Last Used Tool")
        lu_group.setFixedSize(300, 100)
        self.box3_layout.addWidget(pm_group)

        vft_group = QGroupBox("View Favourite Tools")
        vft_group.setFixedSize(300, 200)
        self.box3_layout.addWidget(vft_group)

        vf_group = QGroupBox("View Favourites")
        vf_group.setFixedSize(300, 200)
        self.box3_layout.addWidget(vf_group)

        self.box4_layout = QVBoxLayout()
        self.box4_widget = QWidget()
        self.box4_widget.setLayout(self.box4_layout)
        self.body_layout.addWidget(self.box4_widget)

        log_group = QGroupBox("Log Output")
        log_group.setFixedSize(300, 200)
        log_group.setLayout(QVBoxLayout())
        log_group.layout().addWidget(QLabel("Logs go here"))
        self.box4_layout.addWidget(log_group)

class CalcWidget(QWidget): 
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
