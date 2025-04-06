from model.settings.methods_from_isotopes import Cl37_Cl35, F19_Cl37, S33_S32, S34_S32, S36_S32, O17_O16, O18_O16, \
    C13_C12
from model.elements import Element
from model.settings.material_lists import Material

reference_material_dictionary = {
    # key                                  # value
    #######################
    ### OXYGEN - ZIRCON ###
    #######################
    # Uncertainties are 1sigma
    (Element.OXY, Material.ZIR, "91500"): {O18_O16: (9.94, 0.1), "Citation": "Wiedenbeck et al., 2004"},
    (Element.OXY, Material.ZIR, "M257"): {O18_O16: (13.93, 0.11), "Citation": "Nasdala et al. 2008"},
    (Element.OXY, Material.ZIR, "TEMORA2"): {O18_O16: (8.2, 0.01), "Citation": "Black, et al., 2004"},
    (Element.OXY, Material.ZIR, "Penglai"): {O18_O16: (5.31, 0.06), "Citation": "Li et al. 2010"},

    # Standards below have NOT been analysed in bulk by LF, better to be used as secondary
    (Element.OXY, Material.ZIR, "OGC"): {O18_O16: (5.88, 0.03), "Citation": "Petersson et al., 2019"},
    (Element.OXY, Material.ZIR, "CZ3"): {O18_O16: (15.4, 0.21), "Citation": "Cavosie et al., 2011"},

    ########################
    ### SULPHUR - PYRITE ###
    ########################
    # Uncertainties are 1sigma
    (Element.SUL, Material.PYR, "Sierra"): {S33_S32: (1.09, 0.08), S34_S32: (2.17, 0.14), S36_S32: (3.96, 0.3),
                                            "Citation": "Laflamme et al. 2016"},
    (Element.SUL, Material.PYR, "Balmat"): {S34_S32: (15.1, 0.2), "Citation": "Crowe & Vaughan 1996"},
    # Only 34/32 reported in Crowe & Vaughan - whether uncertainty is 1 or 2 sig is unclear
    (Element.SUL, Material.PYR, "Isua248474"): {S33_S32: (4.33, 0.24), S34_S32: (1.99, 0.18),
                                                "Citation": "Whitehouse2013, Baublys et al. 2004"},
    # SIMS data and rock source described in Whitehouse, bulk from Baublys, large d34S variability reported
    # by Whitehouse2013 (0.86 2SD)
    (Element.SUL, Material.PYR, "Ruttan"): {S34_S32: (1.2, 0.1), "Citation": "Crowe & Vaughan 1996",
                                            "comment": "only 34/32 values"},
    # Only 34/32 reported in Crowe & Vaughan 1996
    (Element.SUL, Material.PYR, "UWPy-1"): {S33_S32: (8.4, None), S34_S32: (16.39, 0.2),
                                            "Citation": "Williford et al., 2011"},
    # This is also from Balmat locality. 34/32 defined in Kozdon et al. 2010 and no-MIF in Williford et al. 2011

    ############################
    ### SULPHUR - PYRRHOTITE ###
    ############################
    # Uncertainties are 1sigma
    (Element.SUL, Material.PRH, "Alexo"): {S33_S32: (1.73, 0.10), S34_S32: (5.23, 0.20), S36_S32: (10.98, 0.295),
                                           "Citation": "Laflamme et al. 2016"},
    # All isotope ratios were measured

    #############################
    ### SULPHUR - PENTLANDITE ###
    #############################
    # Uncertainties are 1sigma
    (Element.SUL, Material.PLT, "VMSO"): {S33_S32: (1.66, 0.12), S34_S32: (3.22, 0.255), S36_S32: (6.37, 0.415),
                                          "Citation": "Laflamme et al. 2016"},
    # All isotope ratios were measured

    #########################
    ### SULPHUR - APATITE ###
    #########################
    # Uncertainties are 1sigma
    (Element.SUL, Material.APT, "Big1"): {S33_S32: (7.22, 0.065), S34_S32: (14.02, 0.11),
                                          "Citation": "Hammerli et al. 2021"},
    # All isotope ratios were measured, NO 36S data on Big1

    ##########################
    ### CHLORINE - APATITE ###
    ##########################
    # Uncertainties are 1sigma
    (Element.CHL, Material.APT, "Tubaf50"): {Cl37_Cl35: (0.32, 0.25), "Citation": "Wudarska et al. 2021"},
    (Element.CHL, Material.APT, "Big1"): {Cl37_Cl35: (0.63, 0.035), "Citation": "In-house collated data, n=53"}

}
