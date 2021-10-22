import re

from src.model.mass_peak import MassPeak
from src.model.settings.asc_file_settings_general import *


class Spot:
    def __init__(self, filename, spot_data):
        self.filename = filename
        parts = re.split('@|\\.|/', self.filename)
        self.sample_name, self.id = parts[-3], parts[-2]
        self.date = spot_data[DATE_INDEX[0]][DATE_INDEX[1]]

        # Finding the number of blocks
        line_number = 113
        contains_blocks = "Blocks" in spot_data[line_number]
        while not contains_blocks:
            line_number += 1
            line = spot_data[line_number]
            contains_blocks = "Blocks" in line
            print(line)
        block_index = spot_data[line_number].index("Blocks")
        self.block_number = spot_data[line_number][block_index-1]
        print(self.block_number)

        # Finding the start of the raw data
        line_number = 160
        contains_word_raw_data = False
        while not contains_word_raw_data:
            line_number += 1
            line = spot_data[line_number]
            if any("RAW DATA" in i for i in line):
                contains_word_raw_data = True
            print(line)
        raw_data_line_start = line_number + 6

        # TODO this should come from the view
        self.mass_peak_names = []

        self.mass_peaks = {}

        for mass_peak_name in self.mass_peak_names:
            detector_yield, detector_background, dead_time = self.get_detector_data()
            raw_cps_data = self.get_raw_cps_data()
            mass_peak = MassPeak(
                self.sample_name,
                self.id,
                mass_peak_name,
                raw_cps_data,
                detector_yield,
                detector_background,
                dead_time
            )

            self.mass_peaks[mass_peak_name] = [mass_peak]

