import uuid
from PyQt6.QtCore import QRect
from core.utils.settings_store import load_settings, save_settings
from core.utils.wm_events import bus
from UI.windows.tool_window import ToolWindow
from core.utils.usage_stats import set_last_tool_opened

class WM:
    def __init__(self):
        self.windows = {}
        self.layout_key = "wm_layout"

    def restore_geometry(self, win_id: str, win: ToolWindow):
        s = load_settings()
        g = s.get(self.layout_key, {}).get(win_id)
        if not g:
            return
        r = QRect(g["x"], g["y"], g["w"], g["h"])
        if r.width() > 0 and r.height() > 0:
            win.setGeometry(r)

    def save_geometry(self, win_id: str, win: ToolWindow):
        s = load_settings()
        d = s.get(self.layout_key, {})
        r = win.geometry()
        d[win_id] = {"x": r.x(), "y": r.y(), "w": r.width(), "h": r.height()}
        s[self.layout_key] = d
        save_settings(s)

    def open(self, title: str, widget_factory):
        wid = str(uuid.uuid4())
        w = widget_factory()
        tw = ToolWindow(wid, title, w)
        tw.destroyed.connect(lambda: self._on_closed(wid))
        self.windows[wid] = {"id": wid, "title": title, "win": tw, "state": "normal"}
        self.restore_geometry(wid, tw)
        set_last_tool_opened(title)
        bus.opened.emit({"id": wid, "title": title, "state": "normal"})
        tw.show()
        return wid

    def _on_closed(self, wid: str):
        if wid in self.windows:
            self.save_geometry(wid, self.windows[wid]["win"])
            del self.windows[wid]
            bus.closed.emit(wid)

    def close(self, wid: str):
        if wid in self.windows:
            self.windows[wid]["win"].close()

    def focus(self, wid: str):
        if wid in self.windows:
            w = self.windows[wid]["win"]
            w.raise_()
            w.activateWindow()
            self._emit_changed(wid, "focused")

    def minimize(self, wid: str):
        if wid in self.windows:
            self.windows[wid]["win"].showMinimized()
            self._emit_changed(wid, "minimized")

    def restore(self, wid: str):
        if wid in self.windows:
            w = self.windows[wid]["win"]
            w.showNormal()
            w.raise_()
            w.activateWindow()
            self._emit_changed(wid, "normal")

    def close_all(self):
        for wid in list(self.windows.keys()):
            self.close(wid)

    def list(self):
        return [{"id": k, "title": v["title"], "state": v["state"]} for k, v in self.windows.items()]

    def _emit_changed(self, wid: str, state: str):
        if wid in self.windows:
            self.windows[wid]["state"] = state
            bus.changed.emit({"id": wid, "title": self.windows[wid]["title"], "state": state})

wm = WM()
