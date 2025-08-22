
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from core.data.functions.log import add_log_entry
from core.data.functions.chemistry_utils import balance_reaction, format_balanced

class Tool(QDialog):
    TITLE = "Reaction Balancer"

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        layout = QVBoxLayout(self)

        info = QLabel(
            "Enter one or more unbalanced reactions, one per line.\n"
            "Use '->' or '=' for arrows, '+' between species.\n"
            "Example:\nH2 + O2 -> H2O\nC3H8 + O2 = CO2 + H2O"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.input = QTextEdit()
        self.input.setFont(QFont("Courier New", 10))
        layout.addWidget(self.input)

        row = QHBoxLayout()
        self.balance_btn = QPushButton("Balance All")
        self.copy_btn = QPushButton("Copy Selected")
        row.addWidget(self.balance_btn); row.addWidget(self.copy_btn)
        layout.addLayout(row)

        self.list = QListWidget()
        layout.addWidget(self.list)

        self.balance_btn.clicked.connect(self._balance_all)
        self.copy_btn.clicked.connect(self._copy_selected)

    def _balance_all(self):
        self.list.clear()
        reactions = [r for r in self.input.toPlainText().splitlines() if r.strip()]
        for rxn in reactions:
            try:
                coeffs, reactants, products = balance_reaction(rxn)
                balanced = format_balanced(coeffs, reactants, products)
                self.list.addItem(QListWidgetItem(balanced))
                add_log_entry("Reaction Balancer", action="Balance", data={"input": rxn, "output": balanced})
            except Exception as e:
                item = QListWidgetItem(f"Error balancing '{rxn}': {e}")
                item.setForeground(QColor(Qt.GlobalColor.red))
                self.list.addItem(item)
                add_log_entry("Reaction Balancer", action="Error", data={"input": rxn, "error": str(e)})

    def _copy_selected(self):
        items = self.list.selectedItems()
        if not items:
            QMessageBox.information(self, "Copy", "Select an item to copy."); return
        text = "\n".join(i.text() for i in items)
        self.clipboard().setText(text)
