import re
import time

import numpy as np
from ltsfit.lts_linefit import lts_linefit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from src.model.elements import Element
from src.model.sample import Sample
from src.model.settings.colours import colour_list, q_colour_list
from src.model.settings.methods_from_isotopes import list_of_method_dictionaries
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
        self.isotopes = None
        self.material = None
        self.primary_reference_material = None
        self.secondary_reference_material = None

        self.method_dictionary = None

        self.signals.isotopesInput.connect(self._isotopes_input)
        self.signals.materialInput.connect(self._material_input)
        self.signals.sampleNamesUpdated.connect(self._sample_names_updated)
        self.signals.referenceMaterialsInput.connect(self._reference_material_tag_samples)

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
            elif sample.name == self.secondary_reference_material:
                sample.is_secondary_reference_material = True
                secondary_reference_material_exists = True

        if primary_reference_material_exists and secondary_reference_material_exists:
            print("fix this")
        else:
            raise Exception("The reference materials selected does not match your sample data")

        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.calculate_relative_secondary_ion_yield()
                spot.calculate_raw_isotope_ratios(self.method_dictionary)
                spot.calculate_mean_st_error_for_isotope_ratios()
                spot.calculate_raw_delta_for_isotope_ratio(self.element)

    def drift_correction_process(self):
        for ratio in self.method_dictionary["ratios"]:
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
            print(score)

            if score > 0.25:
                # https://doi.org/10.1093/mnras/stt562
                # Cappellari et al.(2013a, MNRAS, 432, 1709)
                p = lts_linefit(xs, dxs, ys, dys, pivot=np.median(xs))

                print(p.ab)

            else:
                print("no fit")

    ###############
    ### Signals ###
    ###############

    def _isotopes_input(self, isotopes, enum):
        self.isotopes = isotopes
        self.element = enum
        self.method_dictionary = self.create_method_dictionary_from_isotopes(self.isotopes)

    def _material_input(self, material):
        self.material = material

    def _sample_names_updated(self, sample_names):
        self.list_of_sample_names = sample_names

    def _reference_material_tag_samples(self, primary_reference_material, secondary_reference_material):
        self.primary_reference_material = primary_reference_material
        self.secondary_reference_material = secondary_reference_material

    def create_method_dictionary_from_isotopes(self, isotopes):
        for dictionary in list_of_method_dictionaries:
            if set(isotopes) == set(dictionary["isotopes"]):
                return dictionary

        raise Exception(
            "The isotopes selected are not currently part of a method. For instructions on how to add methods view the HACKING.md file.")
