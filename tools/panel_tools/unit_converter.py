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
        if category in self.data and "SI" in self.data[category]:
            return self.data[category]["SI"]
        return []

    def convert(self, value, from_unit, to_unit, category):
        if category not in self.data:
            raise ValueError(f"Unknown category: {category}")

        if category == "Temperature":
            return self._convert_temperature(value, from_unit, to_unit)

        cat_data = self.data[category]["units"]
        if from_unit not in cat_data or to_unit not in cat_data:
            raise ValueError(f"Units not found in category {category}")

        base_value = value * cat_data[from_unit]
        return base_value / cat_data[to_unit]

    def _convert_temperature(self, v, fu, tu):
        fu = fu.strip()
        tu = tu.strip()

        if fu == "K":
            K = v
        elif fu == "C":
            K = v + 273.15
        elif fu == "F":
            K = (v - 32.0) * (5.0/9.0) + 273.15
        else:
            raise ValueError(f"Unsupported temperature unit: {fu}")

        if tu == "K":
            return K
        elif tu == "C":
            return K - 273.15
        elif tu == "F":
            return (K - 273.15) * (9.0/5.0) + 32.0
        else:
            raise ValueError(f"Unsupported temperature unit: {tu}")
