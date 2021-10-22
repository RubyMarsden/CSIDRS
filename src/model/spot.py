

class Spot:
    def __init__(self, filename, spot_data):
        self.filename = filename
        parts = self.filename.split("@", 1)
        self.sample_name, self.id = parts

