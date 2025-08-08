from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class SimpleToolsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Helper to create placeholder sections
        def placeholder(title, min_height=60):
            lbl = QLabel(title)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFrameShape(QFrame.Shape.Box)
            lbl.setMinimumHeight(min_height)
            return lbl

        # Sections (in planned order)
        layout.addWidget(placeholder("Welcome Section", min_height=80))
        layout.addWidget(placeholder("Simple Calculator", min_height=120))
        layout.addWidget(placeholder("Unit Converter", min_height=160))
        layout.addWidget(placeholder("Scientific Notation ↔ Decimal Converter"))
        layout.addWidget(placeholder("Significant Figures Tool"))
        layout.addWidget(placeholder("Logarithmic Calculator"))
        layout.addWidget(placeholder("Scientific Constants Lookup"))
        layout.addWidget(placeholder("Dimensional Equation Checker"))
        layout.addWidget(placeholder("SI Prefix Combiner/Splitter"))
        layout.addWidget(placeholder("Decimal Time Converter"))
        layout.addWidget(placeholder("Physical Quantity Explainer (EU/UK/US/BR)"))
        layout.addWidget(placeholder("Drag & Drop Import Area", min_height=120))

        # Optional: stretch so the last items don't get squashed
        for i in range(layout.count()):
            layout.setStretch(i, 1)