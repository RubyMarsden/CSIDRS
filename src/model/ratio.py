class Ratio:
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator
        self.name = numerator.value + "/" + denominator.value
        self.delta_name = "delta" + self.name
