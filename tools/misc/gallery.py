from __future__ import annotations

import os, json, re
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QMimeData
from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QTextEdit, QDialogButtonBox,
    QMessageBox, QCheckBox, QInputDialog, QFrame, QToolBar
)

# --- ASH paths (shared, no logging used) ---
from core.data.paths import IMAGES_DIR  # central images folder
# If you prefer a different meta location, tweak this:
_META_FILE = Path(IMAGES_DIR) / "_meta.json"


def _ensure_dirs():
    Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    _META_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not _META_FILE.exists():
        _META_FILE.write_text("{}", encoding="utf-8")


class _Metadata:
    def __init__(self):
        _ensure_dirs()
        try:
            self.meta = json.loads(_META_FILE.read_text(encoding="utf-8"))
        except Exception:
            self.meta = {}

    def save(self):
        _META_FILE.write_text(json.dumps(self.meta, indent=2), encoding="utf-8")

    def get(self, filename: str) -> dict:
        return self.meta.get(filename, {"tags": [], "favorite": False})

    def set_key(self, filename: str, key: str, value):
        self.meta.setdefault(filename, {})[key] = value
        self.save()

    def delete(self, filename: str):
        if filename in self.meta:
            del self.meta[filename]
            self.save()

    def rename(self, old: str, new: str):
        if old in self.meta:
            self.meta[new] = self.meta.pop(old)
            self.save()


