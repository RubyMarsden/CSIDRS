
class SidrsModel:
    def __init__(self):
        self.data = {}
        self.imported_files = []

    #################
    ### Importing ###
    #################

    def import_all_files(self, filenames):
        for filename in filenames:
            self.import_run_asc_file(filename)

    def import_run_asc_file(self, filename):
        if filename in self.imported_files:
            raise Exception("The file: " + filename + " has already been imported")
        self._parse_asc_file_into_data(filename)
        self.imported_files.append(filename)

    def _parse_asc_file_into_data(self, filename):
        file = open(filename, "rt")
        asc_file_data = file.readlines()
        print(asc_file_data)
        return
