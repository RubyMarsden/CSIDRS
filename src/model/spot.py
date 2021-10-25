import re

from src.model.mass_peak import MassPeak
from src.model.settings.asc_file_settings_general import *
from src.model.get_data_from_import import get_data_from_old_asc


class Spot:
    def __init__(self, filename, spot_data):
        self.filename = filename
        parts = re.split('@|\\.|/', self.filename)
        self.sample_name, self.id = parts[-3], parts[-2]
        self.spot_data = spot_data
        self.date = self.spot_data[DATE_INDEX[0]][DATE_INDEX[1]]



        # TODO this should come from the view
        self.mass_peak_names = ["32S", "33S", "34S"]

        self.mass_peaks = {}

        for mass_peak_name in self.mass_peak_names:
            raw_cps_data, detector_data = get_data_from_old_asc(self.spot_data, mass_peak_name)
            mass_peak = MassPeak(
                self.sample_name,
                self.id,
                mass_peak_name,
                raw_cps_data,
                detector_data
            )

            self.mass_peaks[mass_peak_name] = [mass_peak]



