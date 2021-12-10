import re
import time

import numpy as np
# from ltsfit.lts_linefit import lts_linefit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm

from src.model.elements import Element
from src.model.get_data_from_import import get_block_number_from_old_asc
from src.model.maths import drift_correction, calculate_sims_alpha, calculate_alpha_correction, \
    calculate_probability_one_outlier
from src.model.sample import Sample
from src.model.settings.colours import colour_list, q_colour_list
from src.model.settings.isotope_reference_materials import oxygen_zircon_reference_material_dict, \
    sulphur_pyrite_reference_material_dict
from src.model.settings.methods_from_isotopes import list_of_methods
from src.model.spot import Spot
import csv


class SidrsModel:
    def __init__(self, signals):
        self.spots = []
        self.data = {}
        self.samples_by_name = {}
        self.signals = signals
        self.list_of_sample_names = []
        self.imported_files = []
        self.number_of_cycles = None
        self.isotopes = None
        self.material = None
        self.primary_reference_material = None
        self.secondary_reference_material = None
        self.cycle_outlier_probability_list = []
        self.primary_rm_outlier_probability_list = []
        self.drift_coefficient = None
        self.drift_y_intercept = None

        self.method = None

        self.signals.isotopesInput.connect(self._isotopes_input)
        self.signals.materialInput.connect(self._material_input)
        self.signals.sampleNamesUpdated.connect(self._sample_names_updated)
        self.signals.referenceMaterialsInput.connect(self._reference_material_tag_samples)
        self.signals.spotAndCycleFlagged.connect(self._remove_cycle_from_spot)
        self.signals.recalculateNewCycleData.connect(self.recalculate_data_with_cycles_changed)
        self.signals.recalculateNewSpotData.connect(self.recalculate_data_with_spots_excluded)

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
        for j in range(len(split_names[0])):
            for i in range(len(split_names)):
                if split_names[i - 1][j] != split_names[i][j]:
                    self.sample_names.append(split_names[i][j])
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
        secondary_reference_material_exists = False
        for sample in self.samples_by_name.values():
            if sample.name == self.primary_reference_material:
                sample.is_primary_reference_material = True
                primary_reference_material_exists = True
                number_of_primary_rm_spots = len(sample.spots)
            elif sample.name == self.secondary_reference_material:
                sample.is_secondary_reference_material = True
                secondary_reference_material_exists = True

        if primary_reference_material_exists and secondary_reference_material_exists:
            print("fix this")
        else:
            raise Exception("The reference materials selected does not match your sample data")

        self.cycle_outlier_probability_list = [calculate_probability_one_outlier(self.number_of_cycles)]
        self.primary_rm_outlier_probability_list = [calculate_probability_one_outlier(number_of_primary_rm_spots)]
        print(self.cycle_outlier_probability_list)
        print(self.primary_rm_outlier_probability_list)

        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.calculate_relative_secondary_ion_yield()
                spot.calculate_raw_isotope_ratios(self.method)
                spot.calculate_mean_st_error_for_isotope_ratios()
                spot.calculate_raw_delta_for_isotope_ratio(self.element)

    def drift_correction_process(self):
        for ratio in self.method.ratios:

            for sample in self.samples_by_name.values():
                if sample.is_primary_reference_material:
                    primary_rm = sample
                elif sample.is_secondary_reference_material:
                    secondary_rm = sample
                else:
                    continue

            primary_times = []
            primary_time_uncertainties = []
            primary_deltas = []
            primary_delta_uncertainties = []
            for spot in primary_rm.spots:
                if spot.is_flagged is False:
                    timestamp = time.mktime(spot.datetime.timetuple())
                    primary_times.append(timestamp)
                    primary_time_uncertainties.append(0.1)
                    [delta, uncertainty] = spot.not_corrected_deltas[ratio.delta_name]
                    primary_deltas.append(delta)
                    primary_delta_uncertainties.append(uncertainty)
            xs = np.array(primary_times).reshape(-1, 1)
            dxs = np.array(primary_time_uncertainties)
            ys = np.array(primary_deltas)
            dys = np.array(primary_delta_uncertainties)

            regressor = LinearRegression()
            regressor.fit(xs, ys)
            score = regressor.score(xs, ys)
            coeff = regressor.coef_
            intercept = regressor.intercept_
            print(score)
            print(coeff)
            print(intercept)

            X = sm.add_constant(primary_times)

            statsmodel_result = sm.OLS(primary_deltas, X).fit()
            print(statsmodel_result.summary())
            self.drift_y_intercept, self.drift_coefficient = statsmodel_result.params

            t_zero = np.median(primary_times)

            if score > 0.25:
                print("linear fit")
                drift_correction_coef = float(coeff)
                drift_correction_intercept = intercept
                for sample in self.samples_by_name.values():
                    for spot in sample.spots:
                        [delta, uncertainty] = spot.not_corrected_deltas[ratio.delta_name]
                        timestamp = time.mktime(spot.datetime.timetuple())
                        spot.drift_corrected_deltas[ratio.delta_name] = drift_correction(x=timestamp, y=delta,
                                                                                         dy=uncertainty,
                                                                                         drift_coefficient=drift_correction_coef,
                                                                                         zero_time=t_zero)
            else:
                print("no fit")
                for sample in self.samples_by_name.values():
                    for spot in sample.spots:
                        spot.drift_corrected_deltas[ratio.delta_name] = spot.not_corrected_deltas[ratio.delta_name]

    def SIMS_correction_process(self):
        # This correction method is described fully in  Kita et al., 2009
        # How does the ratio process work? Can you have different corrections for each one?
        for ratio in self.method.ratios:
            for sample in self.samples_by_name.values():
                if sample.is_primary_reference_material:
                    primary_rm = sample

            spot_data = [spot.drift_corrected_deltas[ratio.delta_name][0] for spot in primary_rm.spots if
                         not spot.is_flagged]
            primary_rm_mean = np.mean(spot_data)
            primary_uncertainty = np.std(spot_data)

            alpha_sims = calculate_sims_alpha(primary_reference_material_mean_delta=primary_rm_mean,
                                              externally_measured_primary_reference_value_and_uncertainty=
                                              self.primary_rm_values_by_ratio[ratio])

            for sample in self.samples_by_name.values():
                for spot in sample.spots:
                    data = spot.drift_corrected_deltas[ratio.delta_name]
                    spot.alpha_corrected_data[ratio.delta_name] = calculate_alpha_correction(data, alpha_sims,
                                                                                             primary_uncertainty)

    ###############
    ### Signals ###
    ###############

    def _isotopes_input(self, isotopes, enum):
        self.isotopes = isotopes
        self.element = enum
        self.method = self.create_method_dictionary_from_isotopes(self.isotopes)

    def _material_input(self, material):
        self.material = material

    def _sample_names_updated(self, sample_names):
        self.list_of_sample_names = sample_names

    def _reference_material_tag_samples(self, primary_reference_material, secondary_reference_material):
        self.primary_reference_material = primary_reference_material
        self.secondary_reference_material = secondary_reference_material

        # TODO refactor this bit
        if self.element == Element.OXY:
            if self.material == "Zircon":
                self.primary_rm_values_by_ratio = oxygen_zircon_reference_material_dict[primary_reference_material]
                self.secondary_rm_values_by_ratio = oxygen_zircon_reference_material_dict[secondary_reference_material]

        elif self.element == Element.SUL:
            if self.material == "Pyrite":
                self.primary_rm_values_by_ratio = sulphur_pyrite_reference_material_dict[primary_reference_material]
                self.secondary_rm_values_by_ratio = sulphur_pyrite_reference_material_dict[secondary_reference_material]

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

    def recalculate_data_with_spots_excluded(self):
        self.drift_correction_process()
        self.SIMS_correction_process()
        self.on_data_recalculated()

    def on_data_recalculated(self):
        self.signals.replotAndTabulateRecalculatedData.emit()
