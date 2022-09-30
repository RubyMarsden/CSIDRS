import csv
import re
import time

import matplotlib
import numpy as np
# from ltsfit.lts_linefit import lts_linefit
import statsmodels.api as sm
from PyQt5.QtGui import QColor

from model.drift_correction_type import DriftCorrectionType
from model.get_data_from_import import get_block_number_from_asc, \
    get_analytical_conditions_data_from_asc_file
from model.maths import drift_correction, calculate_sims_alpha, calculate_alpha_correction
from model.sample import Sample
from model.settings.colours import colour_list, q_colour_list
from model.settings.isotope_reference_materials import reference_material_dictionary
from model.settings.methods_from_isotopes import list_of_methods
from model.spot import Spot

from model.spot import SpotAttribute

from model.isotopes import Isotope

from model.maths import calculate_cap_value_and_uncertainty
from model.settings.methods_from_isotopes import S33_S32, S34_S32, S36_S32


class SidrsModel:
    def __init__(self, signals):
        self.spots = []
        self.data = {}
        self.analytical_condition_data = None
        self.samples_by_name = {}
        self.signals = signals
        self.list_of_sample_names = []
        self.imported_files = []
        self.number_of_cycles = None
        self.element = None
        self.isotopes = None
        self.material = None
        self.primary_reference_material = None
        self.secondary_reference_material = None
        self.primary_rm_deltas_by_ratio = {}
        self.statsmodel_result_by_ratio = {}
        self.statsmodel_curvilinear_result_by_ratio = {}
        self.statsmodel_multiple_linear_result_by_ratio = {}
        self.t_zero = None
        self.drift_coefficient_by_ratio = {}
        self.drift_y_intercept_by_ratio = {}
        self.drift_correction_type_by_ratio = {}

        self.method = None

        self.signals.isotopesInput.connect(self._isotopes_input)
        self.signals.materialInput.connect(self._material_input)
        self.signals.sampleNamesUpdated.connect(self._sample_names_updated)
        self.signals.referenceMaterialsInput.connect(self._reference_material_tag_samples)
        self.signals.spotAndCycleFlagged.connect(self._remove_cycle_from_spot)
        self.signals.recalculateNewCycleData.connect(self.recalculate_data_with_cycles_changed)
        self.signals.recalculateNewSpotData.connect(self.recalculate_data)
        self.signals.driftCorrectionChanged.connect(self.recalculate_data_with_drift_correction_changed)
        self.signals.multipleLinearRegressionFactorsInput.connect(self.characterise_multiple_linear_regression)
        self.signals.clearAllData.connect(self.clear_all_data_and_methods)

    #################
    ### Importing ###
    #################

    def import_all_files(self, filenames):
        print("import all files")
        # self.sample_names_from_filenames(filenames)
        for filename in filenames:
            if filename in self.imported_files:
                raise Exception("The file: " + filename + " has already been imported")
            spot = self._parse_asc_file_into_data(filename)
            self.spots.append(spot)
            self.imported_files.append(filename)

        if len({spot.number_of_cycles for spot in self.spots}) != 1:
            raise Exception("Spots have different numbers of cycles - you may have input two separate sessions")

        self.number_of_cycles = self.spots[0].number_of_cycles

        filename_for_analytical_conditions = filenames[0]
        self.analytical_condition_data = self._parse_asc_file_into_analytical_conditions_data(
            filename_for_analytical_conditions)

    def _parse_asc_file_into_data(self, filename):
        with open(filename) as file:
            csv_data = csv.reader(file, delimiter='\t')
            count = 0
            data_for_spot = []
            for line in csv_data:
                count += 1
                for i in line:
                    line[line.index(i)] = str.strip(i)
                data_for_spot.append(line)
        spot = Spot(filename, data_for_spot, self.isotopes)
        return spot

    def _parse_asc_file_into_analytical_conditions_data(self, filename):
        with open(filename) as file:
            csv_data = csv.reader(file, delimiter='\t')
            count = 0
            data = []
            for line in csv_data:
                count += 1
                for i in line:
                    line[line.index(i)] = str.strip(i)
                data.append(line)

        analytical_condition_data = get_analytical_conditions_data_from_asc_file(data)
        return analytical_condition_data

    def sample_names_from_filenames(self, filenames):
        full_sample_names = []
        for filename in filenames:
            parts = re.split('@|\\.|/', filename)
            full_sample_name = parts[-3]
            if full_sample_name not in full_sample_names:
                full_sample_names.append(full_sample_name)

        split_names = [re.split('-|_', full_sample_name) for full_sample_name in full_sample_names]

        # TODO - at the end remove the self
        self.sample_names = []
        for i in range(len(split_names)):
            if split_names[i - 1][-1] != split_names[i][-1]:
                if split_names[i][-1] not in self.list_of_sample_names:
                    self.sample_names.append(split_names[i][-1])
        print("sampleNamesUpdated")
        self.signals.sampleNamesUpdated.emit(self.sample_names)

    def _create_samples_from_sample_names(self, spots):
        for sample_name in self.list_of_sample_names:
            self.samples_by_name[sample_name] = Sample(sample_name)
            for spot in spots:
                if sample_name in spot.full_sample_name:
                    self.samples_by_name[sample_name].spots.append(spot)

        for i, sample in enumerate(self.samples_by_name.values()):
            sample.colour = colour_list[i]
            sample.q_colour = q_colour_list[i]

    ##################
    ### Processing ###
    ##################

    def process_data(self):
        print("Processing...")
        self._create_samples_from_sample_names(self.spots)
        primary_reference_material_exists = False
        secondary_reference_material_accounted_for = False
        for i, sample in enumerate(self.samples_by_name.values()):
            if sample.name == self.primary_reference_material:
                sample.is_primary_reference_material = True
                primary_reference_material_exists = True
                number_of_primary_rm_spots = len(sample.spots)
                sample.colour = "black"
                sample.q_colour = QColor(0, 0, 0, 100)
            elif sample.name == self.secondary_reference_material:
                sample.is_secondary_reference_material = True
                secondary_reference_material_accounted_for = True
                sample.colour = "grey"
                sample.q_colour = QColor(128, 128, 128, 100)

            if self.secondary_reference_material == "No secondary reference material":
                secondary_reference_material_accounted_for = True

        if not primary_reference_material_exists or not secondary_reference_material_accounted_for:
            raise Exception("The reference materials selected does not match your sample data")

        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.calculate_relative_secondary_ion_yield()
                spot.calculate_raw_isotope_ratios(self.method)
                spot.calculate_mean_st_error_for_isotope_ratios()
                spot.calculate_raw_delta_for_isotope_ratio(self.element)

    def drift_correction_process(self):
        for sample in self.samples_by_name.values():
            if sample.is_primary_reference_material:
                primary_rm = sample

        for ratio in self.method.ratios:

            self.characterise_linear_drift(ratio, primary_rm.spots)
            if ratio.name() == "36S/32S":
                self.characterise_curvilinear_drift(ratio, primary_rm.spots)

            if self.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.NONE:
                self.calculate_data_not_drift_corrected(ratio)
            elif self.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.LIN:
                self.correct_data_for_linear_drift(ratio)
            elif self.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.QUAD:
                print("Not yet it's not")
            else:
                raise Exception("There is not a valid input drift type.")

    def correct_data_for_linear_drift(self, ratio):
        drift_correction_coef = float(self.drift_coefficient_by_ratio[ratio])
        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                timestamp = time.mktime(spot.datetime.timetuple())
                if ratio.has_delta:
                    [delta, uncertainty] = spot.not_corrected_deltas[ratio]
                    spot.drift_corrected_deltas[ratio] = drift_correction(
                        x=timestamp,
                        y=delta,
                        dy=uncertainty,
                        drift_coefficient=drift_correction_coef,
                        zero_time=self.t_zero)
                else:
                    [ratio_value, uncertainty] = spot.mean_two_st_error_isotope_ratios[ratio]
                    spot.drift_corrected_ratio_values_by_ratio[ratio] = drift_correction(
                        x=timestamp,
                        y=ratio_value,
                        dy=uncertainty,
                        drift_coefficient=drift_correction_coef,
                        zero_time=self.t_zero)

    def calculate_data_not_drift_corrected(self, ratio):
        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                if ratio.has_delta:
                    spot.drift_corrected_deltas[ratio] = spot.not_corrected_deltas[ratio]
                else:
                    spot.drift_corrected_ratio_values_by_ratio[ratio] = spot.mean_two_st_error_isotope_ratios[ratio]

    def get_data_for_drift_characterisation_input(self, ratio, spots):
        times = []
        values = []
        for spot in spots:
            if spot.is_flagged:
                continue
            timestamp = time.mktime(spot.datetime.timetuple())
            if ratio.has_delta:
                [value, _uncertainty] = spot.not_corrected_deltas[ratio]
            else:
                [value, _uncertainty] = spot.mean_two_st_error_isotope_ratios[ratio]

            times.append(timestamp)
            values.append(value)

        return values, times

    def characterise_linear_drift(self, ratio, spots):

        values, times = self.get_data_for_drift_characterisation_input(ratio, spots)
        self.primary_rm_deltas_by_ratio[ratio] = values

        Y = values
        # adding a column of '1s' for statsmodels to the array 'times'
        X = sm.add_constant(times)

        self.statsmodel_result_by_ratio[ratio] = sm.OLS(Y, X).fit()
        self.drift_y_intercept_by_ratio[ratio], self.drift_coefficient_by_ratio[
            ratio] = self.statsmodel_result_by_ratio[ratio].params

        self.t_zero = np.median(times)

    def characterise_curvilinear_drift(self, ratio, spots):
        values, times = self.get_data_for_drift_characterisation_input(ratio, spots)
        Y = values
        x1 = times
        x2 = [t ** 2 for t in times]
        # making the factors into an array and adding a constant
        x_array = np.column_stack((x1, x2))
        X = sm.add_constant(x_array)
        self.statsmodel_curvilinear_result_by_ratio[ratio] = sm.OLS(Y, X).fit()
        return

    def characterise_multiple_linear_regression(self, factors, ratio):
        print("hi")
        for factor in factors:
            print(factor == SpotAttribute.TIME)
        spots_to_use = [spot for spot in self.spots if not spot.is_flagged]
        values = []
        uncertainties = []
        for spot in spots_to_use:
            if ratio.has_delta:
                [value, uncertainty] = spot.not_corrected_deltas[ratio]
            else:
                [value, uncertainty] = spot.mean_two_st_error_isotope_ratios[ratio]
            values.append(value)
            uncertainties.append(uncertainty)

        lists_of_independent_variables = []
        for factor in factors:
            if factor == SpotAttribute.TIME:
                times = []
                for spot in spots_to_use:
                    timestamp = time.mktime(spot.datetime.timetuple())
                    times.append(timestamp)
                lists_of_independent_variables.append(times)
            elif factor == SpotAttribute.DTFAX:
                dtfa_xs = []
                for spot in spots_to_use:
                    dtfa_xs.append(spot.dtfa_x)
                lists_of_independent_variables.append(dtfa_xs)
            elif factor == SpotAttribute.DTFAY:
                dtfa_ys = []
                for spot in spots_to_use:
                    dtfa_ys.append(spot.dtfa_y)
                lists_of_independent_variables.append(dtfa_ys)
            elif factor == SpotAttribute.DISTANCE:
                distances = []
                for spot in spots_to_use:
                    distances.append(spot.distance_from_mount_centre)
                lists_of_independent_variables.append(distances)
            array_of_independent_variables = np.array(lists_of_independent_variables)
            X = np.column_stack(array_of_independent_variables)
            Y = values
            X = sm.add_constant(X)

            self.statsmodel_multiple_linear_result_by_ratio[ratio] = sm.OLS(Y, X).fit()
            print(self.statsmodel_multiple_linear_result_by_ratio[ratio].summary())

    def SIMS_correction_process(self):
        # This correction method is described fully in  Kita et al., 2009
        # How does the ratio process work? Can you have different corrections for each one?
        for ratio in self.method.ratios:
            for sample in self.samples_by_name.values():
                if sample.is_primary_reference_material:
                    primary_rm = sample

            primary_rm_spot_data = [spot.drift_corrected_deltas[ratio][0] for spot in primary_rm.spots if
                                    not spot.is_flagged and ratio.has_delta]

            if primary_rm_spot_data:
                primary_rm_mean = np.mean(primary_rm_spot_data)
                primary_uncertainty = np.std(primary_rm_spot_data)

                alpha_sims, alpha_sims_uncertainty = calculate_sims_alpha(
                    primary_reference_material_mean_delta=primary_rm_mean,
                    primary_reference_material_st_dev=primary_uncertainty,
                    externally_measured_primary_reference_value_and_uncertainty=
                    self.primary_rm_values_by_ratio[ratio])

            for sample in self.samples_by_name.values():
                for spot in sample.spots:

                    if ratio.has_delta:
                        data = spot.drift_corrected_deltas[ratio]
                        spot.alpha_corrected_data[ratio] = calculate_alpha_correction(data, alpha_sims,
                                                                                                 alpha_sims_uncertainty)
                    else:
                        spot.alpha_corrected_data[ratio] = spot.drift_corrected_ratio_values_by_ratio[ratio]

    def calculate_cap_values_S33(self):
        print("Calculating cap33")
        for sample in self.samples_by_name.values():
            if sample.is_primary_reference_material:
                primary_rm = sample

                primary_rm_spot_data_33 = [spot.drift_corrected_deltas[S33_S32][0] for spot in
                                           primary_rm.spots if
                                           not spot.is_flagged]
                primary_rm_spot_data_34 = [spot.drift_corrected_deltas[S34_S32][0] for spot in
                                           primary_rm.spots if
                                           not spot.is_flagged]
                array_33 = np.array(primary_rm_spot_data_33)
                array_34 = np.array(primary_rm_spot_data_34)
                primary_covariance_33_34 = np.cov(array_33, array_34)[0][1]

        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.cap_data_S33 = calculate_cap_value_and_uncertainty(
                    delta_value_x=spot.alpha_corrected_data[S33_S32][0],
                    uncertainty_x=spot.alpha_corrected_data[S33_S32][1],
                    delta_value_relative=spot.alpha_corrected_data[S34_S32][0],
                    uncertainty_relative=spot.alpha_corrected_data[S34_S32][1],
                    MDF=0.515,
                    reference_material_covariance=primary_covariance_33_34)

    def calculate_cap_values_S36(self):
        print("Calculating cap")
        for sample in self.samples_by_name.values():
            if sample.is_primary_reference_material:
                primary_rm = sample

                primary_rm_spot_data_34 = [spot.drift_corrected_deltas[S34_S32][0] for spot in
                                           primary_rm.spots if
                                           not spot.is_flagged]
                primary_rm_spot_data_36 = [spot.drift_corrected_deltas[S36_S32][0] for spot in
                                           primary_rm.spots if
                                           not spot.is_flagged]

                array_34 = np.array(primary_rm_spot_data_34)
                array_36 = np.array(primary_rm_spot_data_36)
                primary_covariance_36_34 = np.cov(array_36, array_34)[0][1]

        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.cap_data_S36 = calculate_cap_value_and_uncertainty(
                    delta_value_x=spot.alpha_corrected_data[S36_S32][0],
                    uncertainty_x=spot.alpha_corrected_data[S36_S32][1],
                    delta_value_relative=spot.alpha_corrected_data[S34_S32][0],
                    uncertainty_relative=spot.alpha_corrected_data[S34_S32][1],
                    MDF=1.91,
                    reference_material_covariance=primary_covariance_36_34)

    ###############
    ### Signals ###
    ###############

    def _isotopes_input(self, isotopes, enum):
        self.isotopes = isotopes
        self.element = enum
        self.method = self.create_method_dictionary_from_isotopes(self.isotopes)
        for ratio in self.method.ratios:
            self.drift_correction_type_by_ratio[ratio] = DriftCorrectionType.NONE

    def _material_input(self, material):
        self.material = material

    def _sample_names_updated(self, sample_names):
        self.list_of_sample_names = sample_names

    def _reference_material_tag_samples(self, primary_reference_material, secondary_reference_material):
        self.primary_reference_material = primary_reference_material
        self.secondary_reference_material = secondary_reference_material

        # TODO refactor this bit

        self.primary_rm_values_by_ratio = reference_material_dictionary[
            (self.element, self.material, primary_reference_material)]
        if self.secondary_reference_material == "No secondary reference material":
            self.secondary_rm_values_by_ratio = None
        else:
            self.secondary_rm_values_by_ratio = reference_material_dictionary[
                (self.element, self.material, primary_reference_material)]

    def create_method_dictionary_from_isotopes(self, isotopes):
        for method in list_of_methods:
            if set(isotopes) == set(method.isotopes):
                return method

        raise Exception(
            "The isotopes selected are not currently part of a method. For instructions on how to add methods view "
            "the HACKING.md file.")

    def recalculate_data_with_cycles_changed(self):
        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.calculate_mean_and_st_dev_for_isotope_ratio_user_picked_outliers()
                spot.calculate_raw_delta_for_isotope_ratio(self.element)

        self.drift_correction_process()
        self.SIMS_correction_process()
        if Isotope.S33 in self.isotopes:
            self.calculate_cap_values_S33()
        if Isotope.S36 in self.isotopes:
            self.calculate_cap_values_S36()

    def _remove_cycle_from_spot(self, spot, cycle_number, is_flagged, ratio):
        spot.exclude_cycle_information_update(cycle_number, is_flagged, ratio)

    def recalculate_data(self):
        self.drift_correction_process()
        self.SIMS_correction_process()
        self.signals.replotAndTabulateRecalculatedData.emit()

    def recalculate_data_with_drift_correction_changed(self, ratio, drift_correction_type):
        self.drift_correction_type_by_ratio[ratio] = drift_correction_type
        self.recalculate_data()

    def clear_all_data_and_methods(self):
        self.spots = []
        self.data.clear()
        self.analytical_condition_data = None
        self.samples_by_name.clear()
        self.list_of_sample_names = []
        self.imported_files = []
        self.number_of_cycles = None
        self.element = None
        self.isotopes = None
        self.material = None
        self.primary_reference_material = None
        self.secondary_reference_material = None
        self.primary_rm_deltas_by_ratio.clear()
        self.statsmodel_result_by_ratio.clear()
        self.t_zero = None
        self.drift_coefficient_by_ratio.clear()
        self.drift_y_intercept_by_ratio.clear()
        self.drift_correction_type_by_ratio.clear()

        self.method = None

        self.signals.dataCleared.emit()
