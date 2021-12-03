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


def drift_correction(x, y, dy, drift_coefficient, zero_time):
    correction = (zero_time - x) * drift_coefficient
    y_corrected = y + correction

    return y_corrected, dy


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
    return


def calculate_sims_alpha(primary_reference_material_mean_delta, externally_measured_primary_reference_value):
    alpha_sims = (1 + (primary_reference_material_mean_delta / 1000)) / \
                 (1 + (externally_measured_primary_reference_value / 1000))

    return alpha_sims


def calculate_alpha_correction(data, alpha_sims, uncertainty_from_primary_st_dev):
    data_point, uncertainty = data
    alpha_corrected_data = (((1 + (data_point / 1000)) / alpha_sims) - 1) * 1000
    uncertainty_propagated_relatively = alpha_corrected_data * uncertainty / data_point
    alpha_corrected_uncertainty = math.sqrt(
        (uncertainty_propagated_relatively ** 2) + (uncertainty_from_primary_st_dev ** 2))
    return alpha_corrected_data, alpha_corrected_uncertainty
