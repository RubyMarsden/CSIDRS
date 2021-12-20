from enum import Enum
from src.model.settings.methods_from_isotopes import S33_S32, S34_S32, S36_S32, O17_O16, O18_O16, O16H1_O16, Cl37_Cl35, \
    F19_Cl37, C13_C12


class DeltaReferenceMaterial(Enum):
    VSMOW = 'VSMOW'
    VCDT = 'VCDT'
    VPDB = 'VPDB'
    SMOC = 'SMOC'


oxygen_isotope_reference = {
    DeltaReferenceMaterial.VSMOW : {O18_O16: 0.002005, O17_O16: 0.0003799, O16H1_O16: None}
}

sulphur_isotope_reference = {
    DeltaReferenceMaterial.VCDT: {S34_S32: 0.04416259, S33_S32: 0.00787724, S36_S32: 0.00015349}
}

carbon_isotope_reference = {
    DeltaReferenceMaterial.VPDB: {C13_C12: 0.011180}
}

chlorine_isotope_reference = {
    DeltaReferenceMaterial.SMOC: {Cl37_Cl35: 0.319533, F19_Cl37: None}
}
