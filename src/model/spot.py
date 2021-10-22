import re
from src.model.settings.asc_file_settings_general import *

class Spot:
    def __init__(self, filename, spot_data):
        self.filename = filename
        parts = re.split('@|\\.|/', self.filename)
        self.sample_name, self.id = parts[-3], parts[-2]
        self.date = spot_data[DATE_INDEX[0]][DATE_INDEX[1]]

