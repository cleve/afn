import unittest
from utils.helper import Helper
from utils.constants import ElementType
from core.element import Element
from core.route import tour_length, two_opt, flatten_route, build_best_route


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

    def test_tour_length_open_route(self):
        """With close_loop=False the return edge must not be counted."""
        distance_matrix = [
            [0, 1, 10],
            [1, 0, 2],
            [10, 2, 0],
        ]
        # 1→2 = 1, 2→3 = 2; no closing edge
        self.assertEqual(tour_length(['1', '2', '3'], distance_matrix, close_loop=False), 3)

    def test_tour_length_single_node(self):
        distance_matrix = [[0]]
        self.assertEqual(tour_length(['1'], distance_matrix), 0.0)

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

    # ------------------------------------------------------------------ #
    # flatten_route                                                        #
    # ------------------------------------------------------------------ #

    def test_flatten_route_leaf_element(self):
        """A leaf element (no children) must produce a single-node list."""
        leaf = Element(3, 0.0, 0.0, ElementType.HIDROGEN)
        self.assertEqual(flatten_route(leaf), ['3'])

    def test_flatten_route_nested_tree(self):
        """flatten_route must traverse the full binary tree in order."""
        leaf1 = Element(1, 0.0, 0.0, ElementType.HIDROGEN)
        leaf2 = Element(2, 1.0, 0.0, ElementType.HIDROGEN)
        leaf3 = Element(3, 2.0, 0.0, ElementType.HIDROGEN)
        leaf4 = Element(4, 3.0, 0.0, ElementType.HIDROGEN)

        helium_a = Element(-1, 0.5, 0.0, ElementType.HELIUM)
        helium_a.nodes = [leaf1, leaf2]

        helium_b = Element(-2, 2.5, 0.0, ElementType.HELIUM)
        helium_b.nodes = [leaf3, leaf4]

        carbon = Element(-3, 1.5, 0.0, ElementType.CARBON)
        carbon.nodes = [helium_a, helium_b]

        result = flatten_route(carbon)
        self.assertEqual(result, ['1', '2', '3', '4'])

    def test_flatten_route_list_of_leaves(self):
        """flatten_route must handle a plain list of leaf elements."""
        leaves = [Element(i, 0.0, 0.0, ElementType.HIDROGEN) for i in range(1, 4)]
        result = flatten_route(leaves)
        self.assertEqual(result, ['1', '2', '3'])

    # ------------------------------------------------------------------ #
    # build_best_route                                                     #
    # ------------------------------------------------------------------ #

    def test_build_best_route_single_element(self):
        """A single leaf element must produce a one-node route."""
        leaf = Element(7, 0.0, 0.0, ElementType.HIDROGEN)
        distance_matrix = [[0]]
        result = build_best_route([leaf], distance_matrix)
        self.assertEqual(result, ['7'])

    def test_build_best_route_returns_all_nodes(self):
        """build_best_route must include every leaf node exactly once."""
        leaf1 = Element(1, 0.0, 0.0, ElementType.HIDROGEN)
        leaf2 = Element(2, 5.0, 0.0, ElementType.HIDROGEN)
        leaf3 = Element(3, 5.0, 5.0, ElementType.HIDROGEN)
        leaf4 = Element(4, 0.0, 5.0, ElementType.HIDROGEN)

        helium_a = Element(-1, 2.5, 0.0, ElementType.HELIUM)
        helium_a.nodes = [leaf1, leaf2]
        helium_b = Element(-2, 2.5, 5.0, ElementType.HELIUM)
        helium_b.nodes = [leaf3, leaf4]

        distance_matrix = [
            [0, 5, 7, 5],
            [5, 0, 5, 7],
            [7, 5, 0, 5],
            [5, 7, 5, 0],
        ]

        result = build_best_route([helium_a, helium_b], distance_matrix)
        self.assertEqual(len(result), 4)
        self.assertEqual(set(result), {'1', '2', '3', '4'})

    def test_build_best_route_minimises_tour_length(self):
        """build_best_route must prefer the shorter of competing orientations."""
        # Square: 1(0,0) 2(1,0) 3(1,1) 4(0,1)
        # Best tours are 1>2>3>4 or its reverse/rotations with length 4.
        # A crossed tour (1>3>2>4) has length > 4.
        leaf1 = Element(1, 0.0, 0.0, ElementType.HIDROGEN)
        leaf2 = Element(2, 1.0, 0.0, ElementType.HIDROGEN)
        leaf3 = Element(3, 1.0, 1.0, ElementType.HIDROGEN)
        leaf4 = Element(4, 0.0, 1.0, ElementType.HIDROGEN)

        seg_a = Element(-1, 0.5, 0.0, ElementType.HELIUM)
        seg_a.nodes = [leaf1, leaf2]
        seg_b = Element(-2, 0.5, 1.0, ElementType.HELIUM)
        seg_b.nodes = [leaf3, leaf4]

        import math
        d = [[math.dist((e.x, e.y), (f.x, f.y)) for f in [leaf1, leaf2, leaf3, leaf4]]
             for e in [leaf1, leaf2, leaf3, leaf4]]

        result = build_best_route([seg_a, seg_b], d)
        self.assertAlmostEqual(tour_length(result, d), 4.0, places=5)


if __name__ == '__main__':
    unittest.main()
