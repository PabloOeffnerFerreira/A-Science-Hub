
from __future__ import annotations
import math
import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Projectile Motion"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        # Inputs
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Initial speed:"))
        self.v = QLineEdit("20")
        self.vu = QComboBox(); self.vu.addItems(["m/s","km/h","mph"])
        r1.addWidget(self.v); r1.addWidget(self.vu)
        lay.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Angle:"))
        self.theta = QLineEdit("45")
        self.tu = QComboBox(); self.tu.addItems(["degrees","radians"])
        r2.addWidget(self.theta); r2.addWidget(self.tu)
        lay.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Initial height:"))
        self.h0 = QLineEdit("0")
        self.hu = QComboBox(); self.hu.addItems(["m","ft"])
        r3.addWidget(self.h0); r3.addWidget(self.hu)
        lay.addLayout(r3)

        self.result = QLabel("")
        lay.addWidget(self.result)

        # Figure
        self.fig = Figure(figsize=(6,4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas, 1)

        # Buttons
        b = QHBoxLayout()
        self.btn_calc = QPushButton("Calculate"); b.addWidget(self.btn_calc)
        self.btn_export = QPushButton("Export Image…"); b.addWidget(self.btn_export)
        lay.addLayout(b)

        self.btn_calc.clicked.connect(self._calc)
        self.btn_export.clicked.connect(lambda: export_figure(self.fig))

    def _calc(self):
        try:
            v = float(self.v.text()); th = float(self.theta.text()); h = float(self.h0.text())
            if self.vu.currentText()=="km/h": v /= 3.6
            elif self.vu.currentText()=="mph": v *= 0.44704
            if self.tu.currentText()=="degrees": th = math.radians(th)
            if self.hu.currentText()=="ft": h *= 0.3048

            g = 9.81
            a = -0.5*g; b = v*math.sin(th); c = h
            disc = b*b - 4*a*c
            if disc < 0: 
                self.result.setText("No real impact (check inputs).")
                self.fig.clear(); self.canvas.draw()
                return
            t1 = (-b + math.sqrt(disc)) / (2*a)
            t2 = (-b - math.sqrt(disc)) / (2*a)
            T = max(t1,t2)
            R = v*math.cos(th)*T
            Hmax = h + (v**2)*(math.sin(th)**2)/(2*g)
            vx = v*math.cos(th)
            vy = v*math.sin(th) - g*T
            vimp = math.sqrt(vx*vx + vy*vy)

            xs = np.linspace(0, R, 600)
            ys = h + xs*math.tan(th) - (g*xs*xs)/(2*(v*math.cos(th))**2)
            ys = np.maximum(ys, 0)

            self.fig.clear(); ax = self.fig.add_subplot(111)
            ax.plot(xs, ys); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)"); ax.grid(True, alpha=0.3)
            self.fig.tight_layout(); self.canvas.draw()

            msg = (f"Range = {R:.3f} m | Flight time = {T:.3f} s | Max height = {Hmax:.3f} m\n"
                   f"Impact speed = {vimp:.3f} m/s (vx={vx:.3f}, vy={vy:.3f})")
            self.result.setText(msg)
            add_log_entry(self.TITLE, action="Calculate", data={"v": v, "theta_rad": th, "h": h, "R": R, "T": T, "Hmax": Hmax, "vimp": vimp})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
