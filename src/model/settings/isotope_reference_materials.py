from src.model.settings.methods_from_isotopes import S33_S32, S34_S32, S36_S32, O17_O16, O18_O16
# TODO should these be objects derived from a reference material class?
# rm_91500 = ReferenceMaterial(name="91500", O18_O16_value=9.94, O18_O16_uncertainty=0.2, citation="Wiedenbeck et al., 2004")
oxygen_zircon_reference_material_dict = {
    "91500": {O18_O16: (9.94, 0.2),"Citation": "Wiedenbeck et al., 2004"},
    "M257": {O18_O16: (13.93, 0.22),"Citation": "Nasdala et al. 2008"},
    "TEMORA2": {O18_O16: (8.2, 0.02),"Citation": "Black, et al., 2004"},
    "Penglai": {O18_O16: (5.31, 0.12),"Citation": "Li et al. 2010"},
    # Standards below have NOT been analysed in bulk by LF, better to be used as secondary
    "OGC": {O18_O16: (5.88, 0.06),"Citation": "Petersson et al., 2019"},
    "CZ3": {O18_O16: (15.4, 0.4),"Citation": "Cavosie et al., 2011"}
}

sulphur_pyrite_reference_material_dict = {
    "Sierra": {S33_S32: (1.09, 0.30), S34_S32: (2.17, 0.28), S36_S32: (3.96, 0.6), "Citation": "Laflamme et al. 2016"},
    # All isotope ratios were measured
    "Balmat": {S34_S32: (15.1, 0.4), "Citation": "Crowe & Vaughan 1996"},
    # Only 34/32 reported in Crowe & Vaughan
    "Isua248474": {S33_S32: (4.33, 0.38), S34_S32: (1.09, 0.30), "Citation": "Whitehouse2013, Baublys et al. 2004"},
    # SIMS data and rock source described in Whitehouse, bulk from Baublys, large d34S variability reported
    # by Whitehouse2013 (0.86 2SD)
    "Ruttan": {S34_S32: (1.2, 0.2), "Citation": "Crowe & Vaughan 1996", "comment": "only 34/32 values"},
    # Only 34/32 reported in Crowe & Vaughan 1996
    "UWPy-1": {S33_S32: (8.4, None), S34_S32: (16.39, 0.4), "Citation": "Williford et al., 2011"}
    # This is also from Balmat locality. 34/32 defined in Kozdon et al. 2010 and no-MIF in Williford et al. 2011
}

sulphur_pyrrhotite_reference_material_dict = {
    "Alexo": {S33_S32: (1.73, 0.20), S34_S32: (5.23, 0.40), S36_S32: (10.98, 0.59), "Citation": "Laflamme et al. 2016"}}
# All isotope ratios were measured

sulphur_pentlandite_reference_material_dict = {
    "VMSO": {S33_S32: (1.66, 0.24), S34_S32: (3.22, 0.51), S36_S32: (6.37, 0.83), "Citation": "Laflamme et al. 2016"}}
# All isotope ratios were measured

sulphur_Apatite_reference_material_dict = {
    "Big1": {S33_S32: (7.22, 0.20), S34_S32: (14.02, 0.40), "Citation": "Hammerli et al. 2021"}}
# All isotope ratios were measured, NO 36S data on Big1
