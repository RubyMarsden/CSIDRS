import unittest
import numpy as np

from src.model.maths import calculate_outlier_resistant_mean_and_st_dev


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


if __name__ == '__main__':
    unittest.main()
