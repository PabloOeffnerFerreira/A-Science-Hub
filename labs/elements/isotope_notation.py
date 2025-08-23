
import datetime
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from core.data.functions.chemistry_utils import load_element_data
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry
try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None

class Tool(QDialog):
    TITLE = "Isotopic Notation"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)

        self.data = load_element_data()

        # Inputs
        self.symbol_entry = QLineEdit(); self.symbol_entry.setPlaceholderText("Element symbol (e.g., H, He, Fe)")
        layout.addWidget(QLabel("Element Symbol:")); layout.addWidget(self.symbol_entry)

        self.mass_entry = QLineEdit(); self.mass_entry.setPlaceholderText("Mass number (integer)")
        layout.addWidget(QLabel("Mass Number (unitless):")); layout.addWidget(self.mass_entry)

        # Buttons
        btn_row = QHBoxLayout()
        self.calc_btn = QPushButton("Calculate")
        self.export_btn = QPushButton("Export Chart")
        btn_row.addWidget(self.calc_btn); btn_row.addWidget(self.export_btn)
        layout.addLayout(btn_row)

        # Result + Figure
        self.result = QTextEdit(); self.result.setReadOnly(True); self.result.setMinimumHeight(150)
        layout.addWidget(self.result)
        self.figure = Figure(figsize=(4,3)); self.canvas = FigureCanvas(self.figure); layout.addWidget(self.canvas)

        self.calc_btn.clicked.connect(self._calculate)
        self.export_btn.clicked.connect(self._export_chart)

        self.last_img_path = None

    def _calculate(self):
        sym = self.symbol_entry.text().strip().capitalize()
        mass_str = self.mass_entry.text().strip()
        if not sym or not mass_str:
            self._show_error("Please enter both element symbol and mass number."); return
        if sym not in self.data:
            self._show_error(f"Element symbol '{sym}' not found."); return
        try:
            mass_num = int(mass_str)
        except ValueError:
            self._show_error("Mass number must be an integer."); return

        el = self.data[sym]
        Z = el.get("number") or el.get("AtomicNumber")
        if Z is None:
            self._show_error(f"Atomic number not found for '{sym}'."); return

        neutrons = mass_num - int(Z)
        if neutrons < 0:
            self._show_error("Mass number cannot be less than atomic number."); return

        # Isotope info if available
        isotope_info = None
        for iso in el.get("isotopes", []):
            if iso.get("mass_number") == mass_num or iso.get("massNumber") == mass_num:
                isotope_info = iso; break
        atomic_mass = (isotope_info.get("atomic_mass")
                       if isotope_info else el.get("atomic_mass") or el.get("AtomicMass"))
        abundance = (isotope_info.get("abundance") if isotope_info else None)
        abundance_str = f"{abundance:.3%}" if abundance is not None else "Unknown"

        result_html = (
            f"<b>Isotopic Notation:</b> {mass_num}<sub>{sym}</sub><br>"
            f"<b>Element:</b> {el.get('name','Unknown')} ({sym})<br>"
            f"<b>Atomic Number (Protons):</b> {Z}<br>"
            f"<b>Neutrons:</b> {neutrons}<br>"
            f"<b>Atomic Mass:</b> {float(atomic_mass):.5f} u<br>"
            f"<b>Natural Abundance:</b> {abundance_str}<br>"
        )

        # Pie chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        labels = ['Protons', 'Neutrons']
        sizes = [int(Z), neutrons]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal'); ax.set_title('Nucleon Composition')
        self.canvas.draw()

        img_path = export_figure(self.figure, out_dir=IMAGES_DIR) if IMAGES_DIR else export_figure(self.figure)
        self.last_img_path = img_path
        result_html += f'<br><i>Chart saved to:</i><br><small>{img_path}</small>'
        self.result.setHtml(result_html)
        add_log_entry("Isotopic Notation", action="Compute",
                      data={"symbol": sym, "A": mass_num, "Z": int(Z), "neutrons": neutrons, "img": str(img_path)})

    def _export_chart(self):
        if self.last_img_path:
            self.result.append(f"Already saved: {self.last_img_path}")
            return
        img_path = export_figure(self.figure, out_dir=IMAGES_DIR) if IMAGES_DIR else export_figure(self.figure)
        self.last_img_path = img_path
        self.result.append(f"Saved: {img_path}")

    def _show_error(self, msg):
        self.result.setHtml(f"<span style='color: red;'>{msg}</span>")
