from PyQt6.QtWidgets import QWidget, QGridLayout, QSizePolicy
from UI.integrated_panels.unit_converter_panel import UnitConverterWidget
from UI.integrated_panels.notation_converter_panel import NotationConverterWidget
from UI.integrated_panels.calculator_panel import SimpleCalculatorWidget
from UI.integrated_panels.dec_time_conv_panel import DecimalTimeConverterWidget
from UI.integrated_panels.si_prefix_combiner_splitter_panel import SiPrefixCombinerSplitter
from UI.integrated_panels.sig_fig_panel import SignificantFiguresWidget
from UI.integrated_panels.sci_cons_lookup_panel import ScientificConstantsLookupWidget
from UI.integrated_panels.dim_eq_checker_panel import DimensionalEquationChecker
from UI.integrated_panels.quantity_checker_panel import ScientificQuantityChecker
from UI.integrated_panels.welcome_panel import WelcomePanel
from UI.common.titled_card import TitledCard
from UI.common.layout_helpers import cap_to_sizehint

def _card(title, child, expand_vertical=False, cap_scale=1.05, cap_extra=8):
    c = TitledCard(title, child)
    if expand_vertical:
        c.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    else:
        c.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        cap_to_sizehint(c, cap_scale, cap_extra)
    return c

class SimpleToolsPanel(QWidget):
    def __init__(self):
        super().__init__()
        grid = QGridLayout(self)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        grid.addWidget(_card("Welcome", WelcomePanel(), expand_vertical=True), 0, 0, 1, 3)

        grid.addWidget(_card("Unit Converter", UnitConverterWidget(), False, 1.02, 6), 1, 0, 1, 1)
        grid.addWidget(_card("Notation Converter", NotationConverterWidget(), False, 1.02, 6), 1, 1, 1, 1)
        grid.addWidget(_card("Decimal Time Converter", DecimalTimeConverterWidget(), False, 1.02, 6), 1, 2, 1, 1)

        grid.addWidget(_card("SI Prefix Combiner/Splitter", SiPrefixCombinerSplitter()), 2, 0, 1, 1)
        grid.addWidget(_card("Significant Figures", SignificantFiguresWidget()), 2, 1, 1, 1)
        grid.addWidget(_card("Scientific Constants", ScientificConstantsLookupWidget()), 2, 2, 1, 1)

        grid.addWidget(_card("Dimensional Equation Checker", DimensionalEquationChecker()), 3, 0, 1, 1)
        grid.addWidget(_card("Simple Calculator", SimpleCalculatorWidget()), 3, 1, 1, 1)
        grid.addWidget(_card("Quantity Checker", ScientificQuantityChecker()), 3, 2, 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setRowStretch(0, 6)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(3, 1)
