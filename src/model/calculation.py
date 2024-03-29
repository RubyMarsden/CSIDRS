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
    calculate_alpha_correction, calculate_cap_value_and_uncertainty
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

    def calculate_raw_delta_values(self, samples, method, element):
        print("Processing...")
        for sample in samples:
            for spot in sample.spots:
                spot.secondary_ion_yield = calculate_relative_secondary_ion_yield(spot)
                spot.raw_isotope_ratios = calculate_raw_isotope_ratios(spot.mass_peaks, method)
                spot.mean_st_error_isotope_ratios, spot.outliers_removed_from_raw_data, spot.outlier_bounds_by_ratio, spot.cycle_flagging_information = calculate_mean_st_error_for_isotope_ratios(
                    spot.number_of_count_measurements, spot.raw_isotope_ratios)
                spot.not_corrected_deltas = calculate_raw_delta_for_isotope_ratio(spot, element)

    def calculate_raw_delta_with_changed_cycle_data(self, samples, element):
        for sample in samples:
            for spot in sample.spots:
                spot.mean_st_error_isotope_ratios = calculate_mean_and_st_dev_for_isotope_ratio_user_picked_outliers(
                    spot)
                spot.not_corrected_deltas = calculate_raw_delta_for_isotope_ratio(spot, element)

    def calculate_data_from_drift_correction_onwards(self, primary_rm, method, samples, drift_correction_type_by_ratio,
                                                     element, material):
        self.drift_correction_process(primary_rm, method, samples, drift_correction_type_by_ratio)
        self.SIMS_correction_process(primary_rm, method, samples, element, material)
        if Isotope.S33 in method.isotopes:
            self.calculate_cap_values_S33(primary_rm, samples)
        if Isotope.S36 in method.isotopes:
            self.calculate_cap_values_S36(primary_rm, samples)

    def drift_correction_process(self, primary_rm, method, samples, drift_correction_type_by_ratio):

        # Currently t_zero is not used anywhere else, however I feel it might be required in the future
        self.calculate_t_zero(primary_rm.spots)
        t_zero = self.get_t_zero()

        for ratio in method.ratios:
            ratio_results = RatioResults()
            ratio_results.assign_primary_rm_deltas_by_ratio(primary_rm, ratio)
            ratio_results.statsmodel_result = characterise_linear_drift(ratio, primary_rm.spots)

            ratio_results.drift_y_intercept, ratio_results.drift_coefficient = ratio_results.statsmodel_result.params

            if ratio == S36_S32:
                ratio_results.statsmodel_curvilinear_result = characterise_curvilinear_drift(ratio, primary_rm.spots)

            for sample in samples:
                for spot in sample.spots:

                    if drift_correction_type_by_ratio[ratio] == DriftCorrectionType.NONE:
                        if ratio.has_delta:
                            spot.drift_corrected_data[ratio] = spot.not_corrected_deltas[ratio]
                        else:
                            spot.drift_corrected_data[ratio] = spot.mean_st_error_isotope_ratios[ratio]

                    elif drift_correction_type_by_ratio[ratio] == DriftCorrectionType.LIN:
                        drift_correction_coef = float(ratio_results.drift_coefficient)

                        spot.drift_corrected_data[ratio] = correct_data_for_linear_drift(spot,
                                                                                         ratio,
                                                                                         drift_correction_coef,
                                                                                         t_zero)

                    elif drift_correction_type_by_ratio[ratio] == DriftCorrectionType.QUAD:
                        print("Not yet it's not")
                    else:
                        raise Exception("There is not a valid input drift type.")

            self.all_ratio_results[ratio] = ratio_results

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

    def SIMS_correction_process(self, primary_rm, method, samples, element, material):
        # This correction method is described fully in  Kita et al., 2009
        # TODO How does the ratio process work? Can you have different corrections for each one?

        for ratio in method.ratios:
            if ratio.has_delta:
                primary_rm_spot_data = [spot.drift_corrected_data[ratio][0] for spot in primary_rm.spots if
                                        not spot.is_flagged and ratio.has_delta]

                if not primary_rm_spot_data:
                    raise Exception("There is not primary reference material data available")
                primary_rm_mean = np.mean(primary_rm_spot_data)
                primary_uncertainty = np.std(primary_rm_spot_data)

                primary_rm_external_value_uncertainty = get_primary_reference_material_external_values_by_ratio(ratio,
                                                                                                                element,
                                                                                                                material,
                                                                                                                primary_rm)

                alpha_sims, alpha_sims_uncertainty = calculate_sims_alpha(
                    primary_reference_material_mean_delta=primary_rm_mean,
                    primary_reference_material_st_dev=primary_uncertainty,
                    externally_measured_primary_reference_value_and_uncertainty=
                    primary_rm_external_value_uncertainty)

            for sample in samples:
                for spot in sample.spots:

                    if ratio.has_delta:
                        data = spot.drift_corrected_data[ratio]
                        spot.alpha_corrected_data[ratio] = calculate_alpha_correction(data, alpha_sims,
                                                                                      alpha_sims_uncertainty)
                    else:
                        spot.alpha_corrected_data[ratio] = spot.drift_corrected_data[ratio]

    def calculate_cap_values_S33(self, primary_rm, samples):
        primary_rm_spot_data_33 = [spot.drift_corrected_data[S33_S32][0] for spot in
                                   primary_rm.spots if
                                   not spot.is_flagged]
        primary_rm_spot_data_34 = [spot.drift_corrected_data[S34_S32][0] for spot in
                                   primary_rm.spots if
                                   not spot.is_flagged]
        array_33 = np.array(primary_rm_spot_data_33)
        array_34 = np.array(primary_rm_spot_data_34)
        primary_covariance_33_34 = np.cov(array_33, array_34)[0][1]

        for sample in samples:
            for spot in sample.spots:
                spot.cap_data_S33 = calculate_cap_value_and_uncertainty(
                    delta_value_x=spot.alpha_corrected_data[S33_S32][0],
                    uncertainty_x=spot.alpha_corrected_data[S33_S32][1],
                    delta_value_relative=spot.alpha_corrected_data[S34_S32][0],
                    uncertainty_relative=spot.alpha_corrected_data[S34_S32][1],
                    MDF=0.515,
                    reference_material_covariance=primary_covariance_33_34)

    def calculate_cap_values_S36(self, primary_rm, samples):
        primary_rm_spot_data_34 = [spot.drift_corrected_data[S34_S32][0] for spot in
                                   primary_rm.spots if
                                   not spot.is_flagged]
        primary_rm_spot_data_36 = [spot.drift_corrected_data[S36_S32][0] for spot in
                                   primary_rm.spots if
                                   not spot.is_flagged]

        array_34 = np.array(primary_rm_spot_data_34)
        array_36 = np.array(primary_rm_spot_data_36)
        primary_covariance_36_34 = np.cov(array_36, array_34)[0][1]

        for sample in samples:
            for spot in sample.spots:
                spot.cap_data_S36 = calculate_cap_value_and_uncertainty(
                    delta_value_x=spot.alpha_corrected_data[S36_S32][0],
                    uncertainty_x=spot.alpha_corrected_data[S36_S32][1],
                    delta_value_relative=spot.alpha_corrected_data[S34_S32][0],
                    uncertainty_relative=spot.alpha_corrected_data[S34_S32][1],
                    MDF=1.91,
                    reference_material_covariance=primary_covariance_36_34)


