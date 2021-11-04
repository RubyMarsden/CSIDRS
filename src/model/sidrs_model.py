import re

from src.model.sample import Sample
from src.model.spot import Spot
import csv


class SidrsModel:
    def __init__(self, signals):
        self.data = {}
        self.samples_by_name = {}
        self.signals = signals
        self.list_of_sample_names = []
        self.imported_files = []
        self.isotopes = None
        self.material = None

        self.signals.isotopesInput.connect(self._isotopes_input)
        self.signals.materialInput.connect(self._material_input)
        self.signals.sampleNamesUpdated.connect(self._sample_names_updated)

    #################
    ### Importing ###
    #################

    def import_all_files(self, filenames):
        spots = []
        self.sample_names_from_filenames(filenames)
        for filename in filenames:
            if filename in self.imported_files:
                raise Exception("The file: " + filename + " has already been imported")
            spot = self._parse_asc_file_into_data(filename)
            spots.append(spot)
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

        split_names = []
        for full_sample_name in full_sample_names:
            name_parts = re.split('-|_', full_sample_name)
            split_names.append(name_parts)

        sample_names = []
        for j in range(len(split_names[0])):
            for i in range(len(split_names)):
                if split_names[i - 1][j] != split_names[i][j]:
                    sample_names.append(split_names[i][j])
        self.signals.sampleNamesUpdated.emit(sample_names)

    def _create_samples_from_sample_names(self, spots):
        for sample_name in self.list_of_sample_names:
            self.samples_by_name[sample_name] = Sample(sample_name)
            for spot in spots:
                if spot.sample_name == sample_name:
                    self.samples_by_name[sample_name].spots.append(spot)

    ###############
    ### Signals ###
    ###############

    def _isotopes_input(self, isotopes, enum):
        self.isotopes = isotopes
        self.element = enum

    def _material_input(self, material):
        self.material = material

    def _sample_names_updated(self, sample_names):
        self.list_of_sample_names = sample_names
        print(self.list_of_sample_names)
