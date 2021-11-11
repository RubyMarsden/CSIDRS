import re
from datetime import datetime

from src.model.mass_peak import MassPeak
from src.model.maths import vector_length_from_origin
from src.model.settings.asc_file_settings_general import *
from src.model.get_data_from_import import get_data_from_old_asc, get_primary_beam_current_data_old_asc, \
    get_dtfa_x_and_y_from_old_asc
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
        #TODO - what happens at midnight?
        if self.twelve_hr_data == "AM":
            self.twenty_four_hour_time = self.time
        elif self.twelve_hr_data == "PM":
            self.twenty_four_hour_time = convert_to_twenty_four_hour_time(self.time)
        self.datetime = datetime.strptime(self.date + " " + self.twenty_four_hour_time, "%d/%m/%Y %H:%M")

        self.x_position = int(spot_data[X_POSITION_INDEX[0]][X_POSITION_INDEX[1]])
        self.y_position = int(spot_data[Y_POSITION_INDEX[0]][Y_POSITION_INDEX[1]])
        self.distance_from_mount_centre = vector_length_from_origin(self.x_position, self.y_position)

        self.dtfa_x, self.dtfa_y = get_dtfa_x_and_y_from_old_asc(self.spot_data)

        self.primary_beam_current = get_primary_beam_current_data_old_asc(self.spot_data)
        self.secondary_ion_yield = None

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

            mass_peak.correct_cps_data_for_detector_parameters()
            mass_peak.outlier_resistant_mean_and_st_error()
            self.mass_peaks[mass_peak_name] = [mass_peak]

    # TODO write a test for this function
    def calculate_relative_secondary_ion_yield(self):
        cps_values = [mass_peak[0].mean_cps for mass_peak in self.mass_peaks.values()]
        total_cps = sum(cps_values)
        self.secondary_ion_yield = total_cps/(self.primary_beam_current * (10 ** 18))

    def calculate_raw_isotope_ratios(self, methods):
        for method in methods:
            # TODO fix this - it's a problem :(
            return
