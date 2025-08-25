from __future__ import annotations
from PyQt6 import QtWidgets, QtGui
from core.ai.ash_assistant.ash_assistant import ash_answer_stream, extract_action_json

class Tool(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ASH Assistant")
        self.resize(800, 560)

        self.input = QtWidgets.QTextEdit()
        self.send  = QtWidgets.QPushButton("Ask")
        self.output= QtWidgets.QTextEdit(); self.output.setReadOnly(True)
        self.action= QtWidgets.QLineEdit(); self.action.setReadOnly(True)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(QtWidgets.QLabel("Question"))
        lay.addWidget(self.input,1)
        lay.addWidget(self.send)
        lay.addWidget(QtWidgets.QLabel("Answer"))
        lay.addWidget(self.output,2)
        lay.addWidget(QtWidgets.QLabel("Action JSON"))
        lay.addWidget(self.action)

        self.send.clicked.connect(self.on_send)

    def on_send(self):
        q = self.input.toPlainText().strip()
        if not q: return
        self.output.clear(); self.action.clear()
        buf=[]
        for chunk in ash_answer_stream(q):
            buf.append(chunk)
            self.output.moveCursor(QtGui.QTextCursor.MoveOperation.End)
            self.output.insertPlainText(chunk)
            QtWidgets.QApplication.processEvents()
        full = "".join(buf)
        act = extract_action_json(full)
        if act: self.action.setText(act)