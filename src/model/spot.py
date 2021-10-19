

class Spot:
    def __init__(self, spot_data, filename):
        self.filename = filename
        parts = self.filename.split("@", 1)
        self.sample_name, self.id = parts

