from itertools import permutations, product
from math import inf
from typing import Sequence

from core.element import Element
from utils.constants import ElementType


DistanceMatrix = Sequence[Sequence[float]]


def _leaf_nodes(element) -> list[Element]:
    if not element.nodes:
        return [element]
    return _leaf_nodes(element.nodes[0]) + _leaf_nodes(element.nodes[1])


def flatten_route(elements) -> list[str]:
    """Expand a fused element tree into the ordered list of node ids."""
    if isinstance(elements, Element):
        if not elements.nodes:
            return [str(int(elements.node_id))]
        return flatten_route(elements.nodes[0]) + flatten_route(elements.nodes[1])

    route = []
    for element in elements:
        route.extend(flatten_route(element))
    return route


def tour_length(route: list[str], distance_matrix: DistanceMatrix, close_loop: bool = True) -> float:
    """Return the total length of a route using the precomputed distance matrix."""
    if len(route) < 2:
        return 0.0

    path_index = [int(node) - 1 for node in route]
    total = 0.0
    for index in range(len(path_index) - 1):
        total += distance_matrix[path_index[index]][path_index[index + 1]]
    if close_loop:
        total += distance_matrix[path_index[-1]][path_index[0]]
    return total


def two_opt(route: list[str], distance_matrix: DistanceMatrix) -> list[str]:
    """Improve a tour with a standard 2-opt local search pass."""
    if len(route) < 4:
        return route

    best_route = route[:]
    improved = True
    route_size = len(best_route)

    while improved:
        improved = False
        for left in range(1, route_size - 2):
            left_prev = int(best_route[left - 1]) - 1
            left_node = int(best_route[left]) - 1
            for right in range(left + 1, route_size - 1):
                right_node = int(best_route[right]) - 1
                right_next = int(best_route[(right + 1) % route_size]) - 1

                current_cost = (
                    distance_matrix[left_prev][left_node]
                    + distance_matrix[right_node][right_next]
                )
                swapped_cost = (
                    distance_matrix[left_prev][right_node]
                    + distance_matrix[left_node][right_next]
                )
                if swapped_cost < current_cost:
                    best_route[left:right + 1] = reversed(best_route[left:right + 1])
                    improved = True
                    break
            if improved:
                break

    return best_route


def build_best_route(elements, distance_matrix: DistanceMatrix) -> list[str]:
    """Evaluate top-level route orientations and return the best route found."""
    if isinstance(elements, Element):
        return flatten_route(elements)
    if not elements:
        return []
    if len(elements) == 1:
        return flatten_route(elements[0])

    flattened_routes = [flatten_route(element) for element in elements]
    best_route = None
    best_length = inf

    for ordered_routes in permutations(flattened_routes):
        for reverse_flags in product((False, True), repeat=len(ordered_routes)):
            candidate_route = []
            for route, reverse_flag in zip(ordered_routes, reverse_flags):
                candidate_route.extend(reversed(route) if reverse_flag else route)
            candidate_length = tour_length(candidate_route, distance_matrix)
            if candidate_length < best_length:
                best_length = candidate_length
                best_route = candidate_route

    return best_route


def optimize_internal_structure(elem_0, elem_1, distance_matrix) -> None:
    """Orient paired helium nodes so the closest leaves become adjacent."""
    if elem_0.element_type != ElementType.HELIUM:
        return

    left_leaf_nodes = _leaf_nodes(elem_0)
    right_leaf_nodes = _leaf_nodes(elem_1)

    min_dist = inf
    union = None
    for left in left_leaf_nodes:
        for right in right_leaf_nodes:
            dist = distance_matrix[int(left.node_id) - 1][int(right.node_id) - 1]
            if dist != 0 and dist < min_dist:
                min_dist = dist
                union = (left, right)

    if union is None:
        return

    if len(elem_0.nodes) == 2 and elem_0.nodes[0] == union[0]:
        elem_0.nodes[0], elem_0.nodes[1] = elem_0.nodes[1], elem_0.nodes[0]
    if len(elem_1.nodes) == 2 and elem_1.nodes[1] == union[1]:
        elem_1.nodes[0], elem_1.nodes[1] = elem_1.nodes[1], elem_1.nodes[0]