# TODO write a test for this function
def calculate_relative_secondary_ion_yield(spot):
    total_cps = 0
    for mass_peak_name, mass_peak in spot.mass_peaks.items():
        if mass_peak_name.usage_in_secondary_ion_calculations:
            total_cps += mass_peak.mean_cps
    secondary_ion_yield = total_cps / (spot.primary_beam_current * (10 ** 18))

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


def calculate_raw_delta_for_isotope_ratio(spot, element):
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
    for ratio, [mean, two_st_error] in spot.mean_st_error_isotope_ratios.items():
        if ratio.has_delta:
            standard_ratio_value, uncertainty = standard_ratios[ratio]
            delta, delta_uncertainty = calculate_delta_from_ratio(mean, two_st_error, standard_ratio_value)
            not_corrected_deltas[ratio] = (delta, delta_uncertainty)

    return not_corrected_deltas


def characterise_linear_drift(ratio, spots):
    values, times = get_data_for_drift_characterisation_input(ratio, spots)
    Y = values
    # adding a column of '1s' for statsmodels to the array 'times'
    X = sm.add_constant(times)
    statsmodel_result = sm.OLS(Y, X).fit()
    return statsmodel_result


def characterise_curvilinear_drift(ratio, spots):
    values, times = get_data_for_drift_characterisation_input(ratio, spots)
    Y = values
    x1 = times
    x2 = [t ** 2 for t in times]
    # making the factors into an array and adding a constant
    x_array = np.column_stack((x1, x2))
    X = sm.add_constant(x_array)
    statsmodel_result = sm.OLS(Y, X).fit()

    return statsmodel_result


def get_data_for_drift_characterisation_input(ratio, spots):
    times = []
    values = []
    for spot in spots:
        if spot.is_flagged:
            continue
        timestamp = time.mktime(spot.datetime.timetuple())
        if ratio.has_delta:
            [value, _uncertainty] = spot.not_corrected_deltas[ratio]
        else:
            [value, _uncertainty] = spot.mean_st_error_isotope_ratios[ratio]

        times.append(timestamp)
        values.append(value)

    return values, times


def correct_data_for_linear_drift(spot, ratio, drift_correction_coef, t_zero):
    timestamp = time.mktime(spot.datetime.timetuple())
    if ratio.has_delta:
        [value, uncertainty] = spot.not_corrected_deltas[ratio]

    else:
        [value, uncertainty] = spot.mean_st_error_isotope_ratios[ratio]

    drift_corrected_data = drift_correction(
        x=timestamp,
        y=value,
        dy=uncertainty,
        drift_coefficient=drift_correction_coef,
        zero_time=t_zero)
    return drift_corrected_data


def get_primary_reference_material_external_values_by_ratio(ratio, element, material, primary_reference_material):
    key = (element, material, primary_reference_material.name)
    return rm_settings.reference_material_dictionary[key][ratio]


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

class RatioResults:
    def __init__(self):
        self._primary_rm_deltas = {}

        self.statsmodel_result = {}
        self.statsmodel_curvilinear_result = {}
        self.statsmodel_multiple_linear_result = {}

        self.drift_coefficient = None
        self.drift_y_intercept = None
        self.drift_correction_type = None

    def assign_primary_rm_deltas_by_ratio(self, primary_rm, ratio):
        values, times = get_data_for_drift_characterisation_input(ratio, primary_rm.spots)
        self._primary_rm_deltas = values

    def get_primary_rm_deltas(self):
        return self._primary_rm_deltas
