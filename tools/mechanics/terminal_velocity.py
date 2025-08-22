import math

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from core.data.functions.log import add_log_entry
from core.data.functions.image_export import export_figure
from core.data.paths import IMAGES_DIR


class Tool(QDialog):
    TITLE = "Terminal Velocity"  # your loader uses this alongside setWindowTitle

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)

        # Mass
        row_mass = QHBoxLayout()
        row_mass.addWidget(QLabel("Mass:"))
        self.mass_edit = QLineEdit("1.0")
        self.mass_unit = QComboBox()
        self.mass_unit.addItems(["kg", "lb"])
        row_mass.addWidget(self.mass_edit)
        row_mass.addWidget(self.mass_unit)
        layout.addLayout(row_mass)

        # Area
        row_area = QHBoxLayout()
        row_area.addWidget(QLabel("Cross-sectional Area:"))
        self.area_edit = QLineEdit("0.5")
        self.area_unit = QComboBox()
        self.area_unit.addItems(["m²", "cm²", "in²"])
        row_area.addWidget(self.area_edit)
        row_area.addWidget(self.area_unit)
        layout.addLayout(row_area)

        # Height
        row_height = QHBoxLayout()
        row_height.addWidget(QLabel("Height:"))
        self.height_edit = QLineEdit("100")
        self.height_unit = QComboBox()
        self.height_unit.addItems(["m", "ft"])
        row_height.addWidget(self.height_edit)
        row_height.addWidget(self.height_unit)
        layout.addLayout(row_height)

        # Air density / altitude
        row_air = QHBoxLayout()
        row_air.addWidget(QLabel("Air Density (kg/m³) or Altitude (m):"))
        self.air_mode = QComboBox()
        self.air_mode.addItems(["Air Density", "Altitude", "Custom"])
        self.air_value = QLineEdit("1.225")
        row_air.addWidget(self.air_mode)
        row_air.addWidget(self.air_value)
        layout.addLayout(row_air)

        # Drag coefficient
        row_cd = QHBoxLayout()
        row_cd.addWidget(QLabel("Drag Coefficient:"))
        self.cd_preset = QComboBox()
        self.cd_preset.addItems([
            "Sphere (0.47)",
            "Flat Plate (1.28)",
            "Cylinder (1.2)",
            "Streamlined Body (0.04)",
            "Custom",
        ])
        self.cd_edit = QLineEdit("1.0")
        row_cd.addWidget(self.cd_preset)
        row_cd.addWidget(self.cd_edit)
        layout.addLayout(row_cd)

        # Result + button
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)
        btn_calc = QPushButton("Calculate")
        btn_calc.clicked.connect(self.calculate)
        layout.addWidget(btn_calc)

        # Plot
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Signals
        self.air_mode.currentTextChanged.connect(self._update_air_mode)
        self.cd_preset.currentTextChanged.connect(self._update_cd_preset)
        self._update_air_mode()
        self._update_cd_preset()

    def _update_air_mode(self):
        mode = self.air_mode.currentText()
        if mode == "Air Density":
            self.air_value.setText("1.225")
            self.air_value.setEnabled(False)
        elif mode == "Altitude":
            self.air_value.setText("0")
            self.air_value.setEnabled(True)
        else:
            self.air_value.setEnabled(True)

    def _update_cd_preset(self):
        preset = self.cd_preset.currentText()
        mapping = {
            "Sphere (0.47)": "0.47",
            "Flat Plate (1.28)": "1.28",
            "Cylinder (1.2)": "1.2",
            "Streamlined Body (0.04)": "0.04",
        }
        if preset in mapping:
            self.cd_edit.setText(mapping[preset])
            self.cd_edit.setEnabled(False)
        else:
            self.cd_edit.setEnabled(True)

    def _rho_from_altitude(self, h_m: float) -> float:
        if h_m < 0:
            h_m = 0
        if h_m < 11000:
            T0 = 288.15
            L = 0.0065
            p0 = 101325.0
            R = 8.31447
            M = 0.0289644
            g = 9.80665
            T = T0 - L * h_m
            p = p0 * (T / T0) ** (g * M / (R * L))
            rho = p * M / (R * T)
        else:
            rho = 0.364
        return rho

    def calculate(self):
        try:
            # Inputs to SI
            mass = float(self.mass_edit.text())
            if self.mass_unit.currentText() == "lb":
                mass *= 0.45359237

            area = float(self.area_edit.text())
            aunit = self.area_unit.currentText()
            if aunit == "cm²":
                area *= 1e-4
            elif aunit == "in²":
                area *= 0.00064516

            height = float(self.height_edit.text())
            if self.height_unit.currentText() == "ft":
                height *= 0.3048

            mode = self.air_mode.currentText()
            aval = float(self.air_value.text())
            if mode == "Altitude":
                rho = self._rho_from_altitude(aval)
            elif mode == "Air Density":
                rho = 1.225
            else:
                rho = aval

            Cd = float(self.cd_edit.text())
            g = 9.81

            # Terminal velocity
            v_terminal = math.sqrt((2 * mass * g) / (rho * area * Cd))

            # Simple Euler integration
            dt = 0.01
            v = 0.0
            y = height
            t = 0.0
            times, velocities = [], []
            while y > 0.0:
                Fg = mass * g
                Fd = 0.5 * rho * v * v * Cd * area
                a = (Fg - Fd) / mass if v >= 0 else (Fg + Fd) / mass
                v += a * dt
                y -= max(v, 0.0) * dt
                t += dt
                times.append(t)
                velocities.append(v)
                if t > 36000:
                    break

            msg = (
                f"Terminal Velocity ≈ {v_terminal:.2f} m/s\n"
                f"Fall Time with drag ≈ {t:.2f} s\n"
                f"Fall Time without drag ≈ {math.sqrt(2 * max(height,0.0) / g):.2f} s"
            )
            self.result_label.setText(msg)

            # Plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(times, velocities)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Velocity (m/s)")
            ax.set_title("Velocity vs Time")
            ax.grid(True)
            self.canvas.draw()

            # Save figure to central images dir
            img_path = export_figure(self.figure, out_dir=IMAGES_DIR)

            # Log
            add_log_entry(
                "Terminal Velocity",
                action="Compute",
                data={
                    "inputs": {
                        "mass_kg": mass,
                        "area_m2": area,
                        "height_m": height,
                        "Cd": Cd,
                        "rho": rho,
                    },
                    "results": {
                        "v_terminal_m_s": v_terminal,
                        "fall_time_s": t,
                        "plot": str(img_path),
                    },
                },
                tags=["physics", "mechanics", "drag"],
            )

            self.result_label.setText(msg + f"\nPlot saved to {img_path}")

        except Exception:
            self.result_label.setText("Please enter valid numbers.")
            add_log_entry("Terminal Velocity", action="invalid_input")
