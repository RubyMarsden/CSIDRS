from enum import Enum

from model.elements import Element


class Isotope(Enum):
    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, isotope_name, usage_in_secondary_ion_calculations):
        self.isotope_name = isotope_name
        self.usage_in_secondary_ion_calculations = usage_in_secondary_ion_calculations

    C12 = "12C", True
    C13 = "13C", True
    C14 = "14C", True
    O16 = "16O", True
    O17 = "17O", True
    O18 = "18O", True
    O16H1 = "16O 1H", False
    S32 = "32S", True
    S33 = "33S", True
    S34 = "34S", True
    S36 = "36S", True
    F19 = "19F", False
    Cl35 = "35Cl", True
    Cl37 = "37Cl", True


isotopes_by_element = {
    Element.CAR: [Isotope.C12, Isotope.C13, Isotope.C14],
    Element.OXY: [Isotope.O16, Isotope.O17, Isotope.O18, Isotope.O16H1],
    Element.SUL: [Isotope.S32, Isotope.S33, Isotope.S34, Isotope.S36],
    Element.CHL: [Isotope.Cl35, Isotope.Cl37, Isotope.F19]
}
