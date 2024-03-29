from enum import Enum
from model.settings.methods_from_isotopes import S33_S32, S34_S32, S36_S32, O17_O16, O18_O16, O16H1_O16, Cl37_Cl35, \
    F19_Cl37, C13_C12


class DeltaReferenceMaterial(Enum):
    VSMOW = 'VSMOW'
    VCDT = 'VCDT'
    VPDB = 'VPDB'
    SMOC = 'SMOC'


oxygen_isotope_reference = {
    DeltaReferenceMaterial.VSMOW: {O18_O16: (0.0020052, 0.000000), O17_O16: (0.0003799, 0.000000)}
}
# "Reference Sheet for International Measurement Standards" (PDF). International Atomic Energy Agency. December 2006.
# Reported uncertainty on VSMOW is O18_O16: (0.0020052, 0.00000045), O17_O16: (0.0003799, 0.0000008)
# However, as this is an arbitrary scale should there be uncertainty propagated through at all?


sulphur_isotope_reference = {
    DeltaReferenceMaterial.VCDT: {S34_S32: (0.04416259, 0), S33_S32: (0.00787724, 0), S36_S32: (0.00015349, 0)}
}

# Artificial scale - uncertainty is not reported for VCDT

carbon_isotope_reference = {
    DeltaReferenceMaterial.VPDB: {C13_C12: (0.011180, 0.000028)}
}
# Absolute isotope ratios defining isotope scales used in isotope ratio mass spectrometers and optical isotope instruments
# Skrzypek, Grzegorz; Dunn, Philip J. H.
# Rapid Communications in Mass Spectrometry (2020), 34 (20), e8890CODEN: RCMSEF; ISSN:0951-4198. (John Wiley & Sons Ltd.)
# Different methods may use different VPDB values?
chlorine_isotope_reference = {
    DeltaReferenceMaterial.SMOC: {Cl37_Cl35: (0.319533, 0)}
}


# As these values are arbirtrary numbers to make a reference scale rather than using pure ratios should there be uncertainty?