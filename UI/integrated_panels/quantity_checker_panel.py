from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt

QUANTITIES = [
    {
        "id": "length",
        "names": {"en": "Length"},
        "unit_name": "metre",
        "unit_symbol": "m",
        "regions": {"EU": {"Q": "l"}, "UK/US": {"Q": "l"}, "BR": {"Q": "l"}},
    },
    {
        "id": "mass",
        "names": {"en": "Mass"},
        "unit_name": "kilogram",
        "unit_symbol": "kg",
        "regions": {"EU": {"Q": "m"}, "UK/US": {"Q": "m"}, "BR": {"Q": "m"}},
    },
    {
        "id": "time",
        "names": {"en": "Time"},
        "unit_name": "second",
        "unit_symbol": "s",
        "regions": {"EU": {"Q": "t"}, "UK/US": {"Q": "t"}, "BR": {"Q": "t"}},
    },
    {
        "id": "electric_current",
        "names": {"en": "Electric current"},
        "unit_name": "ampere",
        "unit_symbol": "A",
        "regions": {"EU": {"Q": "I"}, "UK/US": {"Q": "I"}, "BR": {"Q": "I"}},
    },
    {
        "id": "thermodynamic_temperature",
        "names": {"en": "Thermodynamic temperature"},
        "unit_name": "kelvin",
        "unit_symbol": "K",
        "regions": {"EU": {"Q": "T"}, "UK/US": {"Q": "T"}, "BR": {"Q": "T"}},
    },
    {
        "id": "amount_of_substance",
        "names": {"en": "Amount of substance"},
        "unit_name": "mole",
        "unit_symbol": "mol",
        "regions": {"EU": {"Q": "n"}, "UK/US": {"Q": "n"}, "BR": {"Q": "n"}},
    },
    {
        "id": "luminous_intensity",
        "names": {"en": "Luminous intensity"},
        "unit_name": "candela",
        "unit_symbol": "cd",
        "regions": {"EU": {"Q": "I_v"}, "UK/US": {"Q": "I_v"}, "BR": {"Q": "I_v"}},
    },
    {
        "id": "electric_charge",
        "names": {"en": "Electric charge"},
        "unit_name": "coulomb",
        "unit_symbol": "C",
        "regions": {"EU": {"Q": "Q"}, "UK/US": {"Q": "Q"}, "BR": {"Q": "Q"}},
    },
    {
        "id": "electric_potential_difference",
        "names": {"en": "Electric potential difference"},
        "unit_name": "volt",
        "unit_symbol": "V",
        "regions": {"EU": {"Q": "U"}, "UK/US": {"Q": "V"}, "BR": {"Q": "v"}},
    },
    {
        "id": "electric_field_strength",
        "names": {"en": "Electric field strength"},
        "unit_name": "volt per metre",
        "unit_symbol": "V/m",
        "regions": {"EU": {"Q": "E"}, "UK/US": {"Q": "E"}, "BR": {"Q": "E"}},
    },
    {
        "id": "magnetic_flux_density",
        "names": {"en": "Magnetic flux density"},
        "unit_name": "tesla",
        "unit_symbol": "T",
        "regions": {"EU": {"Q": "B"}, "UK/US": {"Q": "B"}, "BR": {"Q": "B"}},
    },
    {
        "id": "magnetic_field_strength",
        "names": {"en": "Magnetic field strength"},
        "unit_name": "ampere per metre",
        "unit_symbol": "A/m",
        "regions": {"EU": {"Q": "H"}, "UK/US": {"Q": "H"}, "BR": {"Q": "H"}},
    },
    {
        "id": "resistance",
        "names": {"en": "Electrical resistance"},
        "unit_name": "ohm",
        "unit_symbol": "Ω",
        "regions": {"EU": {"Q": "R"}, "UK/US": {"Q": "R"}, "BR": {"Q": "R"}},
    },
    {
        "id": "conductance",
        "names": {"en": "Electrical conductance"},
        "unit_name": "siemens",
        "unit_symbol": "S",
        "regions": {"EU": {"Q": "G"}, "UK/US": {"Q": "G"}, "BR": {"Q": "G"}},
    },
    {
        "id": "capacitance",
        "names": {"en": "Capacitance"},
        "unit_name": "farad",
        "unit_symbol": "F",
        "regions": {"EU": {"Q": "C"}, "UK/US": {"Q": "C"}, "BR": {"Q": "C"}},
    },
    {
        "id": "inductance",
        "names": {"en": "Inductance"},
        "unit_name": "henry",
        "unit_symbol": "H",
        "regions": {"EU": {"Q": "L"}, "UK/US": {"Q": "L"}, "BR": {"Q": "L"}},
    },
    {
        "id": "power",
        "names": {"en": "Power"},
        "unit_name": "watt",
        "unit_symbol": "W",
        "regions": {"EU": {"Q": "P"}, "UK/US": {"Q": "P"}, "BR": {"Q": "P"}},
    },
    {
        "id": "energy",
        "names": {"en": "Energy"},
        "unit_name": "joule",
        "unit_symbol": "J",
        "regions": {"EU": {"Q": "E"}, "UK/US": {"Q": "E"}, "BR": {"Q": "E"}},
    },
    {
        "id": "work",
        "names": {"en": "Work"},
        "unit_name": "joule",
        "unit_symbol": "J",
        "regions": {"EU": {"Q": "W"}, "UK/US": {"Q": "W"}, "BR": {"Q": "W"}},
    },
    {
        "id": "force",
        "names": {"en": "Force"},
        "unit_name": "newton",
        "unit_symbol": "N",
        "regions": {"EU": {"Q": "F"}, "UK/US": {"Q": "F"}, "BR": {"Q": "F"}},
    },
    {
        "id": "torque",
        "names": {"en": "Torque"},
        "unit_name": "newton metre",
        "unit_symbol": "N·m",
        "regions": {"EU": {"Q": "M"}, "UK/US": {"Q": "τ"}, "BR": {"Q": "M"}},
    },
    {
        "id": "pressure",
        "names": {"en": "Pressure"},
        "unit_name": "pascal",
        "unit_symbol": "Pa",
        "regions": {"EU": {"Q": "p"}, "UK/US": {"Q": "p"}, "BR": {"Q": "p"}},
    },
    {
        "id": "frequency",
        "names": {"en": "Frequency"},
        "unit_name": "hertz",
        "unit_symbol": "Hz",
        "regions": {"EU": {"Q": "f"}, "UK/US": {"Q": "f"}, "BR": {"Q": "f"}},
    },
    {
        "id": "wavelength",
        "names": {"en": "Wavelength"},
        "unit_name": "metre",
        "unit_symbol": "m",
        "regions": {"EU": {"Q": "λ"}, "UK/US": {"Q": "λ"}, "BR": {"Q": "λ"}},
    },
    {
        "id": "angular_velocity",
        "names": {"en": "Angular velocity"},
        "unit_name": "radian per second",
        "unit_symbol": "rad/s",
        "regions": {"EU": {"Q": "ω"}, "UK/US": {"Q": "ω"}, "BR": {"Q": "ω"}},
    },
    {
        "id": "acceleration",
        "names": {"en": "Acceleration"},
        "unit_name": "metre per second squared",
        "unit_symbol": "m/s²",
        "regions": {"EU": {"Q": "a"}, "UK/US": {"Q": "a"}, "BR": {"Q": "a"}},
    },
    {
        "id": "momentum",
        "names": {"en": "Momentum"},
        "unit_name": "kilogram metre per second",
        "unit_symbol": "kg·m/s",
        "regions": {"EU": {"Q": "p"}, "UK/US": {"Q": "p"}, "BR": {"Q": "p"}},
    },
    {
        "id": "density",
        "names": {"en": "Density"},
        "unit_name": "kilogram per cubic metre",
        "unit_symbol": "kg/m³",
        "regions": {"EU": {"Q": "ρ"}, "UK/US": {"Q": "ρ"}, "BR": {"Q": "ρ"}},
    }
]

