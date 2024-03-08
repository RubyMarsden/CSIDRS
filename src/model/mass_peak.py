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


def correct_cps_data_for_detector_parameters(mass_peak):
    detector_corrected_cps_data = []
    for data in mass_peak.raw_cps_data:
        data, magnitude = data.split("E+")
        value = float(data) * 10 ** int(magnitude)
        dead_time_corrected_data = correct_cps_for_deadtime_if_required(mass_peak.dead_time, value)
        background_corrected_data = dead_time_corrected_data - int(mass_peak.detector_background)
        yield_corrected_data = background_corrected_data / float(mass_peak.detector_yield)
        detector_corrected_cps_data.append(yield_corrected_data)

    return detector_corrected_cps_data


def outlier_resistant_mean_and_st_error(mass_peak):
    mean_cps, st_dev, n, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(
        mass_peak.detector_corrected_cps_data, 1)

    st_error_cps = st_dev / math.sqrt(n)

    return mean_cps, st_error_cps


def correct_cps_for_deadtime_if_required(dead_time, value):
    dead_time_value = float(dead_time)
    if dead_time_value == 0.0:
        return value

    corrected_data = value / (1 - value * dead_time_value * 10 ** -9)

    return corrected_data
