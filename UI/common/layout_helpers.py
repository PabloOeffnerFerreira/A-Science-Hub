from PyQt6.QtCore import QTimer

def cap_to_sizehint(widget, scale=1.0, extra=0):
    def _apply():
        h = widget.sizeHint().height()
        widget.setMaximumHeight(int(h * scale) + int(extra))
    QTimer.singleShot(0, _apply)