class ScientificQuantityChecker(QWidget):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 200)

        self._region = "EU"
        self._index_by = "Quantity"

        self._by_quantity = {}
        self._by_qsymbol = {}
        self._by_usymbol = {}
        self._rebuild_indexes()

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.region = QComboBox()
        self.region.addItems(["EU", "UK/US", "BR"])

        self.search_mode = QComboBox()
        self.search_mode.addItems(["Quantity", "Q Symbol", "Unit Symbol"])

        self.selector = QComboBox()
        self._refill_selector()

        self.q_name = QLineEdit(); self.q_name.setReadOnly(True); self.q_name.setFixedHeight(20)
        self.q_sym  = QLineEdit(); self.q_sym.setReadOnly(True);  self.q_sym.setFixedHeight(20)
        self.u_name = QLineEdit(); self.u_name.setReadOnly(True); self.u_name.setFixedHeight(20)
        self.u_sym  = QLineEdit(); self.u_sym.setReadOnly(True);  self.u_sym.setFixedHeight(20)

        form.addRow(self._lbl("Region"), self.region)
        form.addRow(self._lbl("Search by"), self.search_mode)
        form.addRow(self._lbl("Select"), self.selector)
        form.addRow(self._lbl("Q.Name"), self.q_name)
        form.addRow(self._lbl("Q.Symbol"), self.q_sym)
        form.addRow(self._lbl("U.Name"), self.u_name)
        form.addRow(self._lbl("U.Symbol"), self.u_sym)

        root.addLayout(form)

        self.region.currentTextChanged.connect(self._on_region_changed)
        self.search_mode.currentTextChanged.connect(self._on_mode_changed)
        self.selector.currentTextChanged.connect(self._on_select_changed)

        self._on_select_changed(self.selector.currentText())

    def _lbl(self, t):
        l = QLabel(t)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return l

    def _rebuild_indexes(self):
        self._by_quantity = {}
        self._by_qsymbol = {}
        self._by_usymbol = {}
        for item in QUANTITIES:
            qname = item["names"]["en"]
            unit_name = item["unit_name"]
            usym = item["unit_symbol"]
            qsym = item["regions"][self._region]["Q"]
            self._by_quantity[qname] = item
            self._by_qsymbol[qsym] = item
            self._by_usymbol[usym] = item

    def _refill_selector(self):
        self.selector.blockSignals(True)
        self.selector.clear()
        if self._index_by == "Quantity":
            self.selector.addItems(sorted(self._by_quantity.keys()))
        elif self._index_by == "Q Symbol":
            self.selector.addItems(sorted(self._by_qsymbol.keys(), key=lambda s: (len(s), s)))
        else:
            self.selector.addItems(sorted(self._by_usymbol.keys(), key=lambda s: (len(s), s)))
        self.selector.blockSignals(False)

    def _on_region_changed(self, r):
        self._region = r
        self._rebuild_indexes()
        self._refill_selector()
        self._on_select_changed(self.selector.currentText())

    def _on_mode_changed(self, mode):
        self._index_by = mode
        self._refill_selector()
        self._on_select_changed(self.selector.currentText())

    def _on_select_changed(self, key):
        if not key:
            self.q_name.clear(); self.q_sym.clear(); self.u_name.clear(); self.u_sym.clear()
            return
        if self._index_by == "Quantity":
            item = self._by_quantity.get(key)
        elif self._index_by == "Q Symbol":
            item = self._by_qsymbol.get(key)
        else:
            item = self._by_usymbol.get(key)
        if not item:
            self.q_name.clear(); self.q_sym.clear(); self.u_name.clear(); self.u_sym.clear()
            return
        qname = item["names"]["en"]
        qsym = item["regions"][self._region]["Q"]
        self.q_name.setText(qname)
        self.q_sym.setText(qsym)
        self.u_name.setText(item["unit_name"])
        self.u_sym.setText(item["unit_symbol"])
