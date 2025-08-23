from __future__ import annotations
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from core.data.functions.log import add_log_entry

b = 2.897771955e-3  # m·K

class Tool(QDialog):
    TITLE = "Blackbody Peak (Wien's Law)"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(640)
        lay = QVBoxLayout(self)

        r0 = QHBoxLayout()
        r0.addWidget(QLabel("Mode:")); self.mode = QComboBox(); self.mode.addItems(["T → λ_peak", "λ_peak → T"])
        r0.addWidget(self.mode); lay.addLayout(r0)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("T (K) or λ_peak (nm):")); self.x = QLineEdit("5778"); r1.addWidget(self.x)
        lay.addLayout(r1)

        self.result = QLabel(""); lay.addWidget(self.result)
        btn = QPushButton("Compute"); lay.addWidget(btn); btn.clicked.connect(self._go)

    def _go(self):
        try:
            mode = self.mode.currentText()
            x = float(self.x.text())
            if mode == "T → λ_peak":
                T = x
                if T <= 0: raise ValueError("T>0")
                lam = (b/T)*1e9
                self.result.setText(f"λ_peak ≈ {lam:.6g} nm")
                data = {"T": T, "lambda_peak_nm": lam}
            else:
                lam_nm = x
                if lam_nm <= 0: raise ValueError("λ>0")
                T = (b/(lam_nm*1e-9))
                self.result.setText(f"T ≈ {T:.6g} K")
                data = {"lambda_peak_nm": lam_nm, "T": T}
            add_log_entry(self.TITLE, action="Compute", data=data)
        except Exception as e:
            self.result.setText("Invalid input.")
            add_log_entry(self.TITLE, action="Error", data={"msg": str(e)})
