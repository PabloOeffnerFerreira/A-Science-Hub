from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QFrame, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from core.data.functions.tool_registry import discover_categories_and_tools

class CategorySidebar(QFrame):
    openTool = pyqtSignal(str, str)

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
