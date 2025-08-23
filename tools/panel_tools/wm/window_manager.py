import os, json, uuid
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget
from core.data.paths import SETTINGS_PATH, WM_FILE
from core.utils.wm_events import bus


def _load_settings():
    try:
        with open(WM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_settings(settings):
    os.makedirs(WM_FILE.parent, exist_ok=True)
    with open(WM_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


# Minimal bug-fix helper: guard against RuntimeError when bus (QObject) is gone
def _safe_emit(signal_emit, payload):
    try:
        signal_emit(payload)
    except RuntimeError:
        # Happens during app shutdown when the underlying QObject is already deleted
        pass
    except Exception:
        # Never let WM crash on signal emission
        pass


class WM:
    def __init__(self):
        self.windows = {}
        self.layout_key = "wm_layout"

    def _restore_geometry(self, win_id: str, win: QWidget):
        s = _load_settings()
        g = s.get(self.layout_key, {}).get(win_id)
        if not g:
            return
        r = QRect(g["x"], g["y"], g["w"], g["h"])
        if r.width() > 0 and r.height() > 0:
            win.setGeometry(r)

    def _save_geometry(self, win_id: str, win: QWidget):
        s = _load_settings()
        d = s.get(self.layout_key, {})
        r = win.geometry()
        d[win_id] = {"x": r.x(), "y": r.y(), "w": r.width(), "h": r.height()}
        s[self.layout_key] = d
        _save_settings(s)

    def open(self, title: str, widget_factory):
        wid = str(uuid.uuid4())
        w = widget_factory()
        w.setWindowTitle(title)

        # Save geometry BEFORE destruction by wrapping closeEvent
        orig_close = getattr(w, "closeEvent", None)

        def _wm_close_event(ev, _wid=wid, _win=w, _orig=orig_close):
            try:
                self._save_geometry(_wid, _win)
            except Exception:
                pass
            if _orig is not None:
                _orig(ev)
            else:
                ev.accept()

        w.closeEvent = _wm_close_event  # type: ignore[attr-defined]

        try:
            # destroyed/finished now only used for cleanup (no geometry calls there)
            w.destroyed.connect(lambda *_: self._on_closed(wid))
            if hasattr(w, "finished"):
                w.finished.connect(lambda *_: self._on_closed(wid))
        except Exception:
            pass

        self.windows[wid] = {"id": wid, "title": title, "win": w, "state": "normal"}
        self._restore_geometry(wid, w)
        w.show()
        _safe_emit(bus.opened.emit, {"id": wid, "title": title, "state": "normal"})  # previously: bus.opened.emit(...)
        return wid

    def adopt(self, title: str, win: QWidget):
        wid = str(uuid.uuid4())
        win.setWindowTitle(title)

        # Save geometry BEFORE destruction by wrapping closeEvent
        orig_close = getattr(win, "closeEvent", None)

        def _wm_close_event(ev, _wid=wid, _win=win, _orig=orig_close):
            try:
                self._save_geometry(_wid, _win)
            except Exception:
                pass
            if _orig is not None:
                _orig(ev)
            else:
                ev.accept()

        win.closeEvent = _wm_close_event  # type: ignore[attr-defined]

        try:
            # destroyed/finished now only used for cleanup (no geometry calls there)
            win.destroyed.connect(lambda *_: self._on_closed(wid))
            if hasattr(win, "finished"):
                win.finished.connect(lambda *_: self._on_closed(wid))
        except Exception:
            pass

        self.windows[wid] = {"id": wid, "title": title, "win": win, "state": "normal"}
        self._restore_geometry(wid, win)
        _safe_emit(bus.opened.emit, {"id": wid, "title": title, "state": "normal"})  # previously: bus.opened.emit(...)
        return wid

    def _on_closed(self, wid: str):
        info = self.windows.get(wid)
        if not info:
            return
        self.windows.pop(wid, None)
        _safe_emit(bus.closed.emit, wid)  # previously: bus.closed.emit(wid)

    def close(self, wid: str):
        if wid in self.windows:
            self.windows[wid]["win"].close()

    def close_all(self):
        for wid in list(self.windows.keys()):
            self.close(wid)

    def focus(self, wid: str):
        if wid in self.windows:
            w = self.windows[wid]["win"]
            w.raise_()
            w.activateWindow()
            self.windows[wid]["state"] = "focused"
            _safe_emit(bus.changed.emit, {"id": wid, "state": "focused"})  # previously: bus.changed.emit(...)

    def minimize(self, wid: str):
        if wid in self.windows:
            w = self.windows[wid]["win"]
            try:
                w.showMinimized()
            except Exception:
                pass
            self.windows[wid]["state"] = "minimized"
            _safe_emit(bus.changed.emit, {"id": wid, "state": "minimized"})  # previously: bus.changed.emit(...)

    def restore(self, wid: str):
        if wid in self.windows:
            w = self.windows[wid]["win"]
            try:
                w.showNormal()
                w.raise_()
                w.activateWindow()
            except Exception:
                pass
            self.windows[wid]["state"] = "normal"
            _safe_emit(bus.changed.emit, {"id": wid, "state": "normal"})  # previously: bus.changed.emit(...)

    def list(self):
        return [{"id": k, "title": v["title"], "state": v["state"]}
                for k, v in self.windows.items()]

    def list_windows(self):
        return self.list()


wm = WM()
