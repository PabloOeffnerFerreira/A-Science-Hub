from __future__ import annotations
import math
import csv
from typing import Tuple, Optional

from PyQt6 import QtWidgets, QtCore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# Use the same logger import other tools use
# Adjust this path only if your other tools use a different exact module path
from core.data.functions.log import add_log_entry


class Tool(QtWidgets.QWidget):
    TITLE = "Lens/Mirror Equation"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Tool_LensMirror")
        outer = QtWidgets.QVBoxLayout(self)

        # Form
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        # Units map (meters base)
        self._UF = {"m": 1.0, "cm": 0.01, "mm": 0.001}

        # Focal length (prefilled)
        self.f = QtWidgets.QLineEdit()
        self.fu = QtWidgets.QComboBox(); self.fu.addItems(["m","cm","mm"]); self.fu.setCurrentText("m")
        self.f.setText("0.5")
        form.addRow("Focal length f:", self._row(self.f, self.fu))

        # Object distance (prefilled)
        self.do = QtWidgets.QLineEdit()
        self.dou = QtWidgets.QComboBox(); self.dou.addItems(["m","cm","mm"]); self.dou.setCurrentText("m")
        self.do.setText("2")
        form.addRow("Object distance do:", self._row(self.do, self.dou))

        # Image distance (blank so we solve for di by default; enables drag)
        self.di = QtWidgets.QLineEdit()
        self.diu = QtWidgets.QComboBox(); self.diu.addItems(["m","cm","mm"]); self.diu.setCurrentText("m")
        form.addRow("Image distance di:", self._row(self.di, self.diu))

        # Element selector (defines sign of f)
        self.kind = QtWidgets.QComboBox()
        self.kind.addItems(["Lens (Converging)", "Lens (Diverging)", "Mirror (Concave)", "Mirror (Convex)"])
        self.kind.setCurrentIndex(0)
        form.addRow("Element:", self.kind)

        # Toggles
        self.show_parallel_ray = QtWidgets.QCheckBox("Parallel ray");      self.show_parallel_ray.setChecked(True)
        self.show_center_ray   = QtWidgets.QCheckBox("Center/Chief ray");  self.show_center_ray.setChecked(True)
        self.show_focal_ray    = QtWidgets.QCheckBox("Focal ray (mirror)");self.show_focal_ray.setChecked(False)
        self.show_virtual_ext  = QtWidgets.QCheckBox("Virtual extensions"); self.show_virtual_ext.setChecked(True)
        self.show_two_f        = QtWidgets.QCheckBox("Show 2F");           self.show_two_f.setChecked(True)
        self.show_grid         = QtWidgets.QCheckBox("Grid");               self.show_grid.setChecked(True)
        toggles_layout = QtWidgets.QHBoxLayout()
        for w in (self.show_parallel_ray, self.show_center_ray, self.show_focal_ray,
                  self.show_virtual_ext, self.show_two_f, self.show_grid):
            toggles_layout.addWidget(w)
        form.addRow("Display:", toggles_layout)

        outer.addLayout(form)

        # Buttons
        btns = QtWidgets.QHBoxLayout()
        self.btn_calc = QtWidgets.QPushButton("Calculate")
        self.btn_clear = QtWidgets.QPushButton("Clear")
        self.btn_export_img = QtWidgets.QPushButton("Export Diagram…")
        self.btn_export_csv = QtWidgets.QPushButton("Export Values (CSV)")
        btns.addWidget(self.btn_calc); btns.addWidget(self.btn_clear)
        btns.addStretch(1)
        btns.addWidget(self.btn_export_img); btns.addWidget(self.btn_export_csv)
        outer.addLayout(btns)

        # Plot
        self.fig = Figure(figsize=(6, 4), constrained_layout=True)
        self.canvas = FigureCanvas(self.fig)
        outer.addWidget(self.canvas, stretch=1)

        # Result text
        self.result = QtWidgets.QLabel("")
        self.result.setWordWrap(True)
        outer.addWidget(self.result)

        # Signals
        self.btn_calc.clicked.connect(self._calc)
        self.btn_clear.clicked.connect(self._clear)
        self.btn_export_img.clicked.connect(self._export_image)
        self.btn_export_csv.clicked.connect(self._export_values_csv)
        for w in (self.kind, self.fu, self.dou, self.diu,
                  self.show_parallel_ray, self.show_center_ray, self.show_focal_ray,
                  self.show_virtual_ext, self.show_two_f, self.show_grid):
            if hasattr(w, "currentIndexChanged"):
                w.currentIndexChanged.connect(self._calc)
            else:
                w.stateChanged.connect(self._calc)

        # Drag interaction
        self._drag_active = False
        self._drag_tol_px = 12
        self._cid_press = self.canvas.mpl_connect("button_press_event", self._on_press)
        self._cid_move  = self.canvas.mpl_connect("motion_notify_event", self._on_move)
        self._cid_rel   = self.canvas.mpl_connect("button_release_event", self._on_release)

        # Initial compute
        self._calc()

    # UI helpers
    def _row(self, editor: QtWidgets.QWidget, unit_combo: QtWidgets.QComboBox):
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w); h.setContentsMargins(0,0,0,0)
        h.addWidget(editor, 1); h.addWidget(unit_combo, 0)
        return w

    # Units
    def _to_m(self, text: str, combo: QtWidgets.QComboBox) -> float:
        return float(text) * self._UF[combo.currentText()]

    def _from_m(self, meters: float, unit_label: str) -> float:
        return meters / self._UF[unit_label]

    # Kind and f sign
    def _read_kind(self) -> Tuple[bool, int, str]:
        k = self.kind.currentText()
        if "Lens" in k:
            is_mirror = False
            f_sign = +1 if "Converging" in k else -1
        else:
            is_mirror = True
            f_sign = +1 if "Concave" in k else -1
        return is_mirror, f_sign, k

    # Parse and solve
    def _parse_two_of_three(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        def get(line, combo):
            t = line.text().strip()
            return None if t == "" else self._to_m(t, combo)
        f = get(self.f, self.fu)
        do = get(self.do, self.dou)
        di = get(self.di, self.diu)
        if sum(x is not None for x in (f, do, di)) < 2:
            raise ValueError("Provide any two of f, do, di.")
        return f, do, di

    @staticmethod
    def _solve_third(f, do, di) -> Tuple[float, float, float]:
        # 1/f = 1/do + 1/di
        if f is None:
            if do == 0 or di == 0: raise ValueError("Zero distance.")
            f = 1.0 / (1.0/do + 1.0/di)
        elif do is None:
            if f == 0 or di == 0: raise ValueError("Zero distance.")
            denom = (1.0/f - 1.0/di)
            do = 1.0/denom if denom != 0 else float('inf')
        elif di is None:
            if f == 0 or do == 0: raise ValueError("Zero distance.")
            denom = (1.0/f - 1.0/do)
            di = 1.0/denom if denom != 0 else float('inf')
        return f, do, di

    @staticmethod
    def _classify(di: float, m: float) -> Tuple[str, str, str]:
        real_virtual = "real" if math.isfinite(di) and di > 0 else "virtual"
        orient = "upright" if m > 0 else "inverted"
        scale = "magnified" if abs(m) > 1 else ("reduced" if abs(m) < 1 else "same size")
        return real_virtual, orient, scale

    # Compute and render
    def _calc(self):
        try:
            is_mirror, f_sign, klabel = self._read_kind()

            f, do, di = self._parse_two_of_three()
            f, do, di = self._solve_third(f, do, di)

            # Enforce f sign from element type
            f = abs(f) * (1 if f_sign > 0 else -1)

            m = float('inf') if do == 0 else -di/do
            rv, orient, scale = self._classify(di, m)

            self._plot_ray_optics(f, do, di, is_mirror)

            # HUD
            ax = self.fig.axes[0] if self.fig.axes else None
            if ax is not None:
                self._draw_hud(ax, f, do, di, m, rv, orient, scale)
            self.canvas.draw()

            # Which value was solved?
            if self.f.text().strip() == "":
                solved_label, solved_val, solved_unit = "Focal length", self._from_m(f, self.fu.currentText()), self.fu.currentText()
            elif self.do.text().strip() == "":
                solved_label, solved_val, solved_unit = "Object distance", self._from_m(do, self.dou.currentText()), self.dou.currentText()
            else:
                solved_label, solved_val, solved_unit = "Image distance", self._from_m(di, self.diu.currentText()), self.diu.currentText()

            inf_note = "" if math.isfinite(di) else "\nImage at infinity (object at focus)."

            self.result.setText(
                f"{solved_label} = {solved_val:.4g} {solved_unit}\n"
                f"Magnification m = {m:.4g}\n"
                f"{klabel}; image is {rv}, {orient}, {scale}{inf_note}"
            )

            add_log_entry(self.TITLE, action="Calculate",
                          data={"f": f, "do": do, "di": di, "m": m, "type": klabel,
                                "classification": {"real_virtual": rv, "orientation": orient, "scale": scale}})

        except Exception as e:
            self.result.setText("Invalid input or singular configuration.")
            self.fig.clear(); self.canvas.draw()
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})

    # Plot
    def _plot_ray_optics(self, f: float, do: float, di: float, is_mirror: bool):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_title("Ray diagram")
        ax.grid(self.show_grid.isChecked(), alpha=0.25)
        ax.axhline(0, color="0.5", lw=1, ls="--")

        h0 = 1.0
        xiO = -do
        xiI = di
        hi = (-di/do) * h0 if (do != 0 and math.isfinite(di)) else float('inf')

        # Element
        ax.axvline(0, color="k", lw=2)
        ax.text(0, 0.12, "Mirror" if is_mirror else "Lens", ha="center", va="bottom")

        # F and 2F
        ax.plot([ f, -f], [0, 0], "bo", ms=5)
        ax.text( f, 0.05, "F", ha="center")
        ax.text(-f, 0.05, "F'", ha="center")
        if self.show_two_f.isChecked():
            for s in (2, -2):
                ax.plot([s*f], [0], "ko", ms=3)
                ax.text(s*f, -0.05, "2F" if s>0 else "2F'", ha="center", va="top", fontsize=8)

        # Mirror ticks for concave/convex cue
        if is_mirror:
            tick_side = -1 if f > 0 else +1
            for yy in np.linspace(-0.5, 0.5, 6):
                ax.plot([0, 0 + 0.04*tick_side], [yy, yy + 0.04], color="k", lw=1)

        # Object / Image
        ax.plot([xiO, xiO], [0, h0], color="g", lw=3, label="Object")
        if math.isfinite(xiI):
            ax.plot([xiI, xiI], [0, hi], color="r", lw=3, label="Image")
        else:
            ax.annotate("Image at ∞", xy=(0.95*max(1, abs(xiO), abs(f)), 0),
                        xytext=(0.6*max(1, abs(xiO), abs(f)), 0.3),
                        arrowprops=dict(arrowstyle="->"))

        # Rays
        if not is_mirror:
            if self.show_parallel_ray.isChecked():
                ax.plot([xiO, 0], [h0, h0], color="C0")
                if f != 0:
                    m1 = (0 - h0) / (f - 0)
                    x_end = xiI if math.isfinite(xiI) else max(2*abs(f), abs(xiO)) + 1.0
                    ax.plot([0, x_end], [h0, h0 + m1*(x_end - 0)], color="C0")
                    if self.show_virtual_ext.isChecked() and di < 0:
                        ax.plot([0, di], [h0, hi], color="C0", ls="--", alpha=0.7)
            if self.show_center_ray.isChecked():
                x_end = xiI if math.isfinite(xiI) else max(2*abs(f), abs(xiO)) + 1.0
                y_end = h0 + (x_end - xiO) * (0 - h0) / (0 - xiO)
                ax.plot([xiO, x_end], [h0, y_end], color="C1")
        else:
            if self.show_parallel_ray.isChecked():
                ax.plot([xiO, 0], [h0, h0], color="C0")
                if f != 0:
                    m1 = (0 - h0) / (f - 0)
                    x_far = xiO - 1.2*abs(do)
                    ax.plot([0, x_far], [h0, h0 + m1*(x_far - 0)], color="C0")
                    if self.show_virtual_ext.isChecked() and di < 0:
                        ax.plot([0, -di], [h0, -hi], color="C0", ls="--", alpha=0.7)
            if self.show_focal_ray.isChecked():
                if f != 0:
                    y_hit = h0 + (0 - xiO) * (0 - h0) / (f - xiO)
                    ax.plot([xiO, 0], [h0, y_hit], color="C2")
                    x_far = xiO - 1.2*abs(do)
                    ax.plot([0, x_far], [y_hit, y_hit], color="C2")
            if self.show_center_ray.isChecked():
                ax.plot([xiO, 0], [h0, h0], color="C1", ls=":")
                ax.plot([0, xiO - 1.2*abs(do)], [h0, h0], color="C1", ls=":")

        # Limits
        xs = [xiO, 0, f, -f, 2*f, -2*f]
        if math.isfinite(xiI): xs.append(xiI)
        span = max(1.0, 1.2*max(abs(v) for v in xs))
        ax.set_xlim(-span, span)
        ax.set_ylim(-0.75*span, 0.75*span)
        ax.legend(loc="upper right", fontsize=8)

    # HUD
    def _draw_hud(self, ax, f, do, di, m, rv, orient, scale):
        txt = (f"f = {f:.4g} m\n"
               f"do = {do:.4g} m\n"
               f"di = {di:.4g} m\n"
               f"m = {m:.4g}\n"
               f"{rv}, {orient}, {scale}")
        ax.text(0.02, 0.98, txt, transform=ax.transAxes,
                ha="left", va="top", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.5", alpha=0.85))

    # Dragging
    def _drag_condition(self) -> bool:
        return (self.di.text().strip() == "" and
                self.f.text().strip() != "" and
                self.do.text().strip() != "")

    def _current_object_xy(self) -> Tuple[Optional[float], Optional[float]]:
        try:
            f, do, di = self._parse_two_of_three()
            f, do, di = self._solve_third(f, do, di)
            return -do, 1.0
        except Exception:
            return None, None

    def _pix_dist(self, ax, x, y, event) -> float:
        px, py = ax.transData.transform((x, y))
        return math.hypot(px - event.x, py - event.y)

    def _on_press(self, event):
        if event.inaxes is None or not self._drag_condition():
            return
        x, y = self._current_object_xy()
        if x is None:
            return
        if self._pix_dist(event.inaxes, x, y, event) <= self._drag_tol_px:
            self._drag_active = True

    def _on_move(self, event):
        if not self._drag_active or event.inaxes is None or event.xdata is None:
            return
        new_do_m = max(1e-6, -float(event.xdata))  # object at x = -do
        try:
            unit = self.dou.currentText()
            self.do.setText(str(self._from_m(new_do_m, unit)))
            self._calc()
        except Exception:
            pass

    def _on_release(self, event):
        self._drag_active = False

    # Exports/clear
    def _export_image(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Diagram", "ray_diagram.png",
                                                        "PNG (*.png);;SVG (*.svg);;PDF (*.pdf)")
        if not path: return
        try:
            self.fig.savefig(path, dpi=200)
        except Exception:
            QtWidgets.QMessageBox.warning(self, "Export failed", "Could not save the diagram.")

    def _export_values_csv(self):
        try:
            is_mirror, f_sign, klabel = self._read_kind()
            f, do, di = self._parse_two_of_three()
            f, do, di = self._solve_third(f, do, di)
            f = abs(f) * (1 if f_sign > 0 else -1)
            m = float('inf') if do == 0 else -di/do
            rv, orient, scale = self._classify(di, m)

            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "optics_values.csv", "CSV Files (*.csv)")
            if not path: return
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["element", "f_m", "do_m", "di_m", "m", "image_real_virtual", "orientation", "scale"])
                w.writerow([klabel, f, do, di, m, rv, orient, scale])
        except Exception:
            QtWidgets.QMessageBox.warning(self, "Export failed", "Could not export current values.")

    def _clear(self):
        self.f.clear(); self.do.clear(); self.di.clear()
        self.f.setText("0.5"); self.do.setText("2")
        self.result.clear()
        self.fig.clear(); self.canvas.draw()