class Tool(QDialog):
    TITLE = "Gallery"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(self.TITLE)
        self.resize(1000, 650)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color:#1e1e1e; color:#dddddd;")

        self.meta = _Metadata()

        # Root layout: lightweight "window manager"-like structure:
        # Toolbar on top + main content below (consistent with labs style).
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.toolbar = self._build_toolbar()
        root.addWidget(self.toolbar)

        content = QFrame()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(10, 10, 10, 10)
        root.addWidget(content, 1)

        # Search row
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or tag")
        self.search_input.setStyleSheet("background-color:#2a2a2a; color:#ffffff;")
        self.search_input.textChanged.connect(self.refresh_list)

        self.fav_filter = QCheckBox("Only favorites")
        self.fav_filter.setStyleSheet("color:#cccccc;")
        self.fav_filter.stateChanged.connect(self.refresh_list)

        self.add_btn = QPushButton("Add Image")
        self.add_btn.setStyleSheet("background-color:#444444; color:#ffffff;")
        self.add_btn.clicked.connect(self.import_images)

        search_row.addWidget(self.search_input)
        search_row.addWidget(self.fav_filter)
        search_row.addWidget(self.add_btn)
        content_lay.addLayout(search_row)

        # Drag hint
        self.drop_hint = QLabel("Drop images here")
        self.drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_lay.addWidget(self.drop_hint)

        # List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.view_entry)
        self.list_widget.setIconSize(QSize(128, 128))
        content_lay.addWidget(self.list_widget, 1)

        self.refresh_list()

    # ---------- Toolbar ----------
    def _build_toolbar(self) -> QToolBar:
        tb = QToolBar()
        tb.setMovable(False)

        act_import = QAction("Import", self)
        act_import.triggered.connect(self.import_images)
        tb.addAction(act_import)

        act_refresh = QAction("Refresh", self)
        act_refresh.triggered.connect(self.refresh_list)
        tb.addAction(act_refresh)

        return tb

    # ---------- Core UI actions ----------
    def refresh_list(self):
        self.list_widget.clear()
        query = (self.search_input.text() or "").strip().lower()
        fav_only = self.fav_filter.isChecked()

        for fname in sorted(os.listdir(IMAGES_DIR)):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            info = self.meta.get(fname)
            tags = ", ".join(info.get("tags", []))
            fav = " ★" if info.get("favorite") else ""

            fulltext = f"{fname} {tags}".lower()
            if query and query not in fulltext:
                continue
            if fav_only and not info.get("favorite"):
                continue

            item = QListWidgetItem(f"{fname}{fav}\nTags: {tags}")
            item.setData(Qt.ItemDataRole.UserRole, fname)

            icon_path = os.path.join(IMAGES_DIR, fname)
            pix = QPixmap(icon_path)
            if not pix.isNull():
                item.setIcon(QIcon(pix.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)))
            self.list_widget.addItem(item)

    def import_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select images", "", "Images (*.png *.jpg *.jpeg)")
        if not files:
            return
        for src_path in files:
            base = os.path.basename(src_path)
            dest = os.path.join(IMAGES_DIR, base)
            if not os.path.exists(dest):
                with open(src_path, "rb") as src, open(dest, "wb") as dst:
                    dst.write(src.read())
        self.refresh_list()

    def view_entry(self, item: QListWidgetItem):
        fname = item.data(Qt.ItemDataRole.UserRole)
        full_path = os.path.join(IMAGES_DIR, fname)
        if not os.path.exists(full_path):
            QMessageBox.warning(self, "Missing file", f"{fname} not found.")
            self.refresh_list()
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(fname)
        lay = QVBoxLayout(dlg)

        # Preview
        img = QLabel()
        pix = QPixmap(full_path)
        img.setPixmap(pix.scaled(512, 512, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation))
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(img)

        # Tags editor
        info = self.meta.get(fname)
        lay.addWidget(QLabel("Tags (comma-separated):"))
        tags_box = QTextEdit()
        tags_box.setFixedHeight(60)
        tags_box.setText(", ".join(info.get("tags", [])))
        lay.addWidget(tags_box)

        # Buttons row
        row = QHBoxLayout()
        fav_btn = QPushButton("★ Favorite" if not info.get("favorite") else "★ Unfavorite")
        fav_btn.clicked.connect(lambda: self._toggle_fav(fname, dlg))
        row.addWidget(fav_btn)

        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(lambda: self._rename(fname, dlg))
        row.addWidget(rename_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self._delete(fname, dlg))
        row.addWidget(delete_btn)

        lay.addLayout(row)

        # Save / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(lambda: self._save_tags(fname, tags_box.toPlainText(), dlg))
        buttons.rejected.connect(dlg.reject)
        lay.addWidget(buttons)

        dlg.exec()

    # ---------- Helpers ----------
    def _save_tags(self, fname: str, raw: str, dlg: QDialog):
        tags = [t.strip() for t in raw.split(",") if t.strip()]
        self.meta.set_key(fname, "tags", tags)
        dlg.accept()
        self.refresh_list()

    def _toggle_fav(self, fname: str, dlg: QDialog):
        info = self.meta.get(fname)
        self.meta.set_key(fname, "favorite", not info.get("favorite"))
        dlg.accept()
        self.refresh_list()

    def _rename(self, fname: str, dlg: QDialog):
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new filename:", text=fname)
        if not ok:
            return
        new_name = re.sub(r'[<>:"/\\|?*]', "", (new_name or "").strip())
        if not new_name.lower().endswith((".png", ".jpg", ".jpeg")):
            QMessageBox.warning(self, "Invalid name", "Use .png, .jpg, or .jpeg")
            return
        src = os.path.join(IMAGES_DIR, fname)
        dest = os.path.join(IMAGES_DIR, new_name)
        if os.path.exists(dest):
            QMessageBox.warning(self, "File exists", f"'{new_name}' already exists.")
            return
        os.rename(src, dest)
        self.meta.rename(fname, new_name)
        dlg.accept()
        self.refresh_list()

    def _delete(self, fname: str, dlg: QDialog):
        path = os.path.join(IMAGES_DIR, fname)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete file:\n{e}")
                return
        self.meta.delete(fname)
        dlg.accept()
        self.refresh_list()

    # ---------- Drag & drop ----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background-color:#222222; color:#ffffff;")

    def dropEvent(self, event):
        self.setStyleSheet("background-color:#1e1e1e; color:#dddddd;")
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local.lower().endswith((".png", ".jpg", ".jpeg")):
                base = os.path.basename(local)
                dest = os.path.join(IMAGES_DIR, base)
                if not os.path.exists(dest):
                    with open(local, "rb") as src, open(dest, "wb") as dst:
                        dst.write(src.read())
        self.refresh_list()
