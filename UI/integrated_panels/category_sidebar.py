from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QFrame, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from core.data.functions.tool_registry import discover_categories_and_tools
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer
import os, shutil
from core.data.paths import IMAGES_DIR
class CategorySidebar(QFrame):
    openTool = pyqtSignal(str, str)

    imagesImported = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("CategorySidebar")
        self.setFixedWidth(240)

        self.categories, self.category_tools = discover_categories_and_tools()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("CatScroll")
        c = QWidget()
        self.cat_layout = QVBoxLayout(c)
        self.cat_layout.setContentsMargins(8, 8, 8, 8)
        self.cat_layout.setSpacing(6)

        self.category_buttons = []
        self._current_category = None
        for cat in self.categories:
            b = QPushButton(cat)
            b.setObjectName("CategoryButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setCheckable(True)
            b.clicked.connect(lambda checked, x=cat: self._on_category_clicked(x))
            self.cat_layout.addWidget(b)
            self.category_buttons.append(b)

        self.cat_layout.addStretch(1)
        scroll.setWidget(c)
        outer.addWidget(scroll)

        # NEW: dropzone above the tool dropdown
        self.drop_target = DropTarget(self)
        outer.addWidget(self.drop_target)

        self.tool_dropdown = QComboBox()
        self.tool_dropdown.setObjectName("ToolDropdown")
        self.tool_dropdown.activated.connect(self._on_tool_selected)
        outer.addWidget(self.tool_dropdown)

        self.setStyleSheet("""
#CategorySidebar {
    background-color: #121214;
    border-right: 1px solid #2a2a2f;
}
#CatScroll {
    border: none;
    background: transparent;
}
#CatScroll QScrollBar:vertical {
    background: #16161a;
    width: 10px;
    margin: 0;
}
#CatScroll QScrollBar::handle:vertical {
    background: #2e2e36;
    min-height: 24px;
    border-radius: 4px;
}
#CatScroll QScrollBar::handle:vertical:hover {
    background: #3a3a44;
}
#CatScroll QScrollBar::add-line:vertical, 
#CatScroll QScrollBar::sub-line:vertical {
    height: 0;
}
#CategoryButton {
    text-align: left;
    padding: 10px 12px;
    color: #e6e6e9;
    background-color: #1a1a1f;
    border: 1px solid #24242a;
    border-radius: 8px;
}
#CategoryButton:hover {
    background-color: #1f1f25;
    border-color: #2d2d35;
}
#CategoryButton:checked {
    background-color: #3b3b8c;
    border-color: #45459a;
    color: #ffffff;
}
#ToolDropdown {
    margin: 0 8px 8px 8px;
    padding: 6px 8px;
    border: 1px solid #2d2d35;
    border-radius: 8px;
    background-color: #1a1a1f;
    color: #e6e6e9;
}
QComboBox QAbstractItemView {
    background-color: #1a1a1f;
    color: #e6e6e9;
    selection-background-color: #3b3b8c;
    selection-color: #ffffff;
    border: 1px solid #2d2d35;
}
#GalleryDropTarget {
    /* base style set in _reset_style; keeping here for theme cohesion if needed */
}
#GalleryDropTarget:hover {
    background-color: #1c1c21;
}
""")

    def _on_category_clicked(self, category):
        self._current_category = category
        for btn in self.category_buttons:
            btn.setChecked(btn.text() == category)
        self.tool_dropdown.clear()
        for item in self.category_tools.get(category, []):
            self.tool_dropdown.addItem(item["label"], item["key"])

    def _on_tool_selected(self, index):
        key = self.tool_dropdown.itemData(index)
        if self._current_category and key:
            self.openTool.emit(self._current_category, key)

# ADD this helper widget inside the same file (above or below CategorySidebar)
class DropTarget(QFrame):
    def __init__(self, parent_sidebar: "CategorySidebar"):
        super().__init__(parent_sidebar)
        self._sidebar = parent_sidebar
        self.setAcceptDrops(True)
        self.setObjectName("GalleryDropTarget")
        self._label = QLabel("Drop images here → Gallery")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.addWidget(self._label)
        self._reset_style()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._reset_label)

    def _reset_style(self):
        self.setStyleSheet("#GalleryDropTarget { border: 1px dashed #2d2d35; border-radius: 8px; background: #18181c; color: #e6e6e9; }")

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            # accept only image files
            for u in e.mimeData().urls():
                f = u.toLocalFile().lower()
                if f.endswith((".png", ".jpg", ".jpeg")):
                    e.acceptProposedAction()
                    self.setStyleSheet("#GalleryDropTarget { border: 1px dashed #3b3b8c; border-radius: 8px; background: #1d1d22; color: #ffffff; }")
                    return
        e.ignore()

    def dragLeaveEvent(self, e):
        self._reset_style()

    def dropEvent(self, e):
        self._reset_style()
        count = 0
        added = []
        for u in e.mimeData().urls():
            src = u.toLocalFile()
            if not src.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            base = os.path.basename(src)
            dest = os.path.join(IMAGES_DIR, base)
            # avoid overwrite
            if not os.path.exists(dest):
                try:
                    shutil.copyfile(src, dest)
                    count += 1
                    added.append(dest)
                except Exception:
                    pass  # silent fail (no popups)
        if count:
            self._label.setText(f"Imported {count} image(s) ✓")
            self._timer.start(1400)
            # optional: let others hook into this
            self._sidebar.imagesImported.emit(added)

    def _reset_label(self):
        self._label.setText("Drop images here → Gallery")
