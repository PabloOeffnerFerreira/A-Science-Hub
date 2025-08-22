from PyQt6.QtWidgets import QApplication
import sys
from core.utils.session_state import initialize_session
import PyQt6.QtWebEngineWidgets

initialize_session()

# Import the main window
from UI.main_window import MainWindow
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()