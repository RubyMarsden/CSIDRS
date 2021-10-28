from src.model.spot import Spot
import csv


class SidrsModel:
    def __init__(self, signals):
        self.data = {}
        self.signals = signals
        self.imported_files = []
        self.mass_peak_names = None
        self.material = None

        self.signals.isotopesInput.connect(self._isotopes_input)
        self.signals.materialInput.connect(self._material_input)

    #################
    ### Importing ###
    #################

    def import_all_files(self, filenames):
        spots = []
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

        spot = Spot(filename, data_for_spot, self.mass_peak_names)
        print("name = ", spot.sample_name, "id = ", spot.id, "datetime = ", spot.datetime)

        return spot


    ###############
    ### Signals ###
    ###############

    def _isotopes_input(self, isotopes):
        self.mass_peak_names = isotopes

    def _material_input(self, material):
        self.material = material