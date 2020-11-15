import unittest
from utils.helper import Helper
from utils.constants import ElementType
from core.star import Star


class TestStarMethods(unittest.TestCase):

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
