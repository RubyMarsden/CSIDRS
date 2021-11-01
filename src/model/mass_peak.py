from src.model.maths import calculate_outlier_resistant_mean_and_st_dev


class MassPeak:
    def __init__(self,
                 sample_name,
                 spot_id,
                 mass_peak_name,
                 raw_cps_data,
                 detector_data
                 ):
        self.sample_name = sample_name
        self.spot_id = spot_id
        self.name = mass_peak_name
        self.raw_cps_data = raw_cps_data
        self.detector_yield = detector_data[0]
        self.detector_background = detector_data[1]
        self.dead_time = detector_data[2]

        self.detector_corrected_cps_data = []

    def correct_cps_data_for_detector_parameters(self):
        for data in self.raw_cps_data:
            data, magnitude = data.split("E+")
            value = float(data) * 10 ** int(magnitude)
            background_corrected_data = value - int(self.detector_background)
            yield_corrected_data = background_corrected_data/float(self.detector_yield)
            # TODO deadtime corrected data
            self.detector_corrected_cps_data.append(yield_corrected_data)
        print(self.detector_corrected_cps_data)

    def outlier_resistant_mean_and_st_error(self):
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(self.detector_corrected_cps_data, 1)
        return mean, st_dev
