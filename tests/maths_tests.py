import unittest
import numpy as np

from src.model.maths import calculate_outlier_resistant_mean_and_st_dev
from src.model.mass_peak import MassPeak


class MathsTests(unittest.TestCase):

    def test_outlier_resistant_mean_no_outliers_allowed(self):
        test_data = [1, 1, 2, 1, 4, 1, 2, 3, 9, 2]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 0)
        self.assertEqual(np.mean(test_data), mean)
        self.assertEqual(np.std(test_data), st_dev)

    def test_outlier_resistant_mean_zeros(self):
        test_data = [0] * 10
        self.assertEqual((0, 0), calculate_outlier_resistant_mean_and_st_dev(test_data, 2))

    def test_outlier_resistant_mean_empty_set(self):
        self.assertRaises(IndexError, calculate_outlier_resistant_mean_and_st_dev, [], 2)

    def test_outlier_resistant_mean_one_higher_outlier(self):
        test_data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 40]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2 = calculate_outlier_resistant_mean_and_st_dev(test_data, 2)
        self.assertEqual(1, mean)
        self.assertEqual(0, st_dev)
        self.assertEqual(1, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_outlier_resistant_mean_one_lower_outlier(self):
        test_data = [1, 40, 40, 40, 40, 40, 40, 40, 40, 40]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2 = calculate_outlier_resistant_mean_and_st_dev(test_data, 2)
        self.assertEqual(40, mean)
        self.assertEqual(0, st_dev)
        self.assertEqual(40, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_outlier_resistant_mean_two_outliers(self):
        test_data = [1, 40, 40, 40, 40, 40, 40, 40, 40, 400]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2 = calculate_outlier_resistant_mean_and_st_dev(test_data, 2)
        self.assertEqual(np.mean(test_data), mean)
        self.assertEqual(np.std(test_data), st_dev)
        self.assertEqual(40, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_background_correction(self):
        test_data = ["10E+0"]
        test_detector_data = [1,10,0]
        mass_peak = MassPeak(
            sample_name="Test",
            spot_id=1,
            mass_peak_name="test",
            raw_cps_data=test_data,
            detector_data=test_detector_data

        )
        mass_peak.correct_cps_data_for_detector_parameters()
        data = mass_peak.detector_corrected_cps_data

        self.assertEqual(data[0], 0)


if __name__ == '__main__':
    unittest.main()
