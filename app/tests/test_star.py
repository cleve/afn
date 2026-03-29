import unittest
import random

from core.element import Element
from core.star import Star
from utils.constants import ElementType


class TestStarMethods(unittest.TestCase):
    
    def setUp(self) -> None:
        self.element = Element(1, 0, 0, ElementType.HIDROGEN)
        self.elements = [(1, 0, 0)]
        self.star = Star([(1, 0, 0)], [[0]])
        return super().setUp()

    def test_get_next_element_type(self):
        assert self.star._get_next_element_type(
            ElementType.HIDROGEN) == ElementType.HELIUM
        assert self.star._get_next_element_type(
            ElementType.HELIUM) == ElementType.CARBON
        assert self.star._get_next_element_type(
            ElementType.CARBON) == ElementType.CARBON
    
    def test_ignition(self):
        assert len(self.star.elements) == 1

    def test_life_terminates_with_odd_number_of_nodes(self):
        random.seed(0)
        base_elements = [(index, float(index), 0.0) for index in range(1, 8)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(len(base_elements))]
            for ii in range(len(base_elements))
        ]
        star = Star(base_elements, distance_matrix)

        star.life()

        self.assertLessEqual(len(star.elements), 2)

    def test_fusion_probability_is_bounded(self):
        base_elements = [(index, float(index), 0.0) for index in range(1, 5)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(len(base_elements))]
            for ii in range(len(base_elements))
        ]
        star = Star(base_elements, distance_matrix)

        probability = star._fusion_probability(0.5)

        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

    def test_fallback_pair_returns_scored_triplet(self):
        base_elements = [(index, float(index), 0.0) for index in range(1, 5)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(len(base_elements))]
            for ii in range(len(base_elements))
        ]
        star = Star(base_elements, distance_matrix)

        pair = star._get_fallback_pair()

        self.assertIsNotNone(pair)
        self.assertEqual(len(pair), 3)
        self.assertIn('score', pair[2])
        self.assertIn('distance', pair[2])

    def test_core_state_updates_after_fusion(self):
        random.seed(0)
        base_elements = [(index, float(index), 0.0) for index in range(1, 5)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(len(base_elements))]
            for ii in range(len(base_elements))
        ]
        star = Star(base_elements, distance_matrix)

        initial_temperature = star.core_temperature
        initial_count = len(star.elements)

        forced_pair = star._get_fallback_pair()
        star._fusion(forced_pair[0], forced_pair[1])
        star._update_core_state(True, forced_pair[2]['score'])

        self.assertLess(len(star.elements), initial_count)
        self.assertGreaterEqual(star.core_temperature, initial_temperature)

    def test_collapse_probability_is_bounded(self):
        base_elements = [(index, float(index), 0.0) for index in range(1, 6)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(len(base_elements))]
            for ii in range(len(base_elements))
        ]
        star = Star(base_elements, distance_matrix)

        probability = star._collapse_probability(idle_cycles=3, max_idle_cycles=10)

        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

    def test_pressure_stays_within_bounds_after_state_updates(self):
        random.seed(7)
        base_elements = [(index, float(index), 0.0) for index in range(1, 6)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(5)]
            for ii in range(5)
        ]
        star = Star(base_elements, distance_matrix)

        for _ in range(30):
            star._update_core_state(True, 0.5)
            self.assertGreaterEqual(star.pressure, 0.7)
            self.assertLessEqual(star.pressure, 2.5)

        for _ in range(30):
            star._update_core_state(False, 0.0)
            self.assertGreaterEqual(star.pressure, 0.7)
            self.assertLessEqual(star.pressure, 2.5)

    def test_pressure_increases_on_average_with_temperature(self):
        """After repeated successful fusions (rising T), mean pressure should grow."""
        random.seed(0)
        base_elements = [(index, float(index), 0.0) for index in range(1, 6)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(5)]
            for ii in range(5)
        ]
        star = Star(base_elements, distance_matrix)
        initial_pressure = star.pressure

        for _ in range(40):
            star._update_core_state(True, 1.0)

        self.assertGreater(star.pressure, initial_pressure)

    def test_fusion_weights_override_partial(self):
        base_elements = [(index, float(index), 0.0) for index in range(1, 5)]
        distance_matrix = [
            [abs(ii - jj) for jj in range(len(base_elements))]
            for ii in range(len(base_elements))
        ]
        custom_weights = {'score': 0.80, 'route_gain': 0.20}
        star = Star(base_elements, distance_matrix, fusion_weights=custom_weights)

        self.assertEqual(star._fusion_weights['score'], 0.80)
        self.assertEqual(star._fusion_weights['route_gain'], 0.20)
        # Unspecified keys should use defaults.
        self.assertEqual(star._fusion_weights['distance'], 0.20)
        self.assertEqual(star._fusion_weights['barrier'], 0.20)


if __name__ == '__main__':
    unittest.main()
