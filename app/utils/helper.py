from enum import Enum
import random
from math import sqrt
from operator import itemgetter
from utils.constants import ElementType
from core.element import Element
from dataclasses import dataclass


@dataclass
class Candidates:
    candidates: list
    element: object
    avg_distance: int


class Helper:
    '''Utilities static methods
    '''
    @staticmethod
    def path_size(str_elements: str, distance_matrix: list) -> float:
        """ Total disance
        """
        pos_array = str_elements[:-1].split(',')
        path_index = [int(elem) - 1 for elem in pos_array]
        total = 0.0
        for index in range(len(path_index)):
            if index == len(path_index) - 1:
                return total
            total += distance_matrix[path_index[index]][path_index[index + 1]]

    @staticmethod
    def fusion(elements: list) -> str:
        '''Unpack elements, track atomic elements
        return list adding a comma at the end.
        '''
        chain = ''
        if isinstance(elements, Element):
            if elements.element_type == ElementType.HIDROGEN:
                chain += str(int(elements.node_id)) + ','
                return chain

            chain += Helper.fusion(elements.nodes)
        else:
            for element in elements:
                chain += Helper.fusion(element)
        return chain

    @staticmethod
    def random_list_element(elements):
        '''Simple choice
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
    def get_temperature(near_elements: list, avg_distance: int, total_elements: int):
        '''Temperature using density
        '''
        portion_dist = 0
        for element in near_elements:
            portion_dist += element.get('distance')
        portion_dist = portion_dist/len(near_elements)
        # Calcule of temperature
        return (total_elements*(100.0*portion_dist/avg_distance))/len(near_elements)

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
            # TODO: Fix here, not ordering
            candidates.append({'distance': distance, "element": element})
        avg_distances = sum_distance / len(elements)
        return Candidates(candidates, random_element, avg_distances)

    @ staticmethod
    def get_distance(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        distance = sqrt((p_1[0] - p_0[0])**2 + (p_1[1] - p_0[1])**2)
        return distance

    @ staticmethod
    def get_mid_point(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        return ((p_0.x + p_1.x) / 2, (p_0.y + p_1.y) / 2)
