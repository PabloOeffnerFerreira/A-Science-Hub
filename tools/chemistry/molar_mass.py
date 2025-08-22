
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from core.data.functions.log import add_log_entry
from core.data.functions.chemistry_utils import load_element_data, parse_hydrate, atomic_mass_u

class Tool(QDialog):
    TITLE = "Molar Mass Calculator"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(420)
        self._elements = load_element_data()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter molecular formula (e.g. H2O, C6H12O6, CuSO4·5H2O):"))
        self.formula_entry = QLineEdit()
        self.formula_entry.setPlaceholderText("Example: C6H12O6 or CuSO4·5H2O")
        layout.addWidget(self.formula_entry)

        btn_row = QHBoxLayout()
        calc = QPushButton("Calculate")
        clear = QPushButton("Clear")
        btn_row.addWidget(calc); btn_row.addWidget(clear)
        layout.addLayout(btn_row)

        self.result = QTextEdit(); self.result.setReadOnly(True)
        layout.addWidget(self.result)

        calc.clicked.connect(self._calculate)
        clear.clicked.connect(lambda: (self.formula_entry.clear(), self.result.clear()))

    def _calculate(self):
        formula = self.formula_entry.text().strip()
        if not formula:
            self.result.setText("Please enter a molecular formula."); return
        try:
            counts = parse_hydrate(formula)
        except Exception as e:
            self.result.setText(f"Error parsing formula: {e}"); return

        total_mass = 0.0
        unknown = []
        lines = []
        for el, cnt in sorted(counts.items()):
            data = self._elements.get(el)
            if not data:
                unknown.append(el); continue
            am = atomic_mass_u(data)
            if am is None:
                unknown.append(el); continue
            subtotal = am * cnt
            total_mass += subtotal
            name = data.get("name") or data.get("Element") or el
            lines.append(f"{el} ({name}) × {cnt} = {subtotal:.5f} g/mol")
        if unknown:
            lines.append("\nUnknown or massless elements: " + ", ".join(unknown))
        lines.append(f"\nTotal Molecular Weight: {total_mass:.5f} g/mol")
        out = "\n".join(lines)
        self.result.setText(out)
        add_log_entry("Molar Mass Calculator", action="Compute",
                      data={"formula": formula, "mass_g_mol": total_mass, "breakdown": lines})
