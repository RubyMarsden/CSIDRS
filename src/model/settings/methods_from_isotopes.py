from src.model.ratio import Ratio
from src.model.isotopes import Isotope

# Sulphur ratios
S33_S32 = Ratio(Isotope.S33, Isotope.S32)
S34_S32 = Ratio(Isotope.S34, Isotope.S32)
S36_S32 = Ratio(Isotope.S36, Isotope.S32)

# Oxygen ratios
O17_O16 = Ratio(Isotope.O17, Isotope.O16)
O18_O16 = Ratio(Isotope.O18, Isotope.O16)
O16H1_O16 = Ratio(Isotope.HYD, Isotope.O16)

three_isotopes_sulphur = {
    "isotopes": [Isotope.S32, Isotope.S33, Isotope.S34],
    "number_of_ratios": 2,
    "ratios": [S33_S32, S34_S32]
}

four_isotopes_sulphur = {
    "isotopes": [Isotope.S32, Isotope.S33, Isotope.S34, Isotope.S36],
    "number_of_ratios": 3,
    "ratios": [S33_S32, S34_S32, S36_S32]
}

two_isotopes_no_hydroxide_oxygen = {
    "isotopes": [Isotope.O16, Isotope.O18],
    "number_of_ratios": 1,
    "ratios": [O18_O16]
}

three_isotopes_no_hydroxide_oxygen = {
    "isotopes": [Isotope.O16, Isotope.O17, Isotope.O18],
    "number_of_ratios": 2,
    "ratios": [O17_O16, O18_O16]
}

two_isotopes_hydroxide_oxygen = {
    "isotopes": [Isotope.O16, Isotope.O18, Isotope.HYD],
    "number_of_ratios": 2,
    "ratios": [O18_O16, O16H1_O16]
}

three_isotopes_hydroxide_oxygen = {
    "isotopes": [Isotope.O16, Isotope.O17, Isotope.O18, Isotope.HYD],
    "number_of_ratios": 3,
    "ratios": [O17_O16, O18_O16, O16H1_O16]
}

list_of_method_dictionaries = [three_isotopes_sulphur,
                               four_isotopes_sulphur,
                               two_isotopes_hydroxide_oxygen,
                               two_isotopes_no_hydroxide_oxygen,
                               three_isotopes_hydroxide_oxygen,
                               three_isotopes_no_hydroxide_oxygen
                               ]
