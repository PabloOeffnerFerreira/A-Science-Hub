from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QWidget
from PyQt6.QtCore import Qt, QTimer
from tools.panel_tools import calc_service
from UI.common.var_chip import VarChip

class SimpleCalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(8,8,8,8)
        root.setSpacing(8)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Expression or assignment (e.g. a=2, 3*sin(pi/6))")
        self.btn_clear = QPushButton("Reset Vars")
        row.addWidget(self.input, 1)
        row.addWidget(self.btn_clear, 0)
        root.addLayout(row)

        self.output = QLineEdit()
        self.output.setReadOnly(True)
        root.addWidget(self.output)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.vars_layout = QVBoxLayout(self.container)
        self.vars_layout.setContentsMargins(0,0,0,0)
        self.vars_layout.setSpacing(6)
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self._do_eval)

        self.btn_clear.clicked.connect(self._reset_vars)
        self.input.textEdited.connect(self._schedule_eval)
        self.input.returnPressed.connect(self._do_eval)

        self._reload_vars()

    def _schedule_eval(self):
        self.timer.start()

    def _do_eval(self):
        text = self.input.text()
        val = calc_service.evaluate(text)
        if val is None:
            self.output.clear()
        else:
            try:
                self.output.setText(f"{float(val):.12g}")
            except Exception:
                self.output.setText(str(val))
        self._reload_vars()

    def _reset_vars(self):
        calc_service.reset_vars()
        self._reload_vars()

    def _reload_vars(self):
        while self.vars_layout.count():
            it = self.vars_layout.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
        for name, value in calc_service.variables().items():
            chip = VarChip(name, value)
            chip.removeRequested.connect(self._remove_var)
            self.vars_layout.addWidget(chip, 0, Qt.AlignmentFlag.AlignTop)
        self.vars_layout.addStretch(1)

    def _remove_var(self, name):
        calc_service.delete_var(name)
        self._reload_vars()
