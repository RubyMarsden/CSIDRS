three_isotopes_sulphur = {
    "isotopes": ["32S", "33S", "34S"],
    "number_of_ratios": 2,
    "ratios": [
        {"numerator": "33S", "denominator": "32S"},
        {"numerator": "34S", "denominator": "32S"}
    ]
}

four_isotopes_sulphur = {
    "isotopes": ["32S", "33S", "34S"],
    "number_of_ratios": 3,
    "ratios": [
        {"numerator": "33S", "denominator": "32S"},
        {"numerator": "34S", "denominator": "32S"},
        {"numerator": "36S", "denominator": "32S"}
    ]
}

two_isotopes_no_hydroxide_oxygen = {
    "isotopes": ["16O", "18O"],
    "number_of_ratios": 1,
    "ratios": [{"numerator": "18O", "denominator": "16O"}]
}

three_isotopes_no_hydroxide_oxygen = {
    "isotopes": ["16O", "17O", "18O"],
    "number_of_ratios": 2,
    "ratios": [
        {"numerator": "18O", "denominator": "16O"},
        {"numerator": "17O", "denominator": "16O"}
    ]
}

two_isotopes_hydroxide_oxygen = {
    "isotopes": ['16O', '18O', '16O1H'],
    "number_of_ratios": 2,
    "ratios": [
        {"numerator": "18O", "denominator": "16O"},
        {"numerator": "16O1H", "denominator": "16O"}
    ]
}

three_isotopes_hydroxide_oxygen = {
    "isotopes": ['16O', '17O', '18O', '16O1H'],
    "number_of_ratios": 3,
    "ratios": [
        {"numerator": "18O", "denominator": "16O"},
        {"numerator": "17O", "denominator": "16O"},
        {"numerator": "16O1H", "denominator": "16O"}
    ]
}

list_of_method_dictionaries = [three_isotopes_sulphur,
                               four_isotopes_sulphur,
                               two_isotopes_hydroxide_oxygen,
                               two_isotopes_no_hydroxide_oxygen,
                               three_isotopes_hydroxide_oxygen,
                               three_isotopes_no_hydroxide_oxygen
                               ]
