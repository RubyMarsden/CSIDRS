import math

from model.maths import calculate_outlier_resistant_mean_and_st_dev


class MassPeak:
    def __init__(self,
                 sample_name,
                 spot_id,
                 mass_peak_name,
                 raw_cps_data,
                 detector_data,
                 number_of_measurements
                 ):
        self.sample_name = sample_name
        self.spot_id = spot_id
        self.name = mass_peak_name
        self.raw_cps_data = raw_cps_data
        self.detector_yield = detector_data[0]
        self.detector_background = detector_data[1]
        self.dead_time = detector_data[2]
        self.number_of_measurements = number_of_measurements

        self.detector_corrected_cps_data = []
        self.mean_cps = None
        self.st_error_cps = None

    def correct_cps_data_for_detector_parameters(self):
        for data in self.raw_cps_data:
            data, magnitude = data.split("E+")
            value = float(data) * 10 ** int(magnitude)
            dead_time_corrected_data = self.correct_cps_for_deadtime_if_required(value)
            background_corrected_data = dead_time_corrected_data - int(self.detector_background)
            yield_corrected_data = background_corrected_data / float(self.detector_yield)
            self.detector_corrected_cps_data.append(yield_corrected_data)

    def outlier_resistant_mean_and_st_error(self):
        mean, st_dev, n, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(
            self.detector_corrected_cps_data, 1)
        self.mean_cps = mean
        self.st_error_cps = st_dev / math.sqrt(n)

    def correct_cps_for_deadtime_if_required(self, value):
        dead_time_value = float(self.dead_time)
        if dead_time_value == 0.0:
            return value

        corrected_data = value / (1 - value * dead_time_value * 10 ** -9)

        return corrected_data

