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

    def __str__(self):
        return self.name()

    # Overriding the equality function as sending an object as a signal seems to break the equality (perhaps the object
    # and class are copied when emitted?)

    def __eq__(self, other):
        return self.numerator == other.numerator and self.denominator == other.denominator and \
            self.has_delta == other.has_delta

    def __hash__(self):
        return hash((self.numerator, self.denominator, self.has_delta))
