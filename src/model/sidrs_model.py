import csv
import re
import time

import matplotlib
import numpy as np
# from ltsfit.lts_linefit import lts_linefit
import statsmodels.api as sm

from src.model.drift_correction_type import DriftCorrectionType
from src.model.get_data_from_import import get_block_number_from_old_asc, \
    get_analytical_conditions_data_from_old_asc_file
from src.model.maths import drift_correction, calculate_sims_alpha, calculate_alpha_correction, \
    calculate_probability_one_outlier
from src.model.sample import Sample
from src.model.settings.colours import colour_list, q_colour_list
from src.model.settings.isotope_reference_materials import reference_material_dictionary
from src.model.settings.methods_from_isotopes import list_of_methods
from src.model.spot import Spot


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
        self.cycle_outlier_probability_list = []
        self.primary_rm_outlier_probability_list = []
        self.primary_rm_deltas_by_ratio = {}
        self.statsmodel_result_by_ratio = {}
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
        self.signals.clearAllData.connect(self.clear_all_data_and_methods)

    #################
    ### Importing ###
    #################

    def import_all_files(self, filenames):
        self.sample_names_from_filenames(filenames)
        for filename in filenames:
            if filename in self.imported_files:
                raise Exception("The file: " + filename + " has already been imported")
            spot = self._parse_asc_file_into_data(filename)
            self.spots.append(spot)
            self.imported_files.append(filename)

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
        # In the asc file cycles are labelled blocks
        self.number_of_cycles = get_block_number_from_old_asc(data_for_spot)
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

        analytical_condition_data = get_analytical_conditions_data_from_old_asc_file(data)
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
                self.sample_names.append(split_names[i][-1])
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
        for sample in self.samples_by_name.values():
            if sample.name == self.primary_reference_material:
                sample.is_primary_reference_material = True
                primary_reference_material_exists = True
                number_of_primary_rm_spots = len(sample.spots)
            elif sample.name == self.secondary_reference_material:
                sample.is_secondary_reference_material = True
                secondary_reference_material_accounted_for = True

            if self.secondary_reference_material == "No secondary reference material":
                secondary_reference_material_accounted_for = True

        if not primary_reference_material_exists or not secondary_reference_material_accounted_for:
            raise Exception("The reference materials selected does not match your sample data")

        self.cycle_outlier_probability_list = [calculate_probability_one_outlier(self.number_of_cycles)]
        self.primary_rm_outlier_probability_list = [calculate_probability_one_outlier(number_of_primary_rm_spots)]

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
            elif sample.is_secondary_reference_material:
                secondary_rm = sample
            else:
                continue

        for ratio in self.method.ratios:

            self.characterise_linear_drift(ratio, primary_rm.spots)
            if ratio.name == "36S/32S":
                self.characterise_curvilinear_drift(ratio, primary_rm.spots)
            else:
                self.characterise_curvilinear_drift(ratio, None)

            self.characterise_multiple_linear_regression(ratio, primary_rm.spots, factors=["dtfa-x", "time"])

            if self.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.NONE:
                self.calculate_data_not_drift_corrected(ratio)
            elif self.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.LIN:
                self.correct_data_for_drift(ratio)
            elif self.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.QUAD:
                print("Not yet it's not")
            else:
                raise Exception("There is not an input valid drift type.")

    def correct_data_for_drift(self, ratio):
        drift_correction_coef = float(self.drift_coefficient_by_ratio[ratio])
        drift_correction_intercept = self.drift_y_intercept_by_ratio[ratio]
        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                if spot.standard_ratios[ratio]:
                    [delta, uncertainty] = spot.not_corrected_deltas[ratio.delta_name]
                    timestamp = time.mktime(spot.datetime.timetuple())
                    spot.drift_corrected_deltas[ratio.delta_name] = drift_correction(
                        x=timestamp, y=delta,
                        dy=uncertainty,
                        drift_coefficient=drift_correction_coef,
                        zero_time=self.t_zero)
                else:
                    [ratio_value, uncertainty] = spot.mean_two_st_error_isotope_ratios[ratio]
                    timestamp = time.mktime(spot.datetime.timetuple())
                    spot.drift_corrected_ratio_values_by_ratio[ratio] = drift_correction(
                        x=timestamp,
                        y=ratio_value,
                        dy=uncertainty,
                        drift_coefficient=drift_correction_coef,
                        zero_time=self.t_zero)

    def calculate_data_not_drift_corrected(self, ratio):
        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.drift_corrected_deltas[ratio.delta_name] = spot.not_corrected_deltas[ratio.delta_name]

    def characterise_linear_drift(self, ratio, spots):
        times = []
        deltas = []
        delta_uncertainties = []
        for spot in spots:
            timestamp = time.mktime(spot.datetime.timetuple())
            if spot.standard_ratios[ratio] and spot.is_flagged is False:
                [delta, uncertainty] = spot.not_corrected_deltas[ratio.delta_name]
                times.append(timestamp)
                deltas.append(delta)
                delta_uncertainties.append(uncertainty)

            elif not spot.standard_ratios[ratio] and spot.is_flagged is False:
                [delta, uncertainty] = spot.mean_two_st_error_isotope_ratios[ratio]
                times.append(timestamp)
                deltas.append(delta)
                delta_uncertainties.append(uncertainty)

        self.primary_rm_deltas_by_ratio[ratio] = deltas

        if self.primary_rm_deltas_by_ratio[ratio]:
            X = sm.add_constant(times)

            self.statsmodel_result_by_ratio[ratio] = sm.OLS(self.primary_rm_deltas_by_ratio[ratio], X).fit()
            self.drift_y_intercept_by_ratio[ratio], self.drift_coefficient_by_ratio[
                ratio] = self.statsmodel_result_by_ratio[ratio].params

            self.t_zero = np.median(times)

        else:
            self.drift_y_intercept_by_ratio[ratio], self.drift_coefficient_by_ratio[ratio] = None, None
            for sample in self.samples_by_name.values():
                for spot in sample.spots:
                    spot.drift_corrected_deltas[ratio.delta_name] = spot.not_corrected_deltas[ratio.delta_name]

    def characterise_curvilinear_drift(self, ratio, spots):
        return

    def characterise_multiple_linear_regression(self, ratio, spots, factors):
        return

    def SIMS_correction_process(self):
        # This correction method is described fully in  Kita et al., 2009
        # How does the ratio process work? Can you have different corrections for each one?
        for ratio in self.method.ratios:
            for sample in self.samples_by_name.values():
                if sample.is_primary_reference_material:
                    primary_rm = sample

            primary_rm_spot_data = [spot.drift_corrected_deltas[ratio.delta_name][0] for spot in primary_rm.spots if
                                    not spot.is_flagged and spot.standard_ratios[ratio]]

            if primary_rm_spot_data:
                primary_rm_mean = np.mean(primary_rm_spot_data)
                primary_uncertainty = np.std(primary_rm_spot_data)

                alpha_sims = calculate_sims_alpha(primary_reference_material_mean_delta=primary_rm_mean,
                                                  externally_measured_primary_reference_value_and_uncertainty=
                                                  self.primary_rm_values_by_ratio[ratio])

            for sample in self.samples_by_name.values():
                for spot in sample.spots:
                    data = spot.drift_corrected_deltas[ratio.delta_name]
                    if data[0]:
                        spot.alpha_corrected_data[ratio.delta_name] = calculate_alpha_correction(data, alpha_sims,
                                                                                                 primary_uncertainty)
                    else:
                        spot.alpha_corrected_data[ratio.delta_name] = spot.not_corrected_deltas[ratio.delta_name]

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
        self.cycle_outlier_probability_list = []
        self.primary_rm_outlier_probability_list = []
        self.primary_rm_deltas_by_ratio.clear()
        self.statsmodel_result_by_ratio.clear()
        self.t_zero = None
        self.drift_coefficient_by_ratio.clear()
        self.drift_y_intercept_by_ratio.clear()
        self.drift_correction_type_by_ratio.clear()

        self.method = None

        self.signals.dataCleared.emit()
