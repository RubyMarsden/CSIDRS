class Sample:
    def __init__(self, sample_name):
        self.spots = []
        self.name = sample_name

        self.colour = None
        self.q_colour = None

    def __repr__(self):
        return self.name
