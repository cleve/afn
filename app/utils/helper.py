import random
from math import inf
from enum import Enum

from utils.constants import Constants, ElementType
from dataclasses import dataclass
from collections import namedtuple
from utils.geometry import euclidean_distance


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
    def random_list_element(elements: list) -> dict:
        '''random.choice wrapper
        '''
        return random.choice(elements)

    @staticmethod
    def get_random_element():
        '''Select uniform element
        '''
        return random.choice([
            ElementType.HIDROGEN,
            ElementType.HELIUM,
            ElementType.CARBON])

    @staticmethod
    def get_randon_element():
        return Helper.get_random_element()

    @staticmethod
    def get_random_number():
        '''Integer random (0, 100000)
        '''
        return str(random.randint(0, 10000))

    @staticmethod
    def get_randon_number():
        return Helper.get_random_number()

    @staticmethod
    def get_random_number_between(min_border, max_border, is_number=False):
        '''Integer random (a, b)
        '''
        if is_number:
            return random.randint(min_border, max_border)
        return str(random.randint(min_border, max_border))

    @staticmethod
    def get_randon_number_between(min_border, max_border, is_number=False):
        return Helper.get_random_number_between(min_border, max_border, is_number)

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
        if not near_elements:
            return Temperature(0, None)

        ratio_elements = len(near_elements) / total_elements
        nearest = min(near_elements, key=lambda element: element.get('distance'))
        distance_ratio = 1.0
        if avg_distance:
            distance_ratio = avg_distance / nearest.get('distance')
        temp = Constants.LIMIT_TEMPERATURE * 1.1
        if len(near_elements) < 4:
            return Temperature(
                temp * (ratio_elements + distance_ratio), random.choice(near_elements).get('element'))
        return Temperature(
            temp * (ratio_elements + distance_ratio), nearest.get('element'))

    @staticmethod
    def select_candidates(elements: list) -> Candidates:
        """Search several options for fusion
            elements: List o same elements
            return Candidate object
        """
        random_element = random.choice(elements)
        selectable_elements = [element for element in elements if element is not random_element]
        if not selectable_elements:
            return Candidates([], random_element, 0)

        selection = random.randint(1, len(selectable_elements))
        selected_elements = random.sample(selectable_elements, selection)

        candidates = []
        sum_distance = 0.0
        for element in selected_elements:
            distance = Helper.get_distance(
                (random_element.x, random_element.y),
                (element.x, element.y)
            )
            sum_distance += distance
            candidates.append({'distance': distance, 'element': element})

        avg_distances = sum_distance / len(candidates)
        return Candidates(candidates, random_element, avg_distances)

    @staticmethod
    def get_distance(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        return euclidean_distance(p_0, p_1)

    @staticmethod
    def get_mid_point(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        return ((p_0.x + p_1.x) / 2, (p_0.y + p_1.y) / 2)
