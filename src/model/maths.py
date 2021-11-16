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

    return np.mean(clean_data), np.std(clean_data), len(clean_data), removed_data


def calculate_delta_from_ratio(mean, st_error, standard_ratio):
    delta = ((mean / standard_ratio) - 1) * 1000
    delta_uncertainty = delta * st_error / mean
    return delta, delta_uncertainty


def vector_length_from_origin(x: int, y: int):
    vector_length = math.sqrt(x ** 2 + y ** 2)
    return vector_length
