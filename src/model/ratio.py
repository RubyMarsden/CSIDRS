class Ratio:
    def __init__(self, numerator, denominator, has_delta: bool):
        self.numerator = numerator
        self.denominator = denominator
        self.has_delta = has_delta

    def name(self):
        return self.numerator.isotope_name + "/" + self.denominator.isotope_name

    def delta_name(self):
        if self.has_delta:
            return "delta" + self.numerator.isotope_name

        raise Exception("You are calling delta_name on a ratio which has no delta value.")
