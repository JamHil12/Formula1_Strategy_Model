import unittest
import modelling_utilities as mu
import numpy as np

class TyreDegCurveQuadratic_ReturnsCorrectArray(unittest.TestCase):
    # tyre_deg_curve_quadratic should return a numpy array of floats
    def test_soft_tyre(self):
        tyre_age = np.arange(3, 18)
        tyre_description = np.array(['Soft'] * 15)
        soft_tyre_deg_quadratic = 0.02
        soft_tyre_deg_linear = 0.002
        medium_tyre_pace_deficit = 0.7
        medium_tyre_deg_quadratic = 0.015
        medium_tyre_deg_linear = 0.002
        hard_tyre_pace_deficit = 1.2
        hard_tyre_deg_quadratic = 0.01
        hard_tyre_deg_linear = 0.002
        # The expected entries in the resulting array are at^2 + bt, where t is tyre age in laps, and a, b are the soft tyre quadratic, linear parameters
        expected_result = np.array([0.186, 0.328, 0.51, 0.732, 0.994, 1.296, 1.638, 2.02, 2.442, 2.904, 3.406, 3.948, 4.53, 5.152, 5.814])
        np.testing.assert_allclose(mu.tyre_deg_curve_quadratic(tyre_age, tyre_description, soft_tyre_deg_quadratic, soft_tyre_deg_linear,
                                                               medium_tyre_pace_deficit, medium_tyre_deg_quadratic, medium_tyre_deg_linear,
                                                               hard_tyre_pace_deficit, hard_tyre_deg_quadratic, hard_tyre_deg_linear),
                                   expected_result)

    def test_medium_tyre(self):
        tyre_age = np.arange(3, 18)
        tyre_description = np.array(['Medium'] * 15)
        soft_tyre_deg_quadratic = 0.02
        soft_tyre_deg_linear = 0.002
        medium_tyre_pace_deficit = 0.7
        medium_tyre_deg_quadratic = 0.015
        medium_tyre_deg_linear = 0.002
        hard_tyre_pace_deficit = 1.2
        hard_tyre_deg_quadratic = 0.01
        hard_tyre_deg_linear = 0.002
        # The expected entries in the resulting array are at^2 + bt + c, where t is tyre age in laps, and a, b, c are the medium tyre quadratic, linear, deficit parameters
        expected_result = np.array([0.841, 0.948, 1.085, 1.252, 1.449, 1.676, 1.933, 2.22, 2.537, 2.884, 3.261, 3.668, 4.105, 4.572, 5.069])
        np.testing.assert_allclose(mu.tyre_deg_curve_quadratic(tyre_age, tyre_description, soft_tyre_deg_quadratic, soft_tyre_deg_linear,
                                                               medium_tyre_pace_deficit, medium_tyre_deg_quadratic, medium_tyre_deg_linear,
                                                               hard_tyre_pace_deficit, hard_tyre_deg_quadratic, hard_tyre_deg_linear),
                                   expected_result)

    def test_hard_tyre(self):
        tyre_age = np.arange(3, 18)
        tyre_description = np.array(['Hard'] * 15)
        soft_tyre_deg_quadratic = 0.02
        soft_tyre_deg_linear = 0.002
        medium_tyre_pace_deficit = 0.7
        medium_tyre_deg_quadratic = 0.015
        medium_tyre_deg_linear = 0.002
        hard_tyre_pace_deficit = 1.2
        hard_tyre_deg_quadratic = 0.01
        hard_tyre_deg_linear = 0.002
        # The expected entries in the resulting array are at^2 + bt + c, where t is tyre age in laps, and a, b, c are the hard tyre quadratic, linear, deficit parameters
        expected_result = np.array([1.296, 1.368, 1.46, 1.572, 1.704, 1.856, 2.028, 2.22, 2.432, 2.664, 2.916, 3.188, 3.48, 3.792, 4.124])
        np.testing.assert_allclose(mu.tyre_deg_curve_quadratic(tyre_age, tyre_description, soft_tyre_deg_quadratic, soft_tyre_deg_linear,
                                                               medium_tyre_pace_deficit, medium_tyre_deg_quadratic, medium_tyre_deg_linear,
                                                               hard_tyre_pace_deficit, hard_tyre_deg_quadratic, hard_tyre_deg_linear),
                                   expected_result)

if __name__ == '__main__':
    unittest.main()