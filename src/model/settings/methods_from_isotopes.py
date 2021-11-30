from src.model.ratio import Ratio
from src.model.isotopes import Isotope
from src.model.method import Method

# Sulphur ratios
S33_S32 = Ratio(Isotope.S33, Isotope.S32)
S34_S32 = Ratio(Isotope.S34, Isotope.S32)
S36_S32 = Ratio(Isotope.S36, Isotope.S32)

# Oxygen ratios
O17_O16 = Ratio(Isotope.O17, Isotope.O16)
O18_O16 = Ratio(Isotope.O18, Isotope.O16)
O16H1_O16 = Ratio(Isotope.HYD, Isotope.O16)

three_isotopes_sulphur = Method([Isotope.S32, Isotope.S33, Isotope.S34], [S33_S32, S34_S32])

four_isotopes_sulphur = Method([Isotope.S32, Isotope.S33, Isotope.S34, Isotope.S36], [S33_S32, S34_S32, S36_S32])

two_isotopes_no_hydroxide_oxygen = Method([Isotope.O16, Isotope.O18], [O18_O16])

three_isotopes_no_hydroxide_oxygen = Method([Isotope.O16, Isotope.O17, Isotope.O18], [O17_O16, O18_O16])

two_isotopes_hydroxide_oxygen = Method([Isotope.O16, Isotope.O18, Isotope.HYD], [O18_O16, O16H1_O16])

three_isotopes_hydroxide_oxygen = Method([Isotope.O16, Isotope.O17, Isotope.O18, Isotope.HYD],
                                         [O17_O16, O18_O16, O16H1_O16])

list_of_methods = [three_isotopes_sulphur,
                   four_isotopes_sulphur,
                   two_isotopes_hydroxide_oxygen,
                   two_isotopes_no_hydroxide_oxygen,
                   three_isotopes_hydroxide_oxygen,
                   three_isotopes_no_hydroxide_oxygen
                   ]
