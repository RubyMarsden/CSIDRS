from src.model.settings.methods_from_isotopes import Cl37_Cl35, F19_Cl37, S33_S32, S34_S32, S36_S32, O17_O16, O18_O16, \
    C13_C12
from src.model.elements import Element
from src.model.settings.material_lists import Material

reference_material_dictionary = {
    # key                                  # value
    #######################
    ### OXYGEN - ZIRCON ###
    #######################
    (Element.OXY, Material.ZIR, "91500"): {O18_O16: (9.94, 0.2), "Citation": "Wiedenbeck et al., 2004"},
    (Element.OXY, Material.ZIR, "M257"): {O18_O16: (13.93, 0.22), "Citation": "Nasdala et al. 2008"},
    (Element.OXY, Material.ZIR, "TEMORA2"): {O18_O16: (8.2, 0.02), "Citation": "Black, et al., 2004"},
    (Element.OXY, Material.ZIR, "Penglai"): {O18_O16: (5.31, 0.12), "Citation": "Li et al. 2010"},

    # Standards below have NOT been analysed in bulk by LF, better to be used as secondary
    (Element.OXY, Material.ZIR, "OGC"): {O18_O16: (5.88, 0.06), "Citation": "Petersson et al., 2019"},
    (Element.OXY, Material.ZIR, "CZ3"): {O18_O16: (15.4, 0.4), "Citation": "Cavosie et al., 2011"},

    ########################
    ### SULPHUR - PYRITE ###
    ########################
    (Element.SUL, Material.PYR, "Sierra"): {S33_S32: (1.09, 0.30), S34_S32: (2.17, 0.28), S36_S32: (3.96, 0.6),
                                            "Citation": "Laflamme et al. 2016"},
    (Element.SUL, Material.PYR, "Balmat"): {S34_S32: (15.1, 0.4), "Citation": "Crowe & Vaughan 1996"},
    # Only 34/32 reported in Crowe & Vaughan
    (Element.SUL, Material.PYR, "Isua248474"): {S33_S32: (4.33, 0.38), S34_S32: (1.09, 0.30),
                                                "Citation": "Whitehouse2013, Baublys et al. 2004"},
    # SIMS data and rock source described in Whitehouse, bulk from Baublys, large d34S variability reported
    # by Whitehouse2013 (0.86 2SD)
    (Element.SUL, Material.PYR, "Ruttan"): {S34_S32: (1.2, 0.2), "Citation": "Crowe & Vaughan 1996",
                                            "comment": "only 34/32 values"},
    # Only 34/32 reported in Crowe & Vaughan 1996
    (Element.SUL, Material.PYR, "UWPy-1"): {S33_S32: (8.4, None), S34_S32: (16.39, 0.4),
                                            "Citation": "Williford et al., 2011"},
    # This is also from Balmat locality. 34/32 defined in Kozdon et al. 2010 and no-MIF in Williford et al. 2011

    ############################
    ### SULPHUR - PYRRHOTITE ###
    ############################

    (Element.SUL, Material.PRH, "Alexo"): {S33_S32: (1.73, 0.20), S34_S32: (5.23, 0.40), S36_S32: (10.98, 0.59),
                                           "Citation": "Laflamme et al. 2016"},
    # All isotope ratios were measured

    #############################
    ### SULPHUR - PENTLANDITE ###
    #############################

    (Element.SUL, Material.PLT, "VMSO"): {S33_S32: (1.66, 0.24), S34_S32: (3.22, 0.51), S36_S32: (6.37, 0.83),
                                          "Citation": "Laflamme et al. 2016"},
    # All isotope ratios were measured

    #########################
    ### SULPHUR - APATITE ###
    #########################

    (Element.SUL, Material.APT, "Big1"): {S33_S32: (7.22, 0.20), S34_S32: (14.02, 0.40),
                                          "Citation": "Hammerli et al. 2021"},
    # All isotope ratios were measured, NO 36S data on Big1

    ##########################
    ### CHLORINE - APATITE ###
    ##########################
    (Element.CHL, Material.APT, "Tubaf50"): {Cl37_Cl35: (0.32, 0.25), "Citation": "Wurarska et al. 2021"},
    (Element.CHL, Material.APT, "Big1"): {Cl37_Cl35: (0.63, 0.14), "Citation": "In-house collated data, n=53"}

}
