
from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Ohm's Law"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(420)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Enter any two; leave one blank."))

        def row(lbl, units):
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); e=QLineEdit(); u=QComboBox(); u.addItems(units); r.addWidget(e); r.addWidget(u); lay.addLayout(r); return e,u
        self.V, self.Vu = row("Voltage V:", ["V","mV","kV"])
        self.I, self.Iu = row("Current I:", ["A","mA","kA"])
        self.R, self.Ru = row("Resistance R:", ["Ω","mΩ","kΩ","MΩ"])

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Solve"); lay.addWidget(btn); btn.clicked.connect(self._go)

    @staticmethod
    def _to_base(val: float, unit: str) -> float:
        if unit in ("mV","mA","mΩ"): return val/1000.0
        if unit == "kV" or unit == "kA" or unit == "kΩ": return val*1000.0
        if unit == "MΩ": return val*1e6
        return val

    @staticmethod
    def _from_base(val: float, unit: str) -> float:
        if unit in ("mV","mA","mΩ"): return val*1000.0
        if unit == "kV" or unit == "kA" or unit == "kΩ": return val/1000.0
        if unit == "MΩ": return val/1e6
        return val

    def _go(self):
        try:
            V = self.V.text().strip(); I = self.I.text().strip(); R = self.R.text().strip()
            Vb = None if V=="" else self._to_base(float(V), self.Vu.currentText())
            Ib = None if I=="" else self._to_base(float(I), self.Iu.currentText())
            Rb = None if R=="" else self._to_base(float(R), self.Ru.currentText())

            if sum(x is not None for x in (Vb,Ib,Rb)) != 2:
                self.result.setText("Fill exactly two fields."); return

            if Vb is None:
                Vb = Ib*Rb
                out = self._from_base(Vb, self.Vu.currentText()); label="Voltage"; unit=self.Vu.currentText()
            elif Ib is None:
                Ib = Vb/Rb
                out = self._from_base(Ib, self.Iu.currentText()); label="Current"; unit=self.Iu.currentText()
            else:
                Rb = Vb/Ib
                out = self._from_base(Rb, self.Ru.currentText()); label="Resistance"; unit=self.Ru.currentText()

            self.result.setText(f"{label} = {out:.6g} {unit}")
            add_log_entry(self.TITLE, action="Solve", data={"V": Vb, "I": Ib, "R": Rb, "label": label})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
