from __future__ import annotations

import math
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QGridLayout, QScrollArea, QComboBox, QMessageBox
)

# Only log CALCULATIONS (no navigation)
try:
    from core.data.functions.log import add_log_entry
except Exception:  # fallback no-op if logger not present
    def add_log_entry(*_, **__): pass

# Physical constants
EPS0 = 8.854187817e-12  # F/m
MU0  = 4e-7 * math.pi   # H/m
SQRT2 = math.sqrt(2.0)


# ---------- small helpers ----------
def line_edit_float(placeholder: str = "", minimum: float | None = None) -> QLineEdit:
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    v = QDoubleValidator()
    if minimum is not None:
        v.setBottom(minimum)
    le.setValidator(v)
    return le

def line_edit_int(placeholder: str = "", minimum: int | None = None) -> QLineEdit:
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    v = QIntValidator()
    if minimum is not None:
        v.setBottom(minimum)
    le.setValidator(v)
    return le

def set_output(label: QLabel, value: float, unit: str):
    # Format with engineering prefixes
    if value == 0 or math.isnan(value) or math.isinf(value):
        label.setText("—")
        return
    prefixes = [
        (1e-12, "p"), (1e-9, "n"), (1e-6, "µ"), (1e-3, "m"),
        (1, ""), (1e3, "k"), (1e6, "M"), (1e9, "G")
    ]
    # Choose prefix that keeps 1 ≤ n < 1000
    scaled = value
    best = ("", 1.0)
    for scale, p in prefixes:
        n = value / scale
        if 1 <= abs(n) < 1000:
            scaled = n
            best = (p, scale)
            break
    label.setText(f"{scaled:.6g} {best[0]}{unit}")


# ---------- Resistor Color Code ----------
class ResistorBands(QWidget):
    BANDS = [
        ("Black",  0, 1,  None),
        ("Brown",  1, 10, "±1%"),
        ("Red",    2, 100,"±2%"),
        ("Orange", 3, 1_000, None),
        ("Yellow", 4, 10_000, None),
        ("Green",  5, 100_000, "±0.5%"),
        ("Blue",   6, 1_000_000, "±0.25%"),
        ("Violet", 7, 10_000_000, "±0.1%"),
        ("Grey",   8, 100_000_000, "±0.05%"),
        ("White",  9, 1_000_000_000, None),
        ("Gold",   None, 0.1, "±5%"),
        ("Silver", None, 0.01, "±10%"),
    ]
    def __init__(self, parent=None):
        super().__init__(parent)
        gb = QGroupBox("Resistor Color Code (4-band)")
        lay = QGridLayout(gb)

        self.band1 = QComboBox(); self.band2 = QComboBox(); self.mult = QComboBox(); self.tol = QComboBox()
        digits = [b[0] for b in self.BANDS if b[1] is not None][:10]
        multipliers = [b[0] for b in self.BANDS if b[2] is not None]
        tolerances = [b[3] for b in self.BANDS if b[3] is not None]
        tol_to_color = {b[3]: b[0] for b in self.BANDS if b[3]}

        for d in digits: self.band1.addItem(d); self.band2.addItem(d)
        for m in multipliers: self.mult.addItem(m)
        for t in tolerances: self.tol.addItem(t)

        self.out_val = QLabel("—")
        self.btn_calc = QPushButton("Compute")

        lay.addWidget(QLabel("Band 1"), 0, 0); lay.addWidget(self.band1, 0, 1)
        lay.addWidget(QLabel("Band 2"), 0, 2); lay.addWidget(self.band2, 0, 3)
        lay.addWidget(QLabel("Multiplier"), 1, 0); lay.addWidget(self.mult, 1, 1)
        lay.addWidget(QLabel("Tolerance"), 1, 2); lay.addWidget(self.tol, 1, 3)
        lay.addWidget(self.btn_calc, 2, 0, 1, 1)
        lay.addWidget(QLabel("Value"), 2, 2); lay.addWidget(self.out_val, 2, 3)

        root = QVBoxLayout(self)
        root.addWidget(gb)

        def do_calc():
            d1 = [b for b in self.BANDS if b[0] == self.band1.currentText()][0][1]
            d2 = [b for b in self.BANDS if b[0] == self.band2.currentText()][0][1]
            mul = [b for b in self.BANDS if b[0] == self.mult.currentText()][0][2]
            tol = self.tol.currentText()
            if d1 is None or d2 is None or mul is None:
                self.out_val.setText("—")
                return
            ohms = (10*d1 + d2) * mul
            set_output(self.out_val, ohms, "Ω")
            add_log_entry("ResistorBands", "compute", {"digits": [d1, d2], "mul": mul, "tol": tol, "ohms": ohms})

        self.btn_calc.clicked.connect(do_calc)


