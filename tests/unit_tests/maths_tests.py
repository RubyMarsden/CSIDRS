import unittest
import numpy as np

from model.maths import calculate_outlier_resistant_mean_and_st_dev, calculate_sims_alpha, \
    calculate_alpha_correction, calculate_cap_value_and_uncertainty, calculate_number_of_outliers_to_remove, \
    calculate_binomial_distribution_probability, calculate_the_total_sum_of_squares_from_the_mean, \
    calculate_rsquared_from_tss_and_rss

from model.mass_peak import MassPeak, correct_cps_data_for_detector_parameters


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
        self.assertRaises(Exception, calculate_outlier_resistant_mean_and_st_dev, [], 2)

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
            detector_data=test_detector_data,
            number_of_measurements=1

        )
        data = correct_cps_data_for_detector_parameters(mass_peak)

        self.assertEqual(data[0], 0)

    def test_alpha_correction_factor_calculation_zero_uncertainty(self):
        alpha_sims = calculate_sims_alpha(1, 1)

        self.assertEqual(alpha_sims, 1)

    def test_alpha_correction_factor_calculation_integers(self):
        data = np.random.normal(100, 1, 1000000)
        external_material = np.random.normal(1000, 10, 1000000)
        alpha_sims = calculate_sims_alpha(data, external_material)
        alpha_corrected_mean = np.mean(alpha_sims)
        st_dev = np.std(alpha_sims)

        self.assertAlmostEqual(alpha_corrected_mean, 0.55, 3)
        self.assertAlmostEqual(st_dev, 0.00279508497, 3)

    def test_alpha_correction_factor_calculation_S34_example(self):
        data = np.random.normal(4.49, 0.16, 1000000)
        external_material = np.random.normal(2.17, 0.28, 1000000)
        alpha_sims = calculate_sims_alpha(data, external_material)

        alpha_corrected_mean = np.mean(alpha_sims)
        st_dev = np.std(alpha_sims)

        self.assertAlmostEqual(alpha_corrected_mean, 1.00231497650099000000, 4)
        self.assertAlmostEqual(st_dev, 0.0003223537519, 4)

    def test_alpha_correction_no_uncertainty(self):
        alpha_corrected_data = calculate_alpha_correction(1, 1)
        alpha_corrected_mean = np.mean(alpha_corrected_data)
        st_dev = np.std(alpha_corrected_data)
        # is almost equal due to some floating point errors
        self.assertAlmostEqual(alpha_corrected_mean, 1)
        self.assertEqual(st_dev, 0)

    def test_alpha_correction_integers(self):
        data = np.full((1000,), 10)
        alpha_sims = np.full((1000,), 2)
        alpha_corrected_data = calculate_alpha_correction(data, alpha_sims)
        alpha_corrected_mean = np.mean(alpha_corrected_data)
        st_dev = np.std(alpha_corrected_data)
        # is almost equal due to some floating point errors
        self.assertAlmostEqual(alpha_corrected_mean, -495)
        # self.assertAlmostEqual(st_dev, 252.50049504902)

    def test_alpha_correction_S34_example(self):
        data = np.random.normal(4.49, 0.16, 10000000)
        alpha_sims = np.random.normal(1.00231497650099000000, 0.0003223537519, 10000000)
        alpha_corrected_data = calculate_alpha_correction(data, alpha_sims)
        alpha_corrected_mean = np.mean(alpha_corrected_data)
        st_dev = np.std(alpha_corrected_data)
        # is almost equal due to some floating point errors
        self.assertAlmostEqual(alpha_corrected_mean, 2.17, 3)
        self.assertAlmostEqual(st_dev, 0.35967174905, 3)

    def test_calculate_cap_value_and_uncertainty_no_uncertainty(self):
        delta_data = np.full((1000, 1), 10)
        delta_relative = np.full((1000, 1), 1)
        cap_value = calculate_cap_value_and_uncertainty(delta_value_x=delta_data,
                                                        delta_value_relative=delta_relative,
                                                        MDF=1)

        cap_mean = np.mean(cap_value)
        st_dev = np.std(cap_value)

        self.assertAlmostEqual(cap_mean, 9)
        # almost because of some floating point errors I think (can give something to the 10^-15)
        self.assertAlmostEqual(st_dev, 0)

    def test_calculate_cap_value_and_uncertainty_integers(self):
        delta_data = np.random.normal(100, 1, 1000000)
        delta_relative = np.random.normal(10, 1, 1000000)
        cap_value = calculate_cap_value_and_uncertainty(delta_value_x=delta_data,
                                                        delta_value_relative=delta_relative,
                                                        MDF=1)
        cap_mean = np.mean(cap_value)
        st_dev = np.std(cap_value)
        self.assertAlmostEqual(cap_mean, 90, 1)
        # self.assertAlmostEqual(st_dev, 2, 3)

    def test_calculate_cap_value_and_uncertainty_Cap33_example(self):
        delta_data = np.random.normal(1.2, 0.09, 1000000)
        delta_relative = np.random.normal(2.17, 0.16, 1000000)
        cap_value = calculate_cap_value_and_uncertainty(delta_value_x=delta_data,
                                                        delta_value_relative=delta_relative,
                                                        MDF=0.515)

        cap_mean = np.mean(cap_value)
        st_dev = np.std(cap_value)

        self.assertAlmostEqual(cap_mean, 0.083037451910, 3)
        # self.assertAlmostEqual(st_dev, 0.16990815079992, 3)

    def test_calculate_binomial_distribution_probability_simple(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.5,
                                                                  number_of_successes=1,
                                                                  number_of_tests=1)

        self.assertEqual(probability, 0.5)

    def test_calculate_binomial_distribution_probability_two_tests_one_success(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.5,
                                                                  number_of_successes=1,
                                                                  number_of_tests=2)

        self.assertAlmostEqual(probability, 0.5)

    def test_calculate_binomial_distribution_probability_two_tests_two_successes(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.5,
                                                                  number_of_successes=2,
                                                                  number_of_tests=2)

        self.assertAlmostEqual(probability, 0.25)

    def test_calculate_binomial_distribution_probability_twenty_tests_one_success_outlier(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.007,
                                                                  number_of_successes=1,
                                                                  number_of_tests=20)

        self.assertAlmostEqual(probability, 0.12250780457)

    def test_calculate_binomial_distribution_probability_twenty_tests_two_successes_outlier(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.007,
                                                                  number_of_successes=2,
                                                                  number_of_tests=20)

        self.assertAlmostEqual(probability, 0.00820419839)

    def test_calculate_binomial_distribution_probability_one_hundred_tests_one_success_outlier(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.007,
                                                                  number_of_successes=1,
                                                                  number_of_tests=100)

        self.assertAlmostEqual(probability, 0.3491995224)

    def test_calculate_binomial_distribution_probability_one_hundred_tests_two_successes_outlier(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.007,
                                                                  number_of_successes=2,
                                                                  number_of_tests=100)

        self.assertAlmostEqual(probability, 0.12185058863)

    def test_calculate_binomial_distribution_probability_one_hundred_tests_three_successes_outlier(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.007,
                                                                  number_of_successes=3,
                                                                  number_of_tests=100)

        self.assertAlmostEqual(probability, 0.02805958502)

    def test_calculate_binomial_distribution_probability_one_hundred_tests_four_successes_outlier(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.007,
                                                                  number_of_successes=4,
                                                                  number_of_tests=100)

        self.assertAlmostEqual(probability, 0.00479669139)

    def test_calculate_binomial_distribution_probability_one_hundred_tests_five_successes_outlier(self):
        probability = calculate_binomial_distribution_probability(probability_of_success=0.007,
                                                                  number_of_successes=5,
                                                                  number_of_tests=100)

        self.assertAlmostEqual(probability, 0.00064921986)

    def test_calculate_number_of_outliers_removed_errors(self):
        func = calculate_number_of_outliers_to_remove
        # Number of tests errors
        self.assertRaises(ValueError, lambda: func(number_of_tests=1.3,
                                                   probability_cutoff=0.01,
                                                   probability_of_single_outlier=0.007))
        self.assertRaises(ValueError, lambda: func(number_of_tests=0,
                                                   probability_cutoff=0.01,
                                                   probability_of_single_outlier=0.007))
        self.assertRaises(ValueError, lambda: func(number_of_tests=-1,
                                                   probability_cutoff=0.01,
                                                   probability_of_single_outlier=0.007))
        # Probability cutoff errors
        self.assertRaises(ValueError, lambda: func(number_of_tests=1,
                                                   probability_cutoff=-0.01,
                                                   probability_of_single_outlier=0.007))
        self.assertRaises(ValueError, lambda: func(number_of_tests=1,
                                                   probability_cutoff=1.01,
                                                   probability_of_single_outlier=0.007))
        # Probability of single outlier errors
        self.assertRaises(ValueError, lambda: func(number_of_tests=1,
                                                   probability_cutoff=0.01,
                                                   probability_of_single_outlier=-0.007))
        self.assertRaises(ValueError, lambda: func(number_of_tests=1,
                                                   probability_cutoff=0.01,
                                                   probability_of_single_outlier=1.007))

    def test_calculate_number_of_outliers_removed_one_test(self):
        number_of_outliers_to_remove = calculate_number_of_outliers_to_remove(number_of_tests=1,
                                                                              probability_cutoff=0.01,
                                                                              probability_of_single_outlier=0.007)

        self.assertEqual(number_of_outliers_to_remove, 0)

    def test_calculate_number_of_outliers_removed_twenty_tests(self):
        number_of_outliers_to_remove = calculate_number_of_outliers_to_remove(number_of_tests=20,
                                                                              probability_cutoff=0.01,
                                                                              probability_of_single_outlier=0.007)

        self.assertEqual(number_of_outliers_to_remove, 1)

    def test_calculate_number_of_outliers_removed_one_hundred_tests(self):
        number_of_outliers_to_remove = calculate_number_of_outliers_to_remove(number_of_tests=100,
                                                                              probability_cutoff=0.01,
                                                                              probability_of_single_outlier=0.007)

        self.assertEqual(number_of_outliers_to_remove, 3)

    def test_rsqaured_no_correlation(self):
        xs = np.array([1, 2, 3, 4, 5])
        ys = np.full((5,), 1)

        xs_constant = np.vstack([xs, np.ones(len(xs))]).T

        results = np.linalg.lstsq(xs_constant, ys)
        m, c = results[0]
        residual_sum_of_squares = results[1]
        tss = calculate_the_total_sum_of_squares_from_the_mean(ys)
        rsquared_array = calculate_rsquared_from_tss_and_rss(tss, residual_sum_of_squares)
        rsquared = rsquared_array.item()

        self.assertEqual(rsquared, 0)
        self.assertAlmostEqual(m, 0)
        self.assertEqual(c, 1)

    def test_rquared_2(self):
        xs = np.array([1, 2, 3, 4, 5])
        ys = np.array([0.95, 1.1, 0.9, 1.1, 0.95])

        xs_constant = np.vstack([xs, np.ones(len(xs))]).T

        results = np.linalg.lstsq(xs_constant, ys)
        m, c = results[0]
        residual_sum_of_squares = results[1]
        tss = calculate_the_total_sum_of_squares_from_the_mean(ys)
        rsquared_array = calculate_rsquared_from_tss_and_rss(tss, residual_sum_of_squares)
        rsquared = rsquared_array.item()

        self.assertAlmostEqual(rsquared, 0)
        self.assertAlmostEqual(m, 0)
        self.assertAlmostEqual(c, 1)

    def test_rquared_3(self):
        xs = np.array([1, 2, 3, 4, 5])
        ys = np.array([1, 2, 3, 4, 5])

        xs_constant = np.vstack([xs, np.ones(len(xs))]).T

        results = np.linalg.lstsq(xs_constant, ys)
        m, c = results[0]
        residual_sum_of_squares = results[1]
        tss = calculate_the_total_sum_of_squares_from_the_mean(ys)
        rsquared_array = calculate_rsquared_from_tss_and_rss(tss, residual_sum_of_squares)
        rsquared = rsquared_array.item()

        self.assertAlmostEqual(rsquared, 1)
        self.assertAlmostEqual(m, 1)
        self.assertAlmostEqual(c, 0)

    def test_rquared_4(self):
        xs = np.array([1, 2, 3, 4, 5])
        ys = np.array([5, 4, 3, 2, 1])

        xs_constant = np.vstack([xs, np.ones(len(xs))]).T

        results = np.linalg.lstsq(xs_constant, ys)
        m, c = results[0]
        residual_sum_of_squares = results[1]
        tss = calculate_the_total_sum_of_squares_from_the_mean(ys)
        rsquared_array = calculate_rsquared_from_tss_and_rss(tss, residual_sum_of_squares)
        rsquared = rsquared_array.item()

        self.assertAlmostEqual(rsquared, 1)
        self.assertAlmostEqual(m, -1)
        self.assertAlmostEqual(c, 6)

    def test_rquared_5(self):
        xs = np.array([1, 2, 3, 4, 5])
        ys = np.array([1, 1.5, 3.5, 4, 4.5])

        xs_constant = np.vstack([xs, np.ones(len(xs))]).T

        results = np.linalg.lstsq(xs_constant, ys)
        m, c = results[0]
        residual_sum_of_squares = results[1]
        tss = calculate_the_total_sum_of_squares_from_the_mean(ys)
        rsquared_array = calculate_rsquared_from_tss_and_rss(tss, residual_sum_of_squares)
        rsquared = rsquared_array.item()

        self.assertAlmostEqual(rsquared, 0.93041237113402)
        self.assertAlmostEqual(m, 0.95)
        self.assertAlmostEqual(c, 0.05)

    def test_rquared_6(self):
        xs = np.array([1, 2, 3, 4, 5])
        ys = np.array([4.5, 4, 3.5, 1.5, 1])

        xs_constant = np.vstack([xs, np.ones(len(xs))]).T

        results = np.linalg.lstsq(xs_constant, ys)
        m, c = results[0]
        residual_sum_of_squares = results[1]
        print(residual_sum_of_squares)
        tss = calculate_the_total_sum_of_squares_from_the_mean(ys)
        rsquared_array = calculate_rsquared_from_tss_and_rss(tss, residual_sum_of_squares)
        rsquared = rsquared_array.item()

        self.assertAlmostEqual(rsquared, 0.93041237113402)
        self.assertAlmostEqual(m, -0.95)
        self.assertAlmostEqual(c, 5.75)

    def test_rquared_7(self):
        xs = np.array([1, 2, 3, 4, 5])
        ys = np.array([3.5, 1, 4, 4.5, 1.5])

        xs_constant = np.vstack([xs, np.ones(len(xs))]).T

        results = np.linalg.lstsq(xs_constant, ys)
        m, c = results[0]
        residual_sum_of_squares = results[1]
        tss = calculate_the_total_sum_of_squares_from_the_mean(ys)
        rsquared_array = calculate_rsquared_from_tss_and_rss(tss, residual_sum_of_squares)
        rsquared = rsquared_array.item()

        self.assertAlmostEqual(rsquared, 0.00257731958762886)
        self.assertAlmostEqual(m, -0.05)
        self.assertAlmostEqual(c, 3.05)

if __name__ == '__main__':
    unittest.main()
