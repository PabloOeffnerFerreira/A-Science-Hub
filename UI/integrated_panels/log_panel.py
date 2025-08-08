import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QMenu, QToolButton, QPushButton
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QGuiApplication
from tools.panel_tools.log import LogController
from core.data.functions.log_signals import log_bus
from core.data.paths import ASSETS_DIR, LOGS_DIR

PIN_ICON_PATH = os.path.join(ASSETS_DIR, "pin.png")
PIN_EMPTY_ICON_PATH = os.path.join(ASSETS_DIR, "pin_empty.png")


class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Top bar ---
        top_bar = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search logs...")
        self.search_bar.textChanged.connect(self.filter_logs)
        top_bar.addWidget(self.search_bar)

        # Pinned filter toggle
        self.show_only_pinned = False
        self.pinned_toggle_btn = QPushButton("Show Only Pinned")
        self.pinned_toggle_btn.setCheckable(True)
        self.pinned_toggle_btn.toggled.connect(self.toggle_pinned_filter)
        top_bar.addWidget(self.pinned_toggle_btn)

        # Dropdown actions
        self.actions_dropdown = QToolButton()
        self.actions_dropdown.setText("Actions")
        self.actions_dropdown.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self)
        menu.addAction("Clear All (Ignore Pinned)", lambda: self.controller.clear_logs(True))
        menu.addAction("Clear All", lambda: self.controller.clear_logs(False))
        menu.addSeparator()
        menu.addAction("Export as CSV", self.export_logs_csv)
        menu.addAction("Export as TXT", self.export_logs_txt)
        self.actions_dropdown.setMenu(menu)
        top_bar.addWidget(self.actions_dropdown)

        main_layout.addLayout(top_bar)

        # --- Table ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["", "Time", "Tool", "Action", "Data", "Tags"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnWidth(0, 30)
        self.table.cellClicked.connect(self.handle_cell_click)

        # Context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        main_layout.addWidget(self.table)

        # Controller
        self.controller = LogController()
        self.controller.logs_updated.connect(self.display_logs)
        self.all_logs = []
        self.filtered_logs = []

        # Load initial logs
        self.controller.load_logs()

        # Listen for global log added event
        log_bus.log_added.connect(self.controller.load_logs)

    def display_logs(self, logs):
        self.all_logs = logs
        self.apply_filters()

    def _populate_table(self, logs):
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            pin_icon = QIcon(PIN_ICON_PATH if log.get("pinned") else PIN_EMPTY_ICON_PATH)
            self.table.setItem(row, 0, QTableWidgetItem(pin_icon, ""))
            self.table.setItem(row, 1, QTableWidgetItem(log["timestamp"]))
            self.table.setItem(row, 2, QTableWidgetItem(log["tool"]))
            self.table.setItem(row, 3, QTableWidgetItem(log["action"]))
            self.table.setItem(row, 4, QTableWidgetItem(str(log["data"])))
            self.table.setItem(row, 5, QTableWidgetItem(", ".join(log["tags"])))

    def handle_cell_click(self, row, col):
        if col == 0:  # Pin icon column
            self.all_logs[row]["pinned"] = not self.all_logs[row].get("pinned", False)
            self.controller.set_pin_state(row, self.all_logs[row]["pinned"])

    def show_context_menu(self, pos: QPoint):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        log = self.filtered_logs[row] if row < len(self.filtered_logs) else None
        if log is None:
            return

        actual_index = self.all_logs.index(log)

        menu = QMenu(self)

        # Pin / Unpin
        if log.get("pinned"):
            menu.addAction("Unpin", lambda: self._after_action(lambda: self.controller.set_pin_state(actual_index, False), row))
        else:
            menu.addAction("Pin", lambda: self._after_action(lambda: self.controller.set_pin_state(actual_index, True), row))

        # Delete
        menu.addAction("Delete", lambda: self._after_action(lambda: self.controller.delete_log(actual_index), row))

        # Copy actions
        menu.addSeparator()
        menu.addAction("Copy Action", lambda: QGuiApplication.clipboard().setText(log["action"]))
        menu.addAction("Copy Data", lambda: QGuiApplication.clipboard().setText(str(log["data"])))

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _after_action(self, func, current_row):
        """Runs an action and reselects a sensible next row."""
        func()
        total_rows = self.table.rowCount()
        if total_rows > 0:
            new_row = min(current_row, total_rows - 1)
            self.table.selectRow(new_row)

    def filter_logs(self, _=None):
        self.apply_filters()

    def toggle_pinned_filter(self, checked):
        self.show_only_pinned = checked
        self.pinned_toggle_btn.setText("Show All" if checked else "Show Only Pinned")
        self.apply_filters()

    def apply_filters(self):
        text = self.search_bar.text().strip().lower()
        self.filtered_logs = []
        for log in self.all_logs:
            if self.show_only_pinned and not log.get("pinned"):
                continue
            if text:
                if not (
                    text in log["timestamp"].lower()
                    or text in log["tool"].lower()
                    or text in log["action"].lower()
                    or text in str(log["data"]).lower()
                    or any(text in tag.lower() for tag in log["tags"])
                ):
                    continue
            self.filtered_logs.append(log)
        self._populate_table(self.filtered_logs)

    def export_logs_csv(self):
        path = os.path.join(LOGS_DIR, "logs_export.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Tool", "Action", "Data", "Tags", "Pinned"])
            for log in self.filtered_logs:
                writer.writerow([
                    log["timestamp"], log["tool"], log["action"],
                    log["data"], ", ".join(log["tags"]), log["pinned"]
                ])

    def export_logs_txt(self):
        path = os.path.join(LOGS_DIR, "logs_export.txt")
        with open(path, "w", encoding="utf-8") as f:
            for log in self.filtered_logs:
                f.write(f"[{log['timestamp']}] {log['tool']} - {log['action']} | {log['data']} | Tags: {', '.join(log['tags'])} | Pinned: {log['pinned']}\n")
