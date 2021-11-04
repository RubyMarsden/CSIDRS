import re
from datetime import datetime

from src.model.mass_peak import MassPeak
from src.model.settings.asc_file_settings_general import *
from src.model.get_data_from_import import get_data_from_old_asc
from src.utils.convert_twelve_to_twenty_four_hour_time import convert_to_twenty_four_hour_time


class Spot:
    def __init__(self, filename, spot_data, mass_peak_names):
        self.filename = filename
        parts = re.split('@|\\.|/', self.filename)
        self.full_sample_name, self.id = parts[-3], parts[-2]
        # TODO change how this works - currently doesn't update
        self.mass_peak_names = mass_peak_names

        self.spot_data = spot_data
        self.date = self.spot_data[DATE_INDEX[0]][DATE_INDEX[1]]
        self.time, self.twelve_hr_data = str.split(self.spot_data[TIME_INDEX[0]][TIME_INDEX[1]])
        if self.twelve_hr_data == "AM":
            self.twenty_four_hour_time = self.time
        elif self.twelve_hr_data == "PM":
            self.twenty_four_hour_time = convert_to_twenty_four_hour_time(self.time)
        self.datetime = datetime.strptime(self.date + " " + self.time, "%d/%m/%Y %H:%M")

        self.x_position = spot_data[X_POSITION_INDEX[0]][X_POSITION_INDEX[1]]
        self.y_position = spot_data[Y_POSITION_INDEX[0]][Y_POSITION_INDEX[1]]

        self.mass_peaks = {}

        for mass_peak_name in self.mass_peak_names:
            raw_cps_data, detector_data = get_data_from_old_asc(self.spot_data, mass_peak_name)
            mass_peak = MassPeak(
                self.full_sample_name,
                self.id,
                mass_peak_name,
                raw_cps_data,
                detector_data
            )

            self.mass_peaks[mass_peak_name] = [mass_peak]
            mass_peak.correct_cps_data_for_detector_parameters()
