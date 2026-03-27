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


if __name__ == '__main__':
    unittest.main()
