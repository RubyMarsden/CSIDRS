class Sample:
    def __init__(self, sample_name):
        self.spots = []
        self.name = sample_name
        self.is_primary_reference_material = False
        self.is_secondary_reference_material = False

    def __repr__(self):
        return self.name
