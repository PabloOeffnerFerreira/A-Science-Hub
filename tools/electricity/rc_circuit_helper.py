
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "RC Circuit Helper"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(760)
        lay = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("R (Ω):")); self.R = QLineEdit("1000"); row.addWidget(self.R)
        row.addWidget(QLabel("C (F):")); self.C = QLineEdit("0.00047"); row.addWidget(self.C)
        row.addWidget(QLabel("V_in (V):")); self.Vin = QLineEdit("5.0"); row.addWidget(self.Vin)
        self.mode = QComboBox(); self.mode.addItems(["Charging", "Discharging"]); row.addWidget(self.mode)
        lay.addLayout(row)

        rng = QHBoxLayout()
        self.tmax = QLineEdit("2.0"); rng.addWidget(QLabel("t_max (s):")); rng.addWidget(self.tmax)
        lay.addLayout(rng)

        b = QHBoxLayout(); self.btn_plot = QPushButton("Plot"); b.addWidget(self.btn_plot); self.btn_export = QPushButton("Export Image…"); b.addWidget(self.btn_export); lay.addLayout(b)

        self.fig = Figure(figsize=(7.2, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig); lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas, 1)

        self.btn_plot.clicked.connect(self._plot)
        self.btn_export.clicked.connect(lambda: export_figure(self.fig))

    def _plot(self):
        try:
            R = float(self.R.text()); C = float(self.C.text()); Vin = float(self.Vin.text()); tmax = float(self.tmax.text())
            tau = R*C
            t = np.linspace(0, tmax, 600)
            if self.mode.currentText() == "Charging":
                V = Vin * (1 - np.exp(-t/tau))
                title = f"Charging: τ = R·C = {tau:.3g} s"
            else:
                V0 = Vin
                V = V0 * np.exp(-t/tau)
                title = f"Discharging: τ = R·C = {tau:.3g} s"
            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.plot(t, V); ax.set_xlabel("t (s)"); ax.set_ylabel("V (V)"); ax.set_title(title); ax.grid(True, alpha=0.3)
            self.fig.tight_layout(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Plot", data={"R": R, "C": C, "Vin": Vin, "mode": self.mode.currentText(), "tmax": tmax, "tau": tau})
        except Exception as e:
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
