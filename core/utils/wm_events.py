from PyQt6.QtCore import QObject, pyqtSignal

class WMEvents(QObject):
    opened = pyqtSignal(dict)
    closed = pyqtSignal(str)
    changed = pyqtSignal(dict)

bus = WMEvents()
