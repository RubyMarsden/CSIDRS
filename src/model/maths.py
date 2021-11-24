import math
import numpy as np
import statsmodels.stats.stattools as stattools


def calculate_outlier_resistant_mean_and_st_dev(data, number_of_outliers_allowed):
    medcouple = stattools.medcouple(data)
    Q1 = np.percentile(data, 25, interpolation='midpoint')
    Q3 = np.percentile(data, 75, interpolation='midpoint')
    IQR = Q3 - Q1

    if medcouple > 0:
        lower_constant = -4
        upper_constant = 3
    else:
        lower_constant = -3
        upper_constant = 4

    skew_corrected_outlier_minimum = Q1 - 1.5 * math.exp(lower_constant * medcouple) * IQR
    skew_corrected_outlier_maximum = Q3 + 1.5 * math.exp(upper_constant * medcouple) * IQR

    data_without_outliers = []
    for x in data:
        if skew_corrected_outlier_minimum <= x <= skew_corrected_outlier_maximum:
            data_without_outliers.append(x)

    if len(data_without_outliers) < len(data) - number_of_outliers_allowed:
        clean_data = data
    else:
        clean_data = data_without_outliers

    removed_data = [item for item in data if item not in clean_data]
    outlier_bounds = (skew_corrected_outlier_minimum, skew_corrected_outlier_maximum)

    return np.mean(clean_data), np.std(clean_data), len(clean_data), removed_data, outlier_bounds


def calculate_delta_from_ratio(mean, two_st_error, standard_ratio):
    delta = ((mean / standard_ratio) - 1) * 1000
    delta_uncertainty = delta * two_st_error / mean
    return delta, delta_uncertainty


def vector_length_from_origin(x: int, y: int):
    vector_length = math.sqrt(x ** 2 + y ** 2)
    return vector_length


def drift_correction(xs, ys, dxs, dys, drift_coefficient, zero_time):
    corrected_ys = []
    for (x, y) in zip(xs, ys):
        correction = (zero_time - x) * drift_coefficient
        y_corrected = y + correction
        corrected_ys.append(y_corrected)

    return xs, corrected_ys, dxs, dys

def calculate_added_uncertainty_to_make_single_population(ys, dys):
    mean, uncertainty = calculate_error_weighted_mean_and_st_dev(ys, dys)


    new_sample_uncertainty = (uncertainty ** 2) * (reduced_chi_squared ** 2)




def calculate_error_weighted_mean_and_st_dev(values, errors):
    non_zero_errors = [error for error in errors if error != 0]

    # If all errors are zero then simply take the mean.
    if len(non_zero_errors) == 0:
        weighted_mean = np.mean(values)
        weighted_st_dev = 0
        return weighted_mean, weighted_st_dev

    # If some errors are zero, replace them with a small value
    if len(non_zero_errors) < len(errors):
        small_value = min(non_zero_errors) / 10
        errors = [(error if error != 0 else small_value) for error in errors]

    inverse_errors = [1 / (error ** 2) for error in errors]
    sigma = sum(inverse_errors)
    weighted_mean = (sum([value * inverseError for value, inverseError in zip(values, inverse_errors)])) / sigma
    weighted_st_dev = math.sqrt(1 / sigma)
    return weighted_mean, weighted_st_dev


def calculate_reduced_chi_squared():
    # TODO - talk this out with Chris?