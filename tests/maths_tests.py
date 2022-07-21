import unittest
import numpy as np

from src.model.maths import calculate_outlier_resistant_mean_and_st_dev, calculate_sims_alpha, \
    calculate_alpha_correction, calculate_cap_value_and_uncertainty
from src.model.mass_peak import MassPeak


class MathsTests(unittest.TestCase):

    def test_outlier_resistant_mean_no_outliers_allowed(self):
        test_data = [1, 1, 2, 1, 4, 1, 2, 3, 9, 2]
        mean, st_dev, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data, 0)
        self.assertEqual(np.mean(test_data), mean)
        self.assertEqual(np.std(test_data), st_dev)

    def test_outlier_resistant_mean_zeros(self):
        test_data = [0] * 10
        mean, st_dev, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data, 2)
        self.assertEqual((0, 0), (mean, st_dev))

    def test_outlier_resistant_mean_empty_set(self):
        self.assertRaises(IndexError, calculate_outlier_resistant_mean_and_st_dev, [], 2)

    def test_outlier_resistant_mean_one_higher_outlier(self):
        test_data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 40]
        mean, st_dev, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data,
                                                                                                             2)
        self.assertEqual(1, mean)
        self.assertEqual(0, st_dev)
        self.assertEqual(1, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_outlier_resistant_mean_one_lower_outlier(self):
        test_data = [1, 40, 40, 40, 40, 40, 40, 40, 40, 40]
        mean, st_dev, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data,
                                                                                                             2)
        self.assertEqual(40, mean)
        self.assertEqual(0, st_dev)
        self.assertEqual(40, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_outlier_resistant_mean_two_outliers(self):
        test_data = [1, 40, 40, 40, 40, 40, 40, 40, 40, 400]
        mean, st_dev, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2, length, removed_data, outlier_bounds = calculate_outlier_resistant_mean_and_st_dev(test_data,
                                                                                                             2)
        self.assertEqual(np.mean(test_data), mean)
        self.assertEqual(np.std(test_data), st_dev)
        self.assertEqual(40, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_background_correction(self):
        test_data = ["10E+0"]
        test_detector_data = [1, 10, 0]
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

    def test_alpha_correction_factor_calculation_zero_uncertainty(self):
        alpha_sims, uncertainty = calculate_sims_alpha(1, 0, (1, 0))

        self.assertEqual(alpha_sims, 1)
        self.assertEqual(uncertainty, 0)

    def test_alpha_correction_factor_calculation_integers(self):
        alpha_sims, uncertainty = calculate_sims_alpha(100, 1, (1000, 10))

        self.assertEqual(alpha_sims, 0.55)
        self.assertAlmostEqual(uncertainty, 0.00279508497)

    def test_alpha_correction_factor_calculation_S34_example(self):
        alpha_sims, uncertainty = calculate_sims_alpha(4.49, 0.16, (2.17, 0.28))

        self.assertAlmostEqual(alpha_sims, 1.00231497650099000000)
        self.assertAlmostEqual(uncertainty, 0.0003223537519)

    def test_alpha_correction_no_uncertainty(self):
        alpha_corrected_data, uncertainty = calculate_alpha_correction((1, 0), 1, 0)
        # is almost equal due to some floating point errors
        self.assertAlmostEqual(alpha_corrected_data, 1)
        self.assertEqual(uncertainty, 0)

    def test_alpha_correction_integers(self):
        alpha_corrected_data, uncertainty = calculate_alpha_correction((10, 1), 2, 1)
        # is almost equal due to some floating point errors
        self.assertAlmostEqual(alpha_corrected_data, -495)
        self.assertAlmostEqual(uncertainty, 252.50049504902)

    def test_alpha_correction_S34_example(self):
        alpha_corrected_data, uncertainty = calculate_alpha_correction((4.49, 0.16), alpha_sims=1.00231497650099000000,
                                                                       alpha_sims_uncertainty=0.0003223537519)
        # is almost equal due to some floating point errors
        self.assertAlmostEqual(alpha_corrected_data, 2.17)
        self.assertAlmostEqual(uncertainty, 0.35967174905)

    def test_calculate_cap_value_and_uncertainty_no_uncertainty(self):
        cap_value, uncertainty = calculate_cap_value_and_uncertainty(delta_value_x=10,
                                                                     uncertainty_x=0,
                                                                     delta_value_relative=1,
                                                                     uncertainty_relative=0,
                                                                     MDF=1,
                                                                     reference_material_covariance=0)

        self.assertAlmostEqual(cap_value, 9)
        self.assertEqual(uncertainty, 0)

    def test_calculate_cap_value_and_uncertainty_integers(self):
        cap_value, uncertainty = calculate_cap_value_and_uncertainty(delta_value_x=100,
                                                                     uncertainty_x=1,
                                                                     delta_value_relative=10,
                                                                     uncertainty_relative=1,
                                                                     MDF=1,
                                                                     reference_material_covariance=1)

        self.assertAlmostEqual(cap_value, 90)
        self.assertEqual(uncertainty, 2)


    def test_calculate_cap_value_and_uncertainty_Cap33_example(self):
        cap_value, uncertainty = calculate_cap_value_and_uncertainty(delta_value_x=1.2,
                                                                     uncertainty_x=0.09,
                                                                     delta_value_relative=2.17,
                                                                     uncertainty_relative=0.16,
                                                                     MDF=0.515,
                                                                     reference_material_covariance=0.0136)

        self.assertAlmostEqual(cap_value, 0.083037451910)
        self.assertAlmostEqual(uncertainty, 0.16990815079992)


if __name__ == '__main__':
    unittest.main()
