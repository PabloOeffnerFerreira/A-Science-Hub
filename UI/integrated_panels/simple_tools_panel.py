from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from UI.integrated_panels.unit_converter_panel import UnitConverterWidget
from UI.integrated_panels.notation_converter_panel import NotationConverterWidget
from UI.integrated_panels.calculator_panel import SimpleCalculatorWidget
from UI.integrated_panels.dec_time_conv_panel import DecimalTimeConverterWidget
from UI.integrated_panels.si_prefix_combiner_splitter_panel import SiPrefixCombinerSplitter
from UI.integrated_panels.sig_fig_panel import SignificantFiguresWidget
from UI.integrated_panels.sci_cons_lookup_panel import ScientificConstantsLookupWidget
from UI.integrated_panels.dim_eq_checker_panel import DimensionalEquationChecker

def placeholder(title: str, min_height: int | None = None) -> QWidget:
    w = QFrame()
    w.setFrameShape(QFrame.Shape.StyledPanel)
    w.setFrameShadow(QFrame.Shadow.Plain)
    lay = QVBoxLayout(w)
    lay.setContentsMargins(10, 8, 10, 8)
    lay.setSpacing(4)
    lbl = QLabel(title)
    lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
    lay.addWidget(lbl)
    if min_height:
        w.setMinimumHeight(min_height)
    return w


class SimpleToolsPanel(QWidget):
    """Simple tools container"""
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(placeholder("Welcome Section", min_height=80), 0, Qt.AlignmentFlag.AlignTop)
        

        uc_nc_layout = QHBoxLayout()
        uc_nc_layout.setContentsMargins(0, 0, 0, 0)
        uc_nc_layout.setSpacing(10)
        uc_nc_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        uc_nc_layout.addWidget(UnitConverterWidget(), 0, Qt.AlignmentFlag.AlignTop)
        uc_nc_layout.addWidget(NotationConverterWidget(), 0, Qt.AlignmentFlag.AlignTop)
        uc_nc_layout.addWidget(DecimalTimeConverterWidget(), 0, Qt.AlignmentFlag.AlignTop)
        uc_row = QFrame()
        uc_row.setFrameShape(QFrame.Shape.NoFrame)
        uc_row.setLayout(uc_nc_layout)
        layout.addWidget(uc_row, 0, Qt.AlignmentFlag.AlignTop)
        sipcs_row = QHBoxLayout()
        sipcs_row.setContentsMargins(0, 0, 0, 0)
        sipcs_row.setSpacing(10)
        sipcs_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        sipcs = SiPrefixCombinerSplitter()
        sipcs_row.addWidget(sipcs)
        sipcs_row.addWidget(SignificantFiguresWidget(), 0, Qt.AlignmentFlag.AlignTop)
        sipcs_row.addWidget(ScientificConstantsLookupWidget(), 0, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(sipcs_row)

        dec_row = QHBoxLayout()
        dec_row.setContentsMargins(0, 0, 0, 0)
        dec_row.setSpacing(10)
        dec_row.setAlignment(Qt.AlignmentFlag.AlignTop)


        dec = DimensionalEquationChecker()
        dec_row.addWidget(dec)
        dec_row.addWidget(SimpleCalculatorWidget(), 0, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(dec_row)

        #layout.addWidget(placeholder("Physical Quantity Explainer (EU/UK/US/BR)"), 0, Qt.AlignmentFlag.AlignTop)
        #layout.addWidget(placeholder("Drag & Drop Import Area", min_height=120), 0, Qt.AlignmentFlag.AlignTop)