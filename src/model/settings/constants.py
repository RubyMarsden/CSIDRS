from src.model.settings.methods_from_isotopes import S33_S32, S34_S32, S36_S32, O17_O16, O18_O16, Cl37_Cl35, F19_Cl37, C13_C12

# TODO make sure all constants come from this file.
oxygen_isotope_reference = {
    'VSMOW': {O18_O16: 0.002005, O17_O16: 0.0003799}
}

sulphur_isotope_reference = {
    'VCDT': {S34_S32: 0.04416259, S33_S32: 0.00787724, S36_S32: 0.00015349}
}

carbon_isotope_reference = {
    'VPDB': {C13_C12: 0.011180}
}

chlorine_isotope_reference = {
    'SMOC': {Cl37_Cl35: 0.319533}
}
