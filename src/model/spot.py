import re

class Spot:
    def __init__(self, filename, spot_data):
        self.filename = filename
        parts = re.split('@|\\.|/', self.filename)
        self.sample_name, self.id = parts[-3], parts[-2]

