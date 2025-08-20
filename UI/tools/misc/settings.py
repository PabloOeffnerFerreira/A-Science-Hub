from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from core.data.functions.settings_io import load_settings, save_settings

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("SettingsTool")
        self._data = load_settings()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.region_label = QLabel("Region")
        self.region_select = QComboBox()
        self.region_select.addItems(["EU", "UK", "US", "BR"])
        self.region_select.setCurrentText(str(self._data.get("region", "EU")))
        self.region_select.currentTextChanged.connect(self._on_region_changed)

        self.mode_label = QLabel("Quantity Selector Mode")
        self.mode_select = QComboBox()
        self.mode_select.addItems(["quantity", "q_symbol", "u_symbol"])
        self.mode_select.setCurrentText(str(self._data.get("quantity_mode", "quantity")))
        self.mode_select.currentTextChanged.connect(self._on_mode_changed)

        layout.addWidget(self.region_label)
        layout.addWidget(self.region_select)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_select)
        layout.addStretch(1)

        self.setStyleSheet("""
#SettingsTool {
    background-color: #121214;
}
QLabel {
    color: #e6e6e9;
}
QComboBox {
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

    def _on_region_changed(self, value: str):
        self._data["region"] = value
        save_settings(self._data)

    def _on_mode_changed(self, value: str):
        self._data["quantity_mode"] = value
        save_settings(self._data)
