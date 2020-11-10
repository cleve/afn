import random
import numpy
from operator import itemgetter
from utils.constants import ElementType


class Helper:
    '''Utilities static methods
    '''
    @staticmethod
    def random_list_element(elements):
        return random.choice(elements)

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
        candidates = filter(lambda element: element.type ==
                            filter_type, elements)
        return list(candidates)

    @staticmethod
    def get_temperature(near_elements, avg_distance, total_elements):
        '''Temperature using density
        '''
        portion_dist = 0
        for element in near_elements:
            portion_dist += element[0]
        portion_dist = portion_dist/len(near_elements)
        # Calcule of temperature
        return (total_elements*(100.0*portion_dist/avg_distance))/len(near_elements)

    @staticmethod
    def select_candidates(elements):
        """Search several options for fusion
        selecting 10% of the elements
            return [list], element, avg_distance
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
        index = random.randint(int(0.1 * len(elements)),
                               int(len(elements) / 2))
        avg_distances = avg_distances/(len(elements) - 1)
        return sorted(distances, key=itemgetter(0))[:index if index > 0 else len(distances)], random_element, avg_distances

    @ staticmethod
    def get_distance(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        distance = numpy.sqrt((p_1[0] - p_0[0])**2 + (p_1[1] - p_0[1])**2)
        return distance

    @ staticmethod
    def get_mid_point(p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        return ((p_0.x + p_1.x) / 2, (p_0.y + p_1.y) / 2)
