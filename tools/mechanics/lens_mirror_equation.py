
from __future__ import annotations
import math
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from core.data.functions.image_export import export_figure
from core.data.functions.log import add_log_entry

class Tool(QDialog):
    TITLE = "Lens & Mirror Equation"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        units = ["m","cm","mm","in","ft"]
        def row(lbl, default=""):
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); e = QLineEdit(default); u = QComboBox(); u.addItems(units); r.addWidget(e); r.addWidget(u); lay.addLayout(r); return e,u
        self.f, self.fu = row("Focal length f:", "0.1")
        self.do, self.dou = row("Object distance d₀:", "0.5")
        self.di, self.diu = row("Image distance dᵢ:", "")

        self.mirror = QCheckBox("Mirror (tick for mirror, untick for lens)"); lay.addWidget(self.mirror)

        self.result = QLabel(""); lay.addWidget(self.result)

        self.fig = Figure(figsize=(6,4), dpi=100)
        self.canvas = FigureCanvas(self.fig); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(NavigationToolbar(self.canvas, self)); lay.addWidget(self.canvas, 1)

        b = QHBoxLayout()
        self.btn_calc = QPushButton("Calculate"); b.addWidget(self.btn_calc)
        self.btn_export = QPushButton("Export Diagram…"); b.addWidget(self.btn_export)
        lay.addLayout(b)

        self.btn_calc.clicked.connect(self._calc)
        self.btn_export.clicked.connect(lambda: export_figure(self.fig))

    @staticmethod
    def _to_m(val: float, unit: str) -> float:
        if unit=="cm": return val*0.01
        if unit=="mm": return val*0.001
        if unit=="in": return val*0.0254
        if unit=="ft": return val*0.3048
        return val

    @staticmethod
    def _from_m(val: float, unit: str) -> float:
        if unit=="cm": return val/0.01
        if unit=="mm": return val/0.001
        if unit=="in": return val/0.0254
        if unit=="ft": return val/0.3048
        return val

    def _calc(self):
        try:
            def parse(e,u):
                t = e.text().strip()
                return (None if t=="" else self._to_m(float(t), u.currentText()))
            f = parse(self.f, self.fu)
            d0 = parse(self.do, self.dou)
            di = parse(self.di, self.diu)

            if sum(x is not None for x in (f,d0,di)) != 2:
                self.result.setText("Fill exactly two fields."); return

            # mirror convention: make f negative for converging mirror
            if self.mirror.isChecked() and f is not None:
                f = -abs(f)

            if f is None:
                f = 1.0/(1.0/d0 + 1.0/di)
                out = self._from_m(f, self.fu.currentText()); label="Focal length"; unit=self.fu.currentText()
            elif d0 is None:
                d0 = 1.0/(1.0/f - 1.0/di)
                out = self._from_m(d0, self.dou.currentText()); label="Object distance"; unit=self.dou.currentText()
            else:
                di = 1.0/(1.0/f - 1.0/d0)
                out = self._from_m(di, self.diu.currentText()); label="Image distance"; unit=self.diu.currentText()

            magn = -di/d0 if (d0 and di) else float("inf")
            typ = ("Mirror" if self.mirror.isChecked() else "Lens") + (" (Converging)" if f>0 else " (Diverging)")

            self._plot_ray(f, d0 or 0.0, di or 0.0)

            self.result.setText(f"{label} = {out:.4g} {unit}\nMagnification = {magn:.4g}\nType: {typ}")
            add_log_entry(self.TITLE, action="Calculate", data={"f": f, "d0": d0, "di": di, "magn": magn, "type": typ})
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})

    def _plot_ray(self, f: float, d0: float, di: float):
        self.fig.clear(); ax = self.fig.add_subplot(111)
        ax.set_title("Ray diagram"); ax.grid(True, alpha=0.3)
        ax.axhline(0, color="grey", linestyle="--"); ax.axvline(0, color="black")
        M = max(abs(x) for x in (f, d0, di, 1.0)) * 1.6
        ax.set_xlim(-0.6*M, M); ax.set_ylim(-0.6*M, 0.6*M)

        # object at -d0, height 1
        h0 = 1.0
        ax.plot([-d0, -d0], [0, h0], "g", lw=3, label="Object")
        # image at +di
        hi = -di/d0 * h0 if d0!=0 else 0.0
        ax.plot([di, di], [0, hi], "r", lw=3, label="Image")

        # focal points
        ax.plot([f], [0], "bo"); ax.plot([-f], [0], "bo")

        # principal rays (simplified)
        ax.plot([-d0, 0], [h0, h0], "b")
        ax.plot([0, di], [h0, 0], "b")
        ax.plot([-d0, di], [h0, hi], "m")

        ax.legend(loc="upper right")
        self.fig.tight_layout(); self.canvas.draw()
