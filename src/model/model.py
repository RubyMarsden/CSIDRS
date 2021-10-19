
class SidrsModel:
    def __init__(self):
        self.data = {}
        self.imported_files = []

    #################
    ### Importing ###
    #################

    def import_all_runs(self, filenames):
        for filename in filenames:
            self.import_run_asc_file(filename)

    def import_run_asc_file(self, filename):
        if filename in self.imported_files:
            raise Exception("The file: " + filename + " has already been imported")



        self.imported_files.append(filename)

        return
