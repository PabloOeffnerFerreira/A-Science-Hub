# UI/integrated_panels/calculator_panel.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QSizePolicy, QFormLayout, QMenu, QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from tools.panel_tools.simple_calc import SafeEvaluator


class SimpleCalculatorWidget(QWidget):
    """Simple scientific calculator panel"""
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 260)

        self.eval = SafeEvaluator()
        self._typing_timer = QTimer(self)
        self._typing_timer.setSingleShot(True)
        self._typing_timer.setInterval(120)
        self._typing_timer.timeout.connect(self._compute)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Expression (e.g., 2*sin(pi/4)^2, x=3, ln(10), log(100,10))")
        form.addRow(QLabel("Input"), self.inp)

        self.out = QLineEdit()
        self.out.setReadOnly(True)
        form.addRow(QLabel("Result"), self.out)

        root.addLayout(form)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Variables"))
        top_row.addStretch(1)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._reset_vars)
        top_row.addWidget(self.reset_btn)
        root.addLayout(top_row)

        self.vars_table = QTableWidget(0, 2)
        self.vars_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.vars_table.horizontalHeader().setStretchLastSection(True)
        self.vars_table.setEditTriggers(self.vars_table.EditTrigger.NoEditTriggers)
        self.vars_table.setFixedHeight(120)
        self.vars_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.vars_table.customContextMenuRequested.connect(self._vars_context_menu)
        root.addWidget(self.vars_table)

        self.inp.textChanged.connect(self._on_text)

    def _on_text(self):
        """Debounce input typing"""
        self._typing_timer.start()

    def _compute(self):
        """Evaluate expression and refresh variables"""
        text = self.inp.text().strip()
        if not text:
            self.out.setText("")
            return
        try:
            val = self.eval.evaluate(text)
            self.out.setText("" if val is None else self._fmt(val))
        except NameError as e:
            self.out.setText(str(e))
        except ZeroDivisionError:
            self.out.setText("Division by zero")
        except Exception:
            self.out.setText("")
        self._refresh_vars()

    def _refresh_vars(self):
        """Refresh variables table"""
        items = sorted(self.eval.get_variables().items())
        self.vars_table.setRowCount(len(items))
        for r, (k, v) in enumerate(items):
            self.vars_table.setItem(r, 0, QTableWidgetItem(k))
            self.vars_table.setItem(r, 1, QTableWidgetItem(self._fmt(v)))

    def _fmt(self, v):
        """Format numbers"""
        if isinstance(v, (int, float)):
            return "{:.15g}".format(v)
        return str(v)

    def _vars_context_menu(self, pos: QPoint):
        """Show context menu for variables"""
        idx = self.vars_table.indexAt(pos)
        if not idx.isValid():
            return
        row = idx.row()
        name_item = self.vars_table.item(row, 0)
        val_item = self.vars_table.item(row, 1)
        if not name_item:
            return
        name = name_item.text()
        value = val_item.text() if val_item else ""

        menu = QMenu(self)
        menu.addAction("Edit…", lambda: self._edit_var(name, value))
        menu.addAction("Delete", lambda: self._delete_var(name))
        menu.exec(self.vars_table.viewport().mapToGlobal(pos))

    def _edit_var(self, name: str, current_value: str):
        """Edit variable value"""
        new_text, ok = QInputDialog.getText(self, "Edit Variable", f"{name} =", text=current_value)
        if not ok:
            return
        try:
            new_val = float(new_text.replace(",", ".").strip())
        except Exception:
            QMessageBox.warning(self, "Invalid Value", "Enter a numeric value.")
            return
        self.eval.set_variable(name, new_val)
        self._refresh_vars()

    def _delete_var(self, name: str):
        """Delete variable"""
        self.eval.delete_variable(name)
        self._refresh_vars()

    def _reset_vars(self):
        """Reset all variables"""
        self.eval.reset_variables()
        self._refresh_vars()
