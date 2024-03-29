from enum import Enum
import random
from math import sqrt, inf
from operator import itemgetter
from utils.constants import Constants, ElementType
from core.element import Element
from dataclasses import dataclass
from collections import namedtuple
from itertools import combinations


@dataclass
class Candidates:
    candidates: list
    element: object
    avg_distance: int


class Helper:
    '''Utilities static methods
    '''
    @staticmethod
    def namedtuple_factory(tuple_name: str, keys: str) -> namedtuple:
        """Get a named tuple object

        Args:
            tuple_name (str): Name to be instantiated
            keys (str): key space separated

        Returns:
            namedtuple: object instance
        """
        return namedtuple(tuple_name, keys)
    
    @staticmethod
    def path_size(nodes: list, distance_matrix: list) -> float:
        """ Total disance
        """
        path_index = [int(node) - 1 for node in nodes]
        total = 0.0
        for index in range(len(path_index)):
            if index == len(path_index) - 1:
                return total
            total += distance_matrix[path_index[index]][path_index[index + 1]]

    @staticmethod
    def fision(elements: list) -> str:
        '''Unpack elements, track atomic elements
        return list adding a comma at the end.
        '''
        chain = []
        if isinstance(elements, Element):
            # Border condition, the elemental state.
            if elements.element_type == ElementType.HIDROGEN:
                return [str(int(elements.node_id))]

            return Helper.fision(elements.nodes)
        else:
            chain = Helper.fision(elements[0]) + Helper.fision(elements[1])
        return chain

    @staticmethod
    def random_list_element(elements: list) -> dict:
        '''random.choice wrapper
        '''
        return random.choice(elements)

    @staticmethod
    def get_randon_element():
        '''Select uniform element
        '''
        return random.choice([
            ElementType.HIDROGEN,
            ElementType.HELIUM,
            ElementType.CARBON])

    @staticmethod
    def get_randon_number():
        '''Integer random (0, 100000)
        '''
        return str(random.randint(0, 10000))

    @staticmethod
    def get_randon_number_between(min_border, max_border, is_number=False):
        '''Integer random (a, b)
        '''
        if is_number:
            return random.randint(min_border, max_border)
        return str(random.randint(min_border, max_border))

    @staticmethod
    def get_candidates(elements: list, filter_type: Enum) -> list:
        '''Candidates using filter element
        '''
        candidates = filter(
            lambda element: element.element_type == filter_type, elements)
        return list(candidates)

    @staticmethod
    def get_temperature(near_elements: list, avg_distance: int, total_elements: int) -> namedtuple:
        '''Temperature using density
        '''
        Temperature = Helper.namedtuple_factory(
            "Temperature", "temperature element")
        ratio_elements = len(near_elements) / total_elements
        ratio = inf
        element_selected = None
        for element in near_elements:
            if element.get('distance') < ratio:
                ratio = element.get('distance')
                element_selected = element.get('element')
        # Calcule of temperature
        temp = Constants.LIMIT_TEMPERATURE *1.1
        if len(near_elements) < 4:
            return Temperature(
                temp*ratio_elements + temp*ratio, random.choice(near_elements).get('element'))
        ratio = ratio / avg_distance
        return Temperature(
            temp*ratio_elements + temp*ratio, element_selected)

    @staticmethod
    def select_candidates(elements: list) -> Candidates:
        """Search several options for fusion
            elements: List o same elements
            return Candidate object
        """
        avg_distances = 0
        sum_distance = 0
        candidates = []
        selected_elements = []

        # List of same elements
        element_set = set(elements)

        # Observing one element
        random_element = element_set.pop()

        # Limit selection
        selection = random.randint(
            2, len(elements))

        for _ in range(selection):
            if len(element_set) == 0:
                break
            selected_elements.append(element_set.pop())
        for element in selected_elements:
            distance = Helper.get_distance(
                (random_element.x, random_element.y),
                (element.x, element.y)
            )
            # Ignore self element
            if distance == 0:
                continue
            sum_distance += distance
            candidates.append({'distance': distance, "element": element})
        avg_distances = sum_distance / len(elements)
        return Candidates(candidates, random_element, avg_distances)

    @ staticmethod
    def get_distance(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        distance = sqrt((p_1[0] - p_0[0])**2 + (p_1[1] - p_0[1])**2)
        return distance

    @staticmethod
    def set_internal_structure(elem_0, elem_1, distance_matrix) -> None:
        """Determine the best structure

        Args:
            elem_0 (Element): First element
            elem_1 (Element): Second element
            distance_matrix: Primiary matrix
        """
        # Check combinations
        if elem_0.element_type == ElementType.HELIUM:
            comb = combinations(elem_0.nodes + elem_1.nodes, 2)
            min_dist = inf
            union = None
            for tup in comb:
                dist = distance_matrix[int(tup[0].node_id - 1)][int(tup[1].node_id - 1)]
                if dist != 0 and dist < min_dist:
                    min_dist = dist
                    union = tup
            # elem_0
            if elem_0.nodes[0] == union[0]:
                elem_0.nodes[0], elem_0.nodes[1] = elem_0.nodes[1], elem_0.nodes[0]
            # elem_1
            if elem_1.nodes[1] == union[1]:
                elem_1.nodes[0], elem_1.nodes[1] = elem_1.nodes[1], elem_1.nodes[0]

    @ staticmethod
    def get_mid_point(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        return ((p_0.x + p_1.x) / 2, (p_0.y + p_1.y) / 2)
