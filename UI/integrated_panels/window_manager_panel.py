from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from tools.panel_tools.wm.window_manager import wm
from core.utils.wm_events import bus

class WindowManagerPanel(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        v.setContentsMargins(8,8,8,8)
        v.setSpacing(8)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID","Title","State"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        v.addWidget(self.table)
        h = QHBoxLayout()
        self.btn_focus = QPushButton("Focus")
        self.btn_min = QPushButton("Minimize")
        self.btn_restore = QPushButton("Restore")
        self.btn_close = QPushButton("Close")
        self.btn_close_all = QPushButton("Close All")
        for b in [self.btn_focus, self.btn_min, self.btn_restore, self.btn_close, self.btn_close_all]:
            h.addWidget(b)
        v.addLayout(h)
        self.btn_focus.clicked.connect(self._focus)
        self.btn_min.clicked.connect(self._min)
        self.btn_restore.clicked.connect(self._restore)
        self.btn_close.clicked.connect(self._close)
        self.btn_close_all.clicked.connect(wm.close_all)
        bus.opened.connect(self._on_opened)
        bus.closed.connect(self._on_closed)
        bus.changed.connect(self._on_changed)
        self._reload()

    def _selected_id(self):
        r = self.table.currentRow()
        if r < 0:
            return None
        return self.table.item(r, 0).text()

    def _reload(self):
        data = wm.list()
        self.table.setRowCount(0)
        for d in data:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(d["id"]))
            self.table.setItem(r, 1, QTableWidgetItem(d["title"]))
            self.table.setItem(r, 2, QTableWidgetItem(d["state"]))

    def _on_opened(self, payload):
        self._reload()

    def _on_closed(self, wid):
        self._reload()

    def _on_changed(self, payload):
        self._reload()

    def _focus(self):
        wid = self._selected_id()
        if wid:
            wm.focus(wid)

    def _min(self):
        wid = self._selected_id()
        if wid:
            wm.minimize(wid)

    def _restore(self):
        wid = self._selected_id()
        if wid:
            wm.restore(wid)

    def _close(self):
        wid = self._selected_id()
        if wid:
            wm.close(wid)
