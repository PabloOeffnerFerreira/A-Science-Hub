from core.data.units.conversion_data import conversion_data
from core.data.units.si_prefixes import si_prefixes

class UnitConverter:
    def __init__(self):
        self.data = conversion_data
        self.categories = list(self.data.keys())

    def get_units_for_category(self, category):
        if category in self.data:
            return list(self.data[category]["units"].keys())
        return []

    def get_si_units_for_category(self, category):
        """Return SI base units for this category"""
        if category in self.data and "SI" in self.data[category]:
            return self.data[category]["SI"]
        return []

    def convert(self, value, from_unit, to_unit, category):
        """Convert between two units in the same category"""
        if category not in self.data:
            raise ValueError(f"Unknown category: {category}")

        cat_data = self.data[category]["units"]

        if from_unit not in cat_data or to_unit not in cat_data:
            raise ValueError(f"Units not found in category {category}")

        # Convert to base unit
        base_value = value * cat_data[from_unit]
        # Convert to target
        return base_value / cat_data[to_unit]