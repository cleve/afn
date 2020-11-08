import random
import numpy
from operator import itemgetter
from utils.constants import ElementType


class Helper:
    '''Utilities static methods
    '''
    @staticmethod
    def get_randon_element():
        '''Select uniform element
        '''
        elem_candidates = [
            ElementType.HIDROGEN,
            ElementType.HELIUM,
            ElementType.CARBON
        ]
        return numpy.random.choice(elem_candidates)

    @staticmethod
    def get_randon_number():
        '''Integer random (0, 100000)
        '''
        return str(random.randint(0, 10000))

    @staticmethod
    def get_randon_number_between(min_border, max_border):
        '''Integer random (a, b)
        '''
        return str(random.randint(min_border, max_border))

    @staticmethod
    def get_candidates(elements, filter_type):
        '''Candidates using filter element
        '''
        print(filter_type)
        candidates = filter(lambda element: element.type ==
                            filter_type, elements)
        return list(candidates)

    @staticmethod
    def get_temperature(near_elements):
        pass

    @staticmethod
    def select_candidates(elements):
        """Search several options for fusion
        selecting 10% of the elements
            return [list], avg_distance
        """
        random_element = numpy.random.choice(elements)
        avg_distances = 0
        distances = []
        for element in elements:
            distance = Helper.get_distance(
                (random_element.x, random_element.y),
                (element.x, element.y)
            )
            if distance == 0:
                continue
            avg_distances += distance
            distances.append([distance, element])
        index = int(0.1 * len(elements))
        avg_distances = avg_distances/(len(elements) - 1)
        return sorted(distances, key=itemgetter(0))[:index], avg_distances

    @staticmethod
    def get_distance(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        distance = numpy.sqrt((p_1[0] - p_0[0])**2 + (p_1[1] - p_0[1])**2)
        return distance
