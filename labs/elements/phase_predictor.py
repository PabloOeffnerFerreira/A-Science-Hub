
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from core.data.functions.log import add_log_entry
from core.data.functions.chemistry_utils import load_element_data, parse_temperature, to_kelvin

def _as_float(x):
    try:
        return float(x)
    except Exception:
        return None

class Tool(QDialog):
    TITLE = "Phase Predictor"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(380)
        self.data = load_element_data()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Element Symbol:"))
        self.sym = QLineEdit(); layout.addWidget(self.sym)

        layout.addWidget(QLabel("Temperature (°C, °F, or K, e.g. 25, 77F, 300K):"))
        self.temp = QLineEdit(); self.temp.setText("25"); layout.addWidget(self.temp)

        layout.addWidget(QLabel("Pressure (atm, optional):"))
        self.press = QLineEdit(); self.press.setPlaceholderText("Default: 1 atm"); layout.addWidget(self.press)

        self.result = QLabel(""); self.result.setWordWrap(True); layout.addWidget(self.result)

        btn = QPushButton("Check Phase"); btn.clicked.connect(self._predict); layout.addWidget(btn)

    def _predict(self):
        sym = self.sym.text().strip().capitalize()
        ttxt = self.temp.text().strip()
        ptxt = self.press.text().strip()

        try:
            tval, tunit = parse_temperature(ttxt)
            tk = to_kelvin(tval, tunit)
        except Exception as e:
            self.result.setText(f"<span style='color:red'>Enter a valid temperature. ({e})</span>"); return

        try:
            p = float(ptxt) if ptxt else 1.0
        except Exception:
            p = 1.0

        el = self.data.get(sym)
        if not el:
            self.result.setText(f"<span style='color:red'>Element symbol '{sym}' not found.</span>"); return

        melt = _as_float(el.get("melt") or el.get("MeltingPoint"))
        boil = _as_float(el.get("boil") or el.get("BoilingPoint"))
        if melt is None or boil is None:
            msg = "No melting or boiling point data available."
            self.result.setText(msg)
            add_log_entry("Phase Predictor", action="NoData", data={"symbol": sym}); return

        if tk < melt:
            phase = "solid"
        elif melt <= tk < boil:
            phase = "liquid"
        else:
            phase = "gas"

        msg = (f"Melting point: {melt:.2f} K<br>"
               f"Boiling point: {boil:.2f} K<br>"
               f"<b>Predicted phase at {tval:.1f}°{tunit.upper()} and {p} atm: "
               f"<span style='color: {'blue' if phase=='solid' else 'orange' if phase=='liquid' else 'red'};'>{phase.capitalize()}</span></b>")
        self.result.setText(msg)
        add_log_entry("Phase Predictor", action="Predict", data={"symbol": sym, "T_K": tk, "P_atm": p, "phase": phase})
