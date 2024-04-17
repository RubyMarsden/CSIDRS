import math
import numpy as np
import statsmodels.stats.stattools as stattools
import scipy
import numpy.typing as npt
from typing import Any


def calculate_outlier_resistant_mean_and_st_dev(data, number_of_outliers_allowed):
    if len(data) == 0:
        raise Exception("No cycle data input")
    elif len(data) == 1:
        return data, 0, len(data), [], ()
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


def calculate_delta_from_ratio(mean: npt.ArrayLike, standard_ratio: npt.ArrayLike) -> npt.NDArray[Any]:
    delta = ((mean / standard_ratio) - 1) * 1000
    return delta


def vector_length_from_origin(x: int, y: int):
    vector_length = math.sqrt(x ** 2 + y ** 2)
    return vector_length


def drift_correction(x: float, y: npt.NDArray[Any], drift_coefficient: npt.NDArray[Any], zero_time: float) -> \
        npt.NDArray[Any]:
    """
    Drift correction is independent of the y-intercept of the linear drift equation
    """
    correction = x * drift_coefficient
    y_corrected = y - correction
    return y_corrected


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


def calculate_sims_alpha(primary_reference_material_mean_delta: npt.NDArray[Any],
                         externally_measured_primary_reference_value: npt.NDArray[Any]) -> npt.NDArray[Any]:
    alpha_sims = (1 + (primary_reference_material_mean_delta / 1000)) / \
                 (1 + (externally_measured_primary_reference_value / 1000))

    return alpha_sims


def calculate_alpha_correction(data: npt.NDArray[Any], alpha_sims: npt.NDArray[Any]) -> npt.NDArray[Any]:
    # from kita et al, 2009
    alpha_corrected_data = (((1 + (data / 1000)) / alpha_sims) - 1) * 1000

    return alpha_corrected_data


def calculate_binomial_distribution_probability(probability_of_success, number_of_successes, number_of_tests):
    probability_of_k_successful_tests = scipy.stats.binom.pmf(k=number_of_successes, n=number_of_tests,
                                                              p=probability_of_success, loc=0)

    return probability_of_k_successful_tests


def calculate_number_of_outliers_to_remove(number_of_tests, probability_cutoff, probability_of_single_outlier):
    if not (0 < probability_cutoff < 1):
        raise ValueError("A probability cutoff of < 0 or > 1 is not mathematically valid.")
    if not (0 < probability_of_single_outlier < 1):
        raise ValueError("A probability of a single outlier of < 0 or > 1 is not mathematically valid.")
    if type(number_of_tests) is not int or number_of_tests <= 0:
        raise ValueError("The number of tests must be a positive integer")

    outliers_allowed = 0
    probability = 1
    while probability > probability_cutoff and outliers_allowed < number_of_tests:
        outliers_allowed += 1
        probability = calculate_binomial_distribution_probability(probability_of_single_outlier, outliers_allowed,
                                                                  number_of_tests)

    number_of_outliers_to_automatically_remove = outliers_allowed - 1

    return number_of_outliers_to_automatically_remove


def calculate_cap_value_and_uncertainty(delta_value_x: npt.NDArray[Any], delta_value_relative: npt.NDArray[Any],
                                        MDF: float) -> npt.NDArray[Any]:
    cap = delta_value_x - 1000 * ((((delta_value_relative / 1000) + 1) ** MDF) - 1)

    return cap


def calculate_the_total_sum_of_squares_from_the_mean(values: npt.NDArray[Any]) -> npt.NDArray[Any]:
    # for each column take the mean and then for each value find the square difference and sum
    means = np.mean(values, axis=0)
    difference_matrix = (means - values)
    square_difference_matrix = difference_matrix ** 2
    # return a value for each column
    total_sum_of_squares_from_the_mean = np.sum(square_difference_matrix, axis=0)
    return total_sum_of_squares_from_the_mean


def calculate_rsquared_from_tss_and_rss(tss: npt.NDArray[Any], rss: npt.NDArray[Any]) -> npt.NDArray[Any]:
    r_sq = 1 - (rss / tss)
    rsquared = np.where(tss == 0, 0, r_sq)
    return rsquared
