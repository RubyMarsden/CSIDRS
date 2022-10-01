from enum import Enum

from model.elements import Element


class Isotope(Enum):
    C12 = "12C"
    C13 = "13C"
    C14 = "14C"
    O16 = "16O"
    O17 = "17O"
    O18 = "18O"
    O16H1 = "16O 1H"
    S32 = "32S"
    S33 = "33S"
    S34 = "34S"
    S36 = "36S"
    F19 = "19F"
    Cl35 = "35Cl"
    Cl37 = "37Cl"


isotopes_by_element = {
    Element.CAR: [Isotope.C12, Isotope.C13, Isotope.C14],
    Element.OXY: [Isotope.O16, Isotope.O17, Isotope.O18, Isotope.O16H1],
    Element.SUL: [Isotope.S32, Isotope.S33, Isotope.S34, Isotope.S36],
    Element.CHL: [Isotope.Cl35, Isotope.Cl37, Isotope.F19]
}
