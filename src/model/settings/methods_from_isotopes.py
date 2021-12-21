from src.model.isotopes import Isotope
from src.model.method import Method
from src.model.ratio import Ratio

# Chlorine ratios
Cl37_Cl35 = Ratio(Isotope.Cl37, Isotope.Cl35)
F19_Cl37 = Ratio(Isotope.F19, Isotope.Cl37)

# Carbon ratios
C13_C12 = Ratio(Isotope.C13, Isotope.C12)
C14_C12 = Ratio(Isotope.C14, Isotope.C12)

# Sulphur ratios
S33_S32 = Ratio(Isotope.S33, Isotope.S32)
S34_S32 = Ratio(Isotope.S34, Isotope.S32)
S36_S32 = Ratio(Isotope.S36, Isotope.S32)

# Oxygen ratios
O17_O16 = Ratio(Isotope.O17, Isotope.O16)
O18_O16 = Ratio(Isotope.O18, Isotope.O16)
O16H1_O16 = Ratio(Isotope.HYD, Isotope.O16)

two_isotopes_carbon = Method([Isotope.C12, Isotope.C13, Isotope.C14], [C14_C12, C13_C12])

two_isotopes_chlorine_fluorine = Method([Isotope.Cl35, Isotope.Cl37, Isotope.F19], [Cl37_Cl35, F19_Cl37])

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
                   three_isotopes_no_hydroxide_oxygen,
                   two_isotopes_chlorine_fluorine,
                   two_isotopes_carbon
                   ]
