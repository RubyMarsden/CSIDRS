import math
from collections import defaultdict

import numpy as np
import time
import statsmodels.api as sm

from model.drift_correction_type import DriftCorrectionType
from model.elements import Element
from model.isotopes import Isotope
from model.maths import calculate_outlier_resistant_mean_and_st_dev, \
    calculate_delta_from_ratio, calculate_number_of_outliers_to_remove, drift_correction, calculate_sims_alpha, \
    calculate_alpha_correction, calculate_cap_value_and_uncertainty, calculate_the_total_sum_of_squares_from_the_mean, \
    calculate_rsquared_from_tss_and_rss
from model.settings.delta_constants import DeltaReferenceMaterial
from model.settings.delta_constants import oxygen_isotope_reference, sulphur_isotope_reference, \
    carbon_isotope_reference, chlorine_isotope_reference
import model.settings.isotope_reference_materials as rm_settings
from model.settings.methods_from_isotopes import S36_S32, S34_S32, S33_S32
from model.settings.statistics_values import PROBABILITY_CUTOFF, PROBABILITY_OF_SINGLE_OUTLIER


class CalculationResults:
    def __init__(self):
        self._t_zero = None
        self.all_ratio_results = defaultdict(RatioResults)

    def calculate_raw_delta_values(self, samples, method, element, montecarlo_number, factor):
        for sample in samples:
            for spot in sample.spots:
                spot.secondary_ion_yield = calculate_relative_secondary_ion_yield(spot, factor)
                spot.raw_isotope_ratios = calculate_raw_isotope_ratios(spot.mass_peaks, method)
                spot.mean_st_error_isotope_ratios, spot.outliers_removed_from_raw_data, spot.outlier_bounds_by_ratio, spot.cycle_flagging_information = calculate_mean_st_error_for_isotope_ratios(
                    spot.number_of_count_measurements, spot.raw_isotope_ratios)
                spot.not_corrected_deltas = calculate_raw_delta_for_isotope_ratio(spot, element, montecarlo_number)

    def calculate_raw_delta_with_changed_cycle_data(self, samples, method, element, montecarlo_number, factor):
        for sample in samples:
            for spot in sample.spots:
                spot.secondary_ion_yield = calculate_relative_secondary_ion_yield(spot, factor)
                spot.raw_isotope_ratios = calculate_raw_isotope_ratios(spot.mass_peaks, method)
                spot.mean_st_error_isotope_ratios = calculate_mean_and_st_dev_for_isotope_ratio_user_picked_outliers(
                    spot)
                spot.not_corrected_deltas = calculate_raw_delta_for_isotope_ratio(spot, element, montecarlo_number)

    def calculate_data_from_drift_correction_onwards(self, primary_rm, method, samples, drift_correction_type_by_ratio,
                                                     element, material, montecarlo_number):
        self.all_ratio_results = self.drift_correction_process(primary_rm, method, samples, drift_correction_type_by_ratio, montecarlo_number)
        self.SIMS_correction_process(primary_rm, method, samples, element, material, montecarlo_number)
        if Isotope.S33 in method.isotopes:
            self.calculate_cap_values_S33(samples)
        if Isotope.S36 in method.isotopes:
            self.calculate_cap_values_S36(samples)

    def drift_correction_process(self, primary_rm, method, samples, drift_correction_type_by_ratio, montecarlo_number):
        all_ratio_results = {}
        # Currently t_zero is not used anywhere else, however I feel it might be required in the future
        self.calculate_t_zero(primary_rm.spots)
        t_zero = self.get_t_zero()

        for ratio in method.ratios:
            ratio_results = RatioResults()
            ratio_results.assign_primary_rm_data_for_drift_corr_by_ratio(primary_rm, ratio, montecarlo_number, t_zero)
            data = ratio_results.get_primary_rm_data_for_drift_corr()
            times = ratio_results.get_primary_rm_times()
            ratio_results.linear_regression_result = characterise_linear_drift(data, times)

            ratio_results.drift_coefficient, ratio_results.drift_y_intercept = ratio_results.linear_regression_result[1]

            if ratio == S36_S32:
                ratio_results.statsmodel_curvilinear_regression_result = characterise_curvilinear_drift(ratio,
                                                                                                        primary_rm.spots,
                                                                                                        montecarlo_number,
                                                                                                        t_zero)

            for sample in samples:
                for spot in sample.spots:

                    if drift_correction_type_by_ratio[ratio] == DriftCorrectionType.NONE:
                        if ratio.has_delta:
                            spot.drift_corrected_data[ratio] = spot.not_corrected_deltas[ratio]
                        else:
                            spot.drift_corrected_data[ratio] = spot.mean_st_error_isotope_ratios[ratio]

                    elif drift_correction_type_by_ratio[ratio] == DriftCorrectionType.LIN:
                        drift_correction_coef = ratio_results.drift_coefficient

                        spot.drift_corrected_data[ratio] = correct_data_for_linear_drift(spot,
                                                                                         ratio,
                                                                                         drift_correction_coef,
                                                                                         t_zero)

                    elif drift_correction_type_by_ratio[ratio] == DriftCorrectionType.QUAD:
                        print("Not yet it's not")
                    else:
                        raise Exception("There is not a valid input drift type.")

            all_ratio_results[ratio] = ratio_results

        return all_ratio_results

    def calculate_t_zero(self, spots):
        times = []
        for spot in spots:
            if spot.is_flagged:
                continue
            timestamp = time.mktime(spot.datetime.timetuple())
            times.append(timestamp)

        self._t_zero = np.median(times)

    def get_t_zero(self):
        return self._t_zero

    def SIMS_correction_process(self, primary_rm, method, samples, element, material, montecarlo_number):
        # This correction method is described fully in  Kita et al., 2009
        # TODO How does the ratio process work? Can you have different corrections for each one?

        for ratio in method.ratios:
            if ratio.has_delta:
                primary_rm_spot_data = [spot.drift_corrected_data[ratio] for spot in primary_rm.spots if not spot.is_flagged and ratio.has_delta]

                if not primary_rm_spot_data:
                    raise Exception("There is not primary reference material data available")

                primary_rm_mean = np.mean(primary_rm_spot_data, axis=0)

                external_mean, external_st_dev = get_primary_reference_material_external_values_by_ratio(ratio, element,
                                                                                                         material,
                                                                                                         primary_rm)
                external_rm_montecarlo = np.random.normal(external_mean, external_st_dev, montecarlo_number)
                alpha_sims = calculate_sims_alpha(
                    primary_reference_material_mean_delta=primary_rm_mean,
                    externally_measured_primary_reference_value=external_rm_montecarlo)

            for sample in samples:
                for spot in sample.spots:

                    if ratio.has_delta:
                        data = spot.drift_corrected_data[ratio]
                        spot.alpha_corrected_data[ratio] = calculate_alpha_correction(data, alpha_sims)
                    else:
                        spot.alpha_corrected_data[ratio] = spot.drift_corrected_data[ratio]

    def calculate_cap_values_S33(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.cap_data_S33 = calculate_cap_value_and_uncertainty(
                    delta_value_x=spot.alpha_corrected_data[S33_S32],
                    delta_value_relative=spot.alpha_corrected_data[S34_S32],
                    MDF=0.515)

    def calculate_cap_values_S36(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.cap_data_S36 = calculate_cap_value_and_uncertainty(
                    delta_value_x=spot.alpha_corrected_data[S36_S32],
                    delta_value_relative=spot.alpha_corrected_data[S34_S32],
                    MDF=1.91)


# TODO write a test for this function
def calculate_relative_secondary_ion_yield(spot, factor):
    total_cps = 0
    for mass_peak_name, mass_peak in spot.mass_peaks.items():
        if mass_peak_name.usage_in_secondary_ion_calculations:
            total_cps += mass_peak.mean_cps

    secondary_ion_yield = factor * total_cps / (spot.primary_beam_current)

    return secondary_ion_yield


def calculate_raw_isotope_ratios(mass_peaks, method):
    raw_isotope_ratios = {}
    for ratio in method.ratios:
        numerator = ratio.numerator
        denominator = ratio.denominator

        ratios = [i / j for i, j in zip(mass_peaks[numerator].detector_corrected_cps_data,
                                        mass_peaks[denominator].detector_corrected_cps_data)]

        raw_isotope_ratios[ratio] = ratios

    return raw_isotope_ratios


def calculate_mean_st_error_for_isotope_ratios(number_of_count_measurements, raw_isotope_ratios):
    number_of_outliers_to_remove = calculate_number_of_outliers_to_remove(number_of_count_measurements,
                                                                          PROBABILITY_CUTOFF,
                                                                          PROBABILITY_OF_SINGLE_OUTLIER)
    mean_st_error_isotope_ratios = {}
    outliers_removed_from_raw_data = {}
    outlier_bounds_by_ratio = {}
    cycle_flagging_information = {}
    for ratio, raw_ratio_list in raw_isotope_ratios.items():
        mean, st_dev, n, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(raw_ratio_list,
                                                                                                    number_of_outliers_to_remove)

        st_error = st_dev / math.sqrt(n)
        mean_st_error_isotope_ratios[ratio] = [mean, st_error]
        outliers_removed_from_raw_data[ratio] = removed_data
        outlier_bounds_by_ratio[ratio] = outlier_bounds

        cycle_exclude_list = [value in outliers_removed_from_raw_data[ratio] for value in raw_ratio_list]
        cycle_flagging_information[ratio] = cycle_exclude_list

    return mean_st_error_isotope_ratios, outliers_removed_from_raw_data, outlier_bounds_by_ratio, cycle_flagging_information


def calculate_raw_delta_for_isotope_ratio(spot, element, montecarlo_number):
    # TODO this is not quite right yet
    if element == Element.OXY:
        standard_ratios = oxygen_isotope_reference[DeltaReferenceMaterial.VSMOW]
    elif element == Element.SUL:
        standard_ratios = sulphur_isotope_reference[DeltaReferenceMaterial.VCDT]
    elif element == Element.CAR:
        standard_ratios = carbon_isotope_reference[DeltaReferenceMaterial.VPDB]
    elif element == Element.CHL:
        standard_ratios = chlorine_isotope_reference[DeltaReferenceMaterial.SMOC]
    else:
        raise Exception

    not_corrected_deltas = {}

    for ratio, [mean, st_dev] in spot.mean_st_error_isotope_ratios.items():
        mean_montecarlo = np.random.normal(mean, st_dev, montecarlo_number)
        if ratio.has_delta:
            standard_ratio_value, uncertainty = standard_ratios[ratio]
            if uncertainty == 0:
                standard_ratio_value_montecarlo = np.full((montecarlo_number,), standard_ratio_value)
            else:
                standard_ratio_value_montecarlo = np.random.normal(loc=standard_ratio_value, scale=uncertainty,
                                                                   size=montecarlo_number)
            delta_montecarlo = calculate_delta_from_ratio(mean_montecarlo, standard_ratio_value_montecarlo)
            not_corrected_deltas[ratio] = delta_montecarlo

    return not_corrected_deltas

def characterise_linear_drift(data, times):
    # adding a column of '1s' for linear regression modelling to the array 'times'
    times_constant = np.vstack([times, np.ones(len(times))]).T

    results = np.linalg.lstsq(times_constant, data)
    m, c = results[0]
    residual_sum_of_squares = results[1]

    total_sum_of_squares_from_mean = calculate_the_total_sum_of_squares_from_the_mean(data)

    r_squared = calculate_rsquared_from_tss_and_rss(total_sum_of_squares_from_mean, residual_sum_of_squares)

    return [r_squared, (m, c)]

def characterise_curvilinear_drift(ratio, spots, montecarlo_number, t_zero):
    values, times = get_data_for_drift_characterisation_input(ratio, spots, montecarlo_number, t_zero)
    Y = values
    x1 = times
    x2 = [t ** 2 for t in times]
    # making the factors into an array and adding a constant
    x_array = np.column_stack((x1, x2))
    X = sm.add_constant(x_array)
    statsmodel_result = sm.OLS(Y, X).fit()

    return statsmodel_result


def get_data_for_drift_characterisation_input(ratio, spots, montecarlo_number, t_zero):
    times = []
    spots_to_use = [spot for spot in spots if not spot.is_flagged]
    if len(spots_to_use) < 2:
        raise Exception("The number of spots which are not excluded is not sufficient to characterise drift.")
    k = montecarlo_number
    values = np.empty((len(spots_to_use), k))
    for i, spot in enumerate(spots_to_use):
        if spot.is_flagged:
            continue
        timestamp = time.mktime(spot.datetime.timetuple())
        relative_time = timestamp - t_zero
        if ratio.has_delta:
            value_montecarlo = spot.not_corrected_deltas[ratio]
        else:

            value_montecarlo = np.random.normal(spot.mean_st_error_isotope_ratios[ratio][0],
                                                spot.mean_st_error_isotope_ratios[ratio][1], montecarlo_number)

        times.append(relative_time)
        values[i] = value_montecarlo

    return values, times


def correct_data_for_linear_drift(spot, ratio, drift_correction_coef, t_zero):
    timestamp = time.mktime(spot.datetime.timetuple())
    relative_time = timestamp - t_zero
    if ratio.has_delta:
        montecarlo_value = spot.not_corrected_deltas[ratio]

    else:
        montecarlo_value = spot.mean_st_error_isotope_ratios[ratio]


    drift_corrected_data = drift_correction(
        x=relative_time,
        y=montecarlo_value,
        drift_coefficient=drift_correction_coef,
        zero_time=t_zero)
    return drift_corrected_data


def get_primary_reference_material_external_values_by_ratio(ratio, element, material, primary_reference_material):
    key = (element, material, primary_reference_material.name)
    return rm_settings.reference_material_dictionary[key][ratio]


def calculate_mean_and_st_dev_for_isotope_ratio_user_picked_outliers(spot):
    mean_st_dev_isotope_ratios = {}
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
        st_error = st_dev / math.sqrt(n)
        mean_st_dev_isotope_ratios[ratio] = [mean, st_error]

    return mean_st_dev_isotope_ratios


class RatioResults:
    def __init__(self):
        self._primary_rm_times_relative_to_t_zero = None
        self._primary_rm_data_for_drift_corr = None

        self.linear_regression_result = {}
        self.statsmodel_curvilinear_regression_result = {}
        self.statsmodel_multiple_linear_result = {}

        self.drift_coefficient = None
        self.drift_y_intercept = None
        self.drift_correction_type = None

    def assign_primary_rm_data_for_drift_corr_by_ratio(self, primary_rm, ratio, montecarlo_number, t_zero):
        values, times = get_data_for_drift_characterisation_input(ratio, primary_rm.spots, montecarlo_number, t_zero)
        self._primary_rm_data_for_drift_corr = values
        self._primary_rm_times_relative_to_t_zero = times

    def get_primary_rm_data_for_drift_corr(self):
        return self._primary_rm_data_for_drift_corr

    def get_primary_rm_times(self):
        return self._primary_rm_times_relative_to_t_zero
