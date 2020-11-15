import unittest
from utils.helper import Helper
from utils.constants import ElementType
from core.element import Element


class TestUtilsMethods(unittest.TestCase):

    def test_get_candidates(self):
        helium = Element(4, 1, 1, ElementType.HELIUM)
        hidro1 = Element(1, 1, 1, ElementType.HIDROGEN)
        hidro2 = Element(1, 1, 1, ElementType.HIDROGEN)
        hidro3 = Element(1, 1, 1, ElementType.HIDROGEN)
        elements = [
            hidro1,
            hidro2,
            hidro3,
            helium,
        ]
        candidates = Helper.get_candidates(elements, ElementType.HELIUM)
        self.assertListEqual(candidates, [helium])
        self.assertNotEqual(
            candidates, [hidro1])

    def test_random_element(self):
        options = [
            ElementType.HIDROGEN,
            ElementType.HELIUM,
            ElementType.CARBON
        ]
        elem_type = Helper.get_randon_element()
        self.assertIn(elem_type, options)

    def test_distance(self):
        point_1 = (4, 3)
        point_2 = (9, 4.5)
        distance = Helper.get_distance(point_1, point_2)
        self.assertAlmostEqual(distance, 5.2201532544)


if __name__ == '__main__':
    unittest.main()
