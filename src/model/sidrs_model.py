import csv
import time
from typing import Iterable, Dict

import numpy as np
import statsmodels.api as sm
from PyQt5.QtGui import QColor

from controllers.signals import signals
from model.calculation import CalculationResults
from model.drift_correction_type import DriftCorrectionType
from model.get_data_from_import import get_analytical_conditions_data_from_asc_file
from model.sample import Sample
from model.settings.colours import colour_list, q_colour_list
from model.settings.methods_from_isotopes import list_of_methods
from model.spot import Spot
from model.spot import SpotAttribute
from utils.csv_utils import write_csv_output
from utils.general_utils import find_longest_common_prefix_index, split_cameca_data_filename


class SidrsModel:
    def __init__(self):
        self.montecarlo_number = 1000000
        self.data = {}
        self.analytical_condition_data = None
        self.samples = []
        self.imported_files = []
        self.number_of_count_measurements = None
        self.element = None
        self.isotopes = None
        self.material = None
        self.primary_reference_material = None
        self.secondary_reference_material = None

        self.calculation_results = None

        self.drift_correction_type_by_ratio = {}

        self.method = None

        signals.isotopesInput.connect(self._isotopes_input)
        signals.materialInput.connect(self._material_input)
        signals.recalculateNewCycleData.connect(self.recalculate_data_with_cycles_changed)
        signals.multipleLinearRegressionFactorsInput.connect(self.characterise_multiple_linear_regression)

    #################
    ### Importing ###
    #################

    def import_all_files(self, filenames):
        print("import all files")
        duplicate_files = set(filenames).intersection(set(self.imported_files))
        if len(duplicate_files) != 0:
            raise Exception("The files: " + str(duplicate_files) + " have already been imported.")

        self.imported_files.extend(filenames)

        sample_names_by_filename = self._sample_names_from_filenames(filenames)
        unique_sample_names = set(sample_names_by_filename.values())
        sorted_sample_names = list(unique_sample_names)
        sorted_sample_names.sort()
        samples_by_name = {}
        for i, sample_name in enumerate(sorted_sample_names):
            sample = Sample(sample_name)
            sample.colour = colour_list[i]
            sample.q_colour = q_colour_list[i]
            samples_by_name[sample_name] = sample

        spots = []
        for filename in filenames:
            spot = self._parse_asc_file_into_data(filename)
            sample_name = sample_names_by_filename[filename]
            sample = samples_by_name[sample_name]
            sample.spots.append(spot)
            spots.append(spot)

        self.samples = list(samples_by_name.values())

        if len({spot.number_of_count_measurements for spot in spots}) != 1:
            raise Exception("Spots have different numbers of cycles - you may have input two separate sessions")

        self.number_of_count_measurements = spots[0].number_of_count_measurements

        filename_for_analytical_conditions = filenames[0]
        self.analytical_condition_data = self._parse_asc_file_into_analytical_conditions_data(
            filename_for_analytical_conditions)

        signals.importedFilesUpdated.emit()
        signals.sampleNamesUpdated.emit()

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

    def _sample_names_from_filenames(self, filenames):
        """
        :param filenames:
        :return: dictionary mapping filenames to samples names
        """
        full_sample_names = {}
        for filename in filenames:
            full_sample_name, spot_id = split_cameca_data_filename(filename)
            full_sample_names[filename] = full_sample_name

        unique_full_sample_names = set(full_sample_names.values())

        if len(unique_full_sample_names) == 0:
            raise Exception("No sample names have been imported - have you selected files?")
        elif len(unique_full_sample_names) == 1:
            sample_names = full_sample_names
        else:
            # Best effort attempt to strip common prefixes which are usually operator name and mount name.
            # If fails then returns the full samples names with prefixes.
            prefix_index = find_longest_common_prefix_index(unique_full_sample_names)
            sample_names = {}
            for filename, full_sample_name in full_sample_names.items():
                truncated_sample_name = full_sample_name[prefix_index:]
                if len(truncated_sample_name) > 0:
                    sample_names[filename] = truncated_sample_name
                else:
                    sample_names = full_sample_names
                    break
        return sample_names

    ##################
    ### Processing ###
    ##################

    def calculate_results(self):
        self.calculation_results = CalculationResults()
        samples = self.get_samples()
        primary_rm = self.get_primary_reference_material()

        self.calculation_results.calculate_raw_delta_values(samples, self.method, self.element, self.montecarlo_number)
        self.calculation_results.calculate_data_from_drift_correction_onwards(primary_rm, self.method, samples,
                                                                              self.drift_correction_type_by_ratio,
                                                                              self.element, self.material, self.montecarlo_number)

        signals.dataRecalculated.emit()

    def characterise_multiple_linear_regression(self, factors, ratio):

        spots_to_use = [spot for spot in self.get_all_spots() if not spot.is_flagged]
        values = []
        uncertainties = []
        for spot in spots_to_use:
            if ratio.has_delta:
                [value, uncertainty] = spot.not_corrected_deltas[ratio]
            else:
                [value, uncertainty] = spot.mean_st_dev_isotope_ratios[ratio]
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

    ###############
    ### Actions ###
    ###############

    def _isotopes_input(self, isotopes, enum):
        self.isotopes = isotopes
        self.element = enum
        self.method = self.create_method_dictionary_from_isotopes(self.isotopes)
        for ratio in self.method.ratios:
            self.drift_correction_type_by_ratio[ratio] = DriftCorrectionType.NONE

    def _material_input(self, material):
        self.material = material

    def get_samples(self) -> Iterable[Sample]:
        """
        :return: a complete list of sample objects
        """
        return self.samples

    def get_samples_by_name(self) -> Dict[str, Sample]:
        """
        :return: a dictionary of sample objects by name
        """
        return {sample.name: sample for sample in self.get_samples()}

    def get_all_spots(self) -> Iterable[Spot]:
        """
        :return: a complete list of spot objects
        """
        spots = []
        for sample in self.get_samples():
            spots.extend(sample.spots)
        return spots

    def _rename_samples(self, rename_operations):
        samples_by_name = self.get_samples_by_name()
        for (old_name, new_name) in rename_operations:
            samples_by_name[old_name].name = new_name

    def _merge_samples(self, merge_operations):
        samples_by_name = self.get_samples_by_name()

        for new_name, old_names in merge_operations:
            new_sample = Sample(new_name)
            new_sample.colour = samples_by_name[old_names[0]].colour
            new_sample.q_colour = samples_by_name[old_names[0]].q_colour

            for old_name in old_names:
                old_sample = samples_by_name[old_name]
                new_sample.spots.extend(old_sample.spots)
                self.samples.remove(old_sample)

            self.samples.append(new_sample)

    def rename_and_merge_samples(self, rename_operations, merge_operations):
        self._rename_samples(rename_operations)
        self._merge_samples(merge_operations)

        if len(rename_operations) > 0 or len(merge_operations) > 0:
            signals.sampleNamesUpdated.emit()

    def set_reference_materials(self, primary_reference_material_name, secondary_reference_material_name):
        for sample in self.get_samples():
            if sample.name == primary_reference_material_name:
                self.primary_reference_material = sample
                self.primary_reference_material.colour = "black"
                self.primary_reference_material.q_colour = QColor(0, 0, 0, 100)

        if self.primary_reference_material is None:
            raise Exception("The primary reference material selected does not match your sample data")

        if secondary_reference_material_name == "No secondary reference material":
            self.secondary_reference_material = None

        else:
            for sample in self.get_samples():
                if sample.name == secondary_reference_material_name:
                    self.secondary_reference_material = sample
                    self.secondary_reference_material.colour = "grey"
                    self.secondary_reference_material.q_colour = QColor(128, 128, 128, 100)

            if self.secondary_reference_material is None:
                raise Exception("The secondary reference material selected does not match your sample data")

    def create_method_dictionary_from_isotopes(self, isotopes):
        for method in list_of_methods:
            if set(isotopes) == set(method.isotopes):
                return method

        raise Exception("The isotopes selected are not currently part of a method. For instructions on how to add "
                        "methods view the HACKING.md file.")

    def recalculate_data_with_cycles_changed(self):
        primary_rm = self.get_primary_reference_material()
        samples = self.get_samples()
        self.calculation_results.calculate_raw_delta_with_changed_cycle_data(samples, self.element)

        self.calculation_results.calculate_data_from_drift_correction_onwards(primary_rm, self.method, samples,
                                                                              self.drift_correction_type_by_ratio,
                                                                              self.element, self.material, self.montecarlo_number)
        signals.dataRecalculated.emit()

    def remove_cycle_from_spot(self, spot, cycle_number, is_flagged, ratio):
        spot.cycle_flagging_information[ratio][cycle_number] = is_flagged

    def recalculate_data_with_drift_correction_changed(self, ratio, drift_correction_type):
        self.drift_correction_type_by_ratio[ratio] = drift_correction_type
        primary_rm = self.get_primary_reference_material()
        samples = self.get_samples()
        self.calculation_results.calculate_data_from_drift_correction_onwards(primary_rm, self.method, samples,
                                                                              self.drift_correction_type_by_ratio,
                                                                              self.element, self.material, self.montecarlo_number)
        signals.dataRecalculated.emit()

    def clear_all_data_and_methods(self):
        self.data.clear()
        self.analytical_condition_data = None
        self.samples = []
        self.imported_files = []
        self.number_of_count_measurements = None
        self.element = None
        self.isotopes = None
        self.material = None
        self.primary_reference_material = None
        self.secondary_reference_material = None
        self.calculation_results = None
        self.drift_correction_type_by_ratio.clear()

        self.method = None

        signals.dataCleared.emit()

    def export_cycle_data_csv(self, filename):
        method = self.method

        column_headers = ["Sample name", "Cycle number"]

        for ratio in method.ratios:
            column_headers.append(str(ratio.name()))
            column_headers.append("Excluded cycle")

        for isotope in method.isotopes:
            column_headers.append(str(isotope.name + " (cps)"))
            column_headers.append("Yield and background corrected " + isotope.isotope_name + " (cps)")

        rows = []
        for sample in self.get_samples():
            for spot in sample.spots:
                spot_name = str(sample.name + " " + spot.id)
                ratio = method.ratios[0]
                for i, value in enumerate(spot.cycle_flagging_information[ratio]):
                    row = [spot_name, i + 1]
                    for ratio in method.ratios:
                        boolean = spot.cycle_flagging_information[ratio][i]
                        if boolean:
                            excluded_info = "x"
                        else:
                            excluded_info = " "

                        row.extend([spot.raw_isotope_ratios[ratio][i], excluded_info])

                    for isotope in method.isotopes:
                        row.append(spot.mass_peaks[isotope].raw_cps_data[i])
                        row.append(spot.mass_peaks[isotope].detector_corrected_cps_data[i])

                    rows.append(row)

        write_csv_output(output_file=filename, headers=column_headers, rows=rows)

        write_csv_output(output_file=filename, headers=column_headers, rows=rows)

    def export_raw_data_csv(self, filename):
        method = self.method

        column_headers = ["Sample name"]
        for ratio in method.ratios:
            ratio_uncertainty_name = "uncertainty"
            column_headers.append(ratio.name())
            column_headers.append(ratio_uncertainty_name)
            if ratio.has_delta:
                column_headers.append(ratio.delta_name())
                column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        rows = []
        for sample in self.get_samples():
            for spot in sample.spots:
                row = [str(sample.name + " " + spot.id)]

                for ratio in method.ratios:
                    ratio_value, ratio_uncertainty = spot.mean_st_error_isotope_ratios[ratio]
                    row.append(ratio_value)
                    ratio_uncertainty_2 = ratio_uncertainty * 2
                    row.append(ratio_uncertainty_2)
                    if ratio.has_delta:
                        delta_data = spot.not_corrected_deltas[ratio]
                        delta = np.mean(delta_data)
                        delta_uncertainty = (np.std(delta_data)) * 2
                        row.append(delta)
                        row.append(delta_uncertainty)

                row.append(spot.dtfa_x)
                row.append(spot.dtfa_y)
                row.append(format(spot.secondary_ion_yield, ".5f"))
                row.append(spot.distance_from_mount_centre)

                rows.append(row)

        write_csv_output(output_file=filename, headers=column_headers, rows=rows)

    def export_corrected_data_csv(self, filename):

        method = self.method

        column_headers = ["Sample name", "Spot excluded"]
        for ratio in method.ratios:
            ratio_uncertainty_name = "uncertainty"
            if ratio.has_delta:
                column_headers.append("corrected " + ratio.delta_name())
                column_headers.append(ratio_uncertainty_name)
                column_headers.append("uncorrected " + ratio.delta_name())
                column_headers.append(ratio_uncertainty_name)
            else:
                column_headers.append("corrected " + ratio.name())
                column_headers.append(ratio_uncertainty_name)
            column_headers.append("uncorrected " + ratio.name())
            column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        rows = []
        for sample in self.get_samples():
            for spot in sample.spots:
                spot_excluded = "x" if spot.is_flagged else ""
                row = [str(sample.name + "-" + spot.id), spot_excluded]

                for ratio in method.ratios:
                    if ratio.has_delta:
                        delta, delta_uncertainty = np.mean(spot.alpha_corrected_data[ratio]), np.std(spot.alpha_corrected_data[ratio])
                        uncorrected_delta, uncorrected_delta_uncertainty = np.mean(spot.not_corrected_deltas[ratio]), np.std(spot.not_corrected_deltas[ratio])
                        row.append(delta)
                        row.append(delta_uncertainty)
                        row.append(uncorrected_delta)
                        row.append(uncorrected_delta_uncertainty)
                    else:
                        corrected_ratio, corrected_ratio_uncertainty = np.mean(spot.alpha_corrected_data[ratio]), np.std(spot.alpha_corrected_data[ratio])
                        row.append(corrected_ratio)
                        row.append(corrected_ratio_uncertainty)

                    [uncorrected_ratio, uncorrected_ratio_uncertainty] = spot.mean_st_error_isotope_ratios[ratio]
                    row.append(uncorrected_ratio)
                    row.append(uncorrected_ratio_uncertainty)

                row.append(spot.dtfa_x)
                row.append(spot.dtfa_y)
                row.append(format(spot.secondary_ion_yield, ".5f"))
                row.append(spot.distance_from_mount_centre)

                rows.append(row)

        write_csv_output(output_file=filename, headers=column_headers, rows=rows)

    def export_analytical_conditions_csv(self, filename):
        column_headers = []
        rows = [row for row in self.analytical_condition_data if row]

        write_csv_output(output_file=filename, headers=column_headers, rows=rows)

    def get_primary_reference_material(self):
        return self.primary_reference_material

