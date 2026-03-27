import unittest
from utils.helper import Helper
from utils.constants import ElementType
from core.element import Element
from core.route import tour_length, two_opt


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
        elem_type = Helper.get_random_element()
        self.assertIn(elem_type, options)

    def test_distance(self):
        point_1 = (4, 3)
        point_2 = (9, 4.5)
        distance = Helper.get_distance(point_1, point_2)
        self.assertAlmostEqual(distance, 5.2201532544)

    def test_tour_length_closes_the_route(self):
        distance_matrix = [
            [0, 1, 10],
            [1, 0, 2],
            [10, 2, 0],
        ]
        self.assertEqual(tour_length(['1', '2', '3'], distance_matrix), 13)

    def test_two_opt_improves_crossed_route(self):
        distance_matrix = [
            [0, 2, 3, 2],
            [2, 0, 2, 3],
            [3, 2, 0, 2],
            [2, 3, 2, 0],
        ]
        route = ['1', '3', '2', '4']

        improved_route = two_opt(route, distance_matrix)

        self.assertLess(tour_length(improved_route, distance_matrix), tour_length(route, distance_matrix))


if __name__ == '__main__':
    unittest.main()