# ---------- Capacitance (parallel plates) ----------
class Capacitance(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        gb = QGroupBox("Capacitance (parallel plates)")
        lay = QGridLayout(gb)

        self.A = line_edit_float("Area A (m^2)", 0.0)
        self.d = line_edit_float("Separation d (m)", 0.0)
        self.er = line_edit_float("Relative permittivity εr", 0.0); self.er.setText("1.0")

        self.out_C = QLabel("—")
        self.btn = QPushButton("Compute")

        lay.addWidget(QLabel("A"), 0, 0); lay.addWidget(self.A, 0, 1)
        lay.addWidget(QLabel("d"), 0, 2); lay.addWidget(self.d, 0, 3)
        lay.addWidget(QLabel("εr"), 1, 0); lay.addWidget(self.er, 1, 1)
        lay.addWidget(self.btn, 1, 3)
        lay.addWidget(QLabel("Capacitance"), 2, 2); lay.addWidget(self.out_C, 2, 3)

        root = QVBoxLayout(self); root.addWidget(gb)

        def compute():
            try:
                A = float(self.A.text()); d = float(self.d.text()); er = float(self.er.text())
                C = EPS0 * er * A / d
                set_output(self.out_C, C, "F")
                add_log_entry("Capacitance", "compute", {"A": A, "d": d, "er": er, "C": C})
            except Exception as e:
                QMessageBox.warning(self, "Capacitance", f"Invalid input: {e}")

        self.btn.clicked.connect(compute)


# ---------- Inductance (solenoid) ----------
class Inductance(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        gb = QGroupBox("Inductance (solenoid)")
        lay = QGridLayout(gb)

        self.N = line_edit_int("Turns N", 1)
        self.len_m = line_edit_float("Length ℓ (m)", 0.0)
        self.area = line_edit_float("Cross-section A (m^2)", 0.0)
        self.mur = line_edit_float("μr", 0.0); self.mur.setText("1.0")

        self.out_L = QLabel("—")
        self.btn = QPushButton("Compute")

        lay.addWidget(QLabel("N"), 0, 0); lay.addWidget(self.N, 0, 1)
        lay.addWidget(QLabel("ℓ"), 0, 2); lay.addWidget(self.len_m, 0, 3)
        lay.addWidget(QLabel("A"), 1, 0); lay.addWidget(self.area, 1, 1)
        lay.addWidget(QLabel("μr"), 1, 2); lay.addWidget(self.mur, 1, 3)
        lay.addWidget(self.btn, 2, 0)
        lay.addWidget(QLabel("Inductance"), 2, 2); lay.addWidget(self.out_L, 2, 3)

        root = QVBoxLayout(self); root.addWidget(gb)

        def compute():
            try:
                N = int(self.N.text()); l = float(self.len_m.text()); A = float(self.area.text()); mur = float(self.mur.text())
                L = MU0 * mur * (N**2) * A / l
                set_output(self.out_L, L, "H")
                add_log_entry("Inductance", "compute", {"N": N, "l": l, "A": A, "mur": mur, "L": L})
            except Exception as e:
                QMessageBox.warning(self, "Inductance", f"Invalid input: {e}")

        self.btn.clicked.connect(compute)


# ---------- RC time constant ----------
class RCTau(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        gb = QGroupBox("RC Time Constant")
        lay = QGridLayout(gb)

        self.R = line_edit_float("R (Ω)", 0.0)
        self.C = line_edit_float("C (F)", 0.0)

        self.out_tau = QLabel("—")
        self.btn = QPushButton("Compute")

        lay.addWidget(QLabel("R"), 0, 0); lay.addWidget(self.R, 0, 1)
        lay.addWidget(QLabel("C"), 0, 2); lay.addWidget(self.C, 0, 3)
        lay.addWidget(self.btn, 1, 0)
        lay.addWidget(QLabel("τ = R·C"), 1, 2); lay.addWidget(self.out_tau, 1, 3)

        root = QVBoxLayout(self); root.addWidget(gb)

        def compute():
            try:
                R = float(self.R.text()); C = float(self.C.text())
                tau = R * C
                set_output(self.out_tau, tau, "s")
                add_log_entry("RC_Tau", "compute", {"R": R, "C": C, "tau": tau})
            except Exception as e:
                QMessageBox.warning(self, "RC τ", f"Invalid input: {e}")

        self.btn.clicked.connect(compute)


# ---------- Power & Energy ----------
class PowerEnergy(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        gb = QGroupBox("Power & Energy")
        lay = QGridLayout(gb)

        self.V = line_edit_float("Voltage V (V)", 0.0)
        self.I = line_edit_float("Current I (A)", 0.0)
        self.R = line_edit_float("Resistance R (Ω)", 0.0)
        self.hours = line_edit_float("Time (hours)", 0.0); self.hours.setText("1")
        self.price = line_edit_float("Price (per kWh)", 0.0)

        self.out_P = QLabel("—")
        self.out_E = QLabel("—")
        self.out_cost = QLabel("—")
        self.btn = QPushButton("Compute")

        lay.addWidget(QLabel("V"), 0, 0); lay.addWidget(self.V, 0, 1)
        lay.addWidget(QLabel("I"), 0, 2); lay.addWidget(self.I, 0, 3)
        lay.addWidget(QLabel("R"), 1, 0); lay.addWidget(self.R, 1, 1)
        lay.addWidget(QLabel("Hours"), 1, 2); lay.addWidget(self.hours, 1, 3)
        lay.addWidget(QLabel("Price/kWh"), 2, 0); lay.addWidget(self.price, 2, 1)
        lay.addWidget(self.btn, 2, 3)
        lay.addWidget(QLabel("Power P"), 3, 2); lay.addWidget(self.out_P, 3, 3)
        lay.addWidget(QLabel("Energy"), 4, 2); lay.addWidget(self.out_E, 4, 3)
        lay.addWidget(QLabel("Cost"), 5, 2); lay.addWidget(self.out_cost, 5, 3)

        root = QVBoxLayout(self); root.addWidget(gb)

        def compute():
            try:
                V = float(self.V.text()) if self.V.text() else None
                I = float(self.I.text()) if self.I.text() else None
                R = float(self.R.text()) if self.R.text() else None
                h = float(self.hours.text()) if self.hours.text() else 0.0
                price = float(self.price.text()) if self.price.text() else 0.0

                # Determine power P using available inputs
                P = None
                if V is not None and I is not None:
                    P = V * I
                elif V is not None and R is not None and R != 0:
                    P = V * V / R
                elif I is not None and R is not None:
                    P = (I ** 2) * R

                if P is None:
                    raise ValueError("Provide at least two of V, I, R")

                set_output(self.out_P, P, "W")

                # Energy in kWh and J
                E_kWh = (P * h) / 1000.0
                self.out_E.setText(f"{E_kWh:.6g} kWh")
                cost = E_kWh * price if price else 0.0
                self.out_cost.setText(f"{cost:.6g}")

                add_log_entry("PowerEnergy", "compute", {"V": V, "I": I, "R": R, "hours": h, "P": P, "E_kWh": E_kWh, "cost": cost})
            except Exception as e:
                QMessageBox.warning(self, "Power & Energy", f"Invalid input: {e}")

        self.btn.clicked.connect(compute)


# ---------- AC Wave (RMS helper only, no plot to keep this compact) ----------
class ACWave(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        gb = QGroupBox("AC Wave (RMS / Peak conversions)")
        lay = QGridLayout(gb)

        self.v_rms = line_edit_float("V_rms (V)", 0.0)
        self.i_rms = line_edit_float("I_rms (A)", 0.0)

        self.out_v_peak = QLabel("—")
        self.out_i_peak = QLabel("—")
        self.btn = QPushButton("Compute peaks")

        lay.addWidget(QLabel("V_rms"), 0, 0); lay.addWidget(self.v_rms, 0, 1)
        lay.addWidget(QLabel("I_rms"), 0, 2); lay.addWidget(self.i_rms, 0, 3)
        lay.addWidget(self.btn, 1, 0)
        lay.addWidget(QLabel("V_peak"), 1, 2); lay.addWidget(self.out_v_peak, 1, 3)
        lay.addWidget(QLabel("I_peak"), 2, 2); lay.addWidget(self.out_i_peak, 2, 3)

        root = QVBoxLayout(self); root.addWidget(gb)

        def compute():
            try:
                v_rms = float(self.v_rms.text()) if self.v_rms.text() else None
                i_rms = float(self.i_rms.text()) if self.i_rms.text() else None
                if v_rms is None and i_rms is None:
                    raise ValueError("Enter V_rms and/or I_rms")

                if v_rms is not None:
                    set_output(self.out_v_peak, v_rms * SQRT2, "V")
                else:
                    self.out_v_peak.setText("—")
                if i_rms is not None:
                    set_output(self.out_i_peak, i_rms * SQRT2, "A")
                else:
                    self.out_i_peak.setText("—")

                add_log_entry("ACWave", "compute", {"V_rms": v_rms, "I_rms": i_rms})
            except Exception as e:
                QMessageBox.warning(self, "AC Wave", f"Invalid input: {e}")

        self.btn.clicked.connect(compute)


# ---------- Main container dialog (single window, all tools embedded) ----------
class Tool(QDialog):
    TITLE = "Electricity Mini Tools"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(self.TITLE)
        self.resize(1000, 800)

        # Scroll area for all mini tools in one window
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)

        col = QVBoxLayout(content)
        col.setContentsMargins(10, 10, 10, 10)
        col.setSpacing(12)

        # Add all mini tools here (no tabs)
        col.addWidget(ResistorBands(self))
        col.addWidget(Capacitance(self))
        col.addWidget(Inductance(self))
        col.addWidget(RCTau(self))
        col.addWidget(PowerEnergy(self))
        col.addWidget(ACWave(self))

        col.addStretch(1)

        root = QVBoxLayout(self)
        root.addWidget(scroll)
