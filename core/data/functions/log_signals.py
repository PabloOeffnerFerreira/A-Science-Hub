from PyQt6.QtCore import QObject, pyqtSignal

class LogSignalBus(QObject):
    log_added = pyqtSignal()

# Global instance — import this anywhere to connect/emit
log_bus = LogSignalBus()