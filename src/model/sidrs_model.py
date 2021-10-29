import re

from src.model.spot import Spot
import csv


class SidrsModel:
    def __init__(self, signals):
        self.data = {}
        self.signals = signals
        self.list_of_sample_names = []
        self.imported_files = []
        self.isotopes = None
        self.material = None

        self.signals.isotopesInput.connect(self._isotopes_input)
        self.signals.materialInput.connect(self._material_input)

    #################
    ### Importing ###
    #################

    def import_all_files(self, filenames):
        spots = []
        self.list_of_sample_names = self.sample_names_from_filenames(filenames)
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
        print("name = ", spot.sample_name, "id = ", spot.id, "datetime = ", spot.datetime)

        return spot

    def sample_names_from_filenames(self, filenames):
        full_sample_names = []
        for filename in filenames:
            parts = re.split('@|\\.|/', filename)
            full_sample_name = parts[-3]
            if full_sample_name not in full_sample_names:
                full_sample_names.append(full_sample_name)

        print(full_sample_names)
        split_names = []
        for full_sample_name in full_sample_names:
            name_parts = re.split('-|_', full_sample_name)
            split_names.append(name_parts)

        for j in range(len(split_names[0])):
            for i in range(len(split_names)):
                if split_names[i-1][j] != split_names[i][j]:
                    self.list_of_sample_names.append(split_names[i][j])

        print(self.list_of_sample_names)
        return self.list_of_sample_names

    ###############
    ### Signals ###
    ###############

    def _isotopes_input(self, isotopes, enum):
        self.isotopes = isotopes
        self.element = enum

    def _material_input(self, material):
        self.material = material
