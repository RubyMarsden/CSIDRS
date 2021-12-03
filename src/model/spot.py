import math
import re
from datetime import datetime

from src.model.elements import Element
from src.model.mass_peak import MassPeak
from src.model.maths import vector_length_from_origin, calculate_outlier_resistant_mean_and_st_dev, \
    calculate_delta_from_ratio
from src.model.settings.asc_file_settings_general import *
from src.model.get_data_from_import import get_data_from_old_asc, get_primary_beam_current_data_old_asc, \
    get_dtfa_x_and_y_from_old_asc
from src.model.settings.constants import oxygen_isotope_reference, sulphur_isotope_reference, carbon_isotope_reference
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
        # TODO - what happens at midnight?
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

        self.is_flagged = False
        self.secondary_ion_yield = None
        self.mass_peaks = {}
        self.raw_isotope_ratios = {}
        self.mean_two_st_error_isotope_ratios = {}
        self.outliers_removed_from_raw_data = {}
        self.outlier_bounds = {}
        self.cycle_flagging_information = {}
        self.not_corrected_deltas = {}
        self.drift_corrected_deltas = {}
        self.alpha_corrected_data = {}

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
            self.mass_peaks[mass_peak_name] = mass_peak

    # TODO write a test for this function
    def calculate_relative_secondary_ion_yield(self):
        cps_values = [mass_peak.mean_cps for mass_peak in self.mass_peaks.values()]
        total_cps = sum(cps_values)
        self.secondary_ion_yield = total_cps / (self.primary_beam_current * (10 ** 18))

    def calculate_raw_isotope_ratios(self, method):

        for ratio in method.ratios:
            numerator = ratio.numerator
            denominator = ratio.denominator

            ratios = [i / j for i, j in zip(self.mass_peaks[numerator].detector_corrected_cps_data,
                                            self.mass_peaks[denominator].detector_corrected_cps_data)]

            self.raw_isotope_ratios[ratio] = ratios

    def calculate_mean_st_error_for_isotope_ratios(self):
        for ratio, raw_ratio_list in self.raw_isotope_ratios.items():
            # TODO fix number of outliers allowed
            mean, st_dev, n, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(raw_ratio_list,
                                                                                                        1)
            two_st_error = 2 * st_dev / math.sqrt(n)
            self.mean_two_st_error_isotope_ratios[ratio] = [mean, two_st_error]
            self.outliers_removed_from_raw_data[ratio] = removed_data
            self.outlier_bounds[ratio] = outlier_bounds

            cycle_exclude_list = []
            for value in raw_ratio_list:
                if value in self.outliers_removed_from_raw_data[ratio]:
                    cycle_exclude_list.append(True)
                else:
                    cycle_exclude_list.append(False)
            self.cycle_flagging_information[ratio] = cycle_exclude_list

    def calculate_raw_delta_for_isotope_ratio(self, element):
        # TODO this is not quite right yet
        if element == Element.OXY:
            standard_ratios = oxygen_isotope_reference["VSMOW"]
        elif element == Element.SUL:
            standard_ratios = sulphur_isotope_reference["VCDT"]
        elif element == Element.CAR:
            standard_ratios = carbon_isotope_reference["VPDB"]
        else:
            raise Exception

        for ratio, [mean, two_st_error] in self.mean_two_st_error_isotope_ratios.items():
            standard_ratio = standard_ratios[ratio]
            delta, delta_uncertainty = calculate_delta_from_ratio(mean, two_st_error, standard_ratio)
            self.not_corrected_deltas[ratio.delta_name] = [delta, delta_uncertainty]
