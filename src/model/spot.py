import math
import re
from datetime import datetime

from model.get_data_from_import import get_data_from_asc, get_primary_beam_current_data_asc, \
    get_dtfa_x_and_y_from_asc
from model.mass_peak import MassPeak, correct_cps_data_for_detector_parameters, outlier_resistant_mean_and_st_error
from model.maths import vector_length_from_origin, calculate_outlier_resistant_mean_and_st_dev
from model.settings.asc_file_settings_general import *
from utils.convert_date_format_from_new_asci import standardise_date_format
from utils.convert_twelve_to_twenty_four_hour_time import convert_to_twenty_four_hour_time_pm, \
    convert_to_twenty_four_hour_time_am
from utils.general_utils import split_cameca_data_filename


class Spot:
    def __init__(self, filename, spot_data, mass_peak_names):
        self.filename = filename
        self.full_sample_name, self.id = split_cameca_data_filename(filename)
        split_sample_name = re.split('-|_', self.full_sample_name)
        self.sample_name = split_sample_name[-1]
        # TODO change how this works - currently doesn't update
        self.mass_peak_names = mass_peak_names

        self.spot_data = spot_data
        self.date = standardise_date_format(self.spot_data[DATE_INDEX[0]][DATE_INDEX[1]])
        self.time, self.twelve_hr_data = str.split(self.spot_data[TIME_INDEX[0]][TIME_INDEX[1]])
        # TODO - what happens at midnight?
        if self.twelve_hr_data == "AM":
            self.twenty_four_hour_time = convert_to_twenty_four_hour_time_am(self.time)
        elif self.twelve_hr_data == "PM":
            self.twenty_four_hour_time = convert_to_twenty_four_hour_time_pm(self.time)
        self.datetime = datetime.strptime(self.date + " " + self.twenty_four_hour_time, "%d/%m/%Y %H:%M")

        self.x_position = int(spot_data[X_POSITION_INDEX[0]][X_POSITION_INDEX[1]])
        self.y_position = int(spot_data[Y_POSITION_INDEX[0]][Y_POSITION_INDEX[1]])

        self.distance_from_mount_centre = vector_length_from_origin(self.x_position, self.y_position)

        self.dtfa_x, self.dtfa_y = get_dtfa_x_and_y_from_asc(self.spot_data)

        self.primary_beam_current = get_primary_beam_current_data_asc(self.spot_data)

        self.is_flagged = False
        self.secondary_ion_yield = None
        self.mass_peaks = {}
        self.raw_isotope_ratios = {}
        self.mean_two_st_error_isotope_ratios = {}
        self.outliers_removed_from_raw_data = {}
        self.outlier_bounds = {}
        self.cycle_flagging_information = {}
        self.standard_ratios = None
        self.drift_corrected_ratio_values_by_ratio = {}
        self.not_corrected_deltas = {}
        self.drift_corrected_data = {}
        self.alpha_corrected_data = {}

        for mass_peak_name in self.mass_peak_names:
            raw_cps_data, detector_data, number_of_measurements = get_data_from_asc(self.spot_data, mass_peak_name)
            mass_peak = MassPeak(
                self.full_sample_name,
                self.id,
                mass_peak_name,
                raw_cps_data,
                detector_data,
                number_of_measurements
            )

            mass_peak.detector_corrected_cps_data = correct_cps_data_for_detector_parameters(mass_peak)
            mass_peak.mean_cps, mass_peak.st_error_cps = outlier_resistant_mean_and_st_error(mass_peak)
            self.mass_peaks[mass_peak_name] = mass_peak

        if len({mass_peak.number_of_measurements for mass_peak in self.mass_peaks.values()}) != 1:
            raise Exception("Mass peaks have different numbers of cycles - this indicates a problem with the input "
                            "data file")
        self.number_of_count_measurements = [mass_peak for mass_peak in self.mass_peaks.values()][
            0].number_of_measurements


def calculate_mean_and_st_dev_for_isotope_ratio_user_picked_outliers(spot):
    mean_two_st_error_isotope_ratios = {}
    for ratio in spot.raw_isotope_ratios.keys():
        list_of_cycle_exclusion_information = spot.cycle_flagging_information[ratio]
        raw_ratio_list = spot.raw_isotope_ratios[ratio]
        raw_ratio_list_exclude = []
        for i, boolean in enumerate(list_of_cycle_exclusion_information):
            if not boolean:
                raw_ratio_list_exclude.append(i)

        raw_ratio_list = [raw_ratio_list[i] for i in raw_ratio_list_exclude]

        mean, st_dev, n, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(raw_ratio_list,
                                                                                                    0)
        two_st_error = 2 * st_dev / math.sqrt(n)

        mean_two_st_error_isotope_ratios[ratio] = [mean, two_st_error]

    return mean_two_st_error_isotope_ratios


def exclude_cycle_information_update(spot, cycle_number, is_flagged, ratio):
    spot.cycle_flagging_information[ratio][cycle_number] = is_flagged


from enum import Enum


class SpotAttribute(Enum):

    # Overriding the equality function as sending an Enum as a signal seems to break the equality (perhaps the object
    # and class are copied when emitted?)
    def __eq__(self, other):
        return self.value == other.value and self.name == other.name

    TIME = "Time"
    DTFAX = "dtfa-x"
    DTFAY = "dtfa-y"
    DISTANCE = "Distance to mount centre"
