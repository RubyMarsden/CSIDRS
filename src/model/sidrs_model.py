from src.model.spot import Spot
import csv


class SidrsModel:
    def __init__(self):
        self.data = {}
        self.imported_files = []

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
            for line in csv_data:
                for i in line:
                    line[line.index(i)] = str.strip(i)
                print(line)

        spot = Spot(filename, csv_data)
        print("name = ", spot.sample_name, "id = ", spot.id)

        return spot
