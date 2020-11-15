import random
import numpy
from operator import itemgetter
from utils.constants import ElementType
from core.element import Element


class Helper:
    '''Utilities static methods
    '''
    @staticmethod
    def path_size(str_elements, distance_matrix):
        '''Size
        '''
        pos_array = str_elements.split(',')[:-1]
        path_index = [int(float(elem)) - 1 for elem in pos_array]
        total = 0.0
        for index in range(len(path_index)):
            if index == len(path_index) - 1:
                return total
            total += distance_matrix[path_index[index]][path_index[index + 1]]

    @staticmethod
    def fision(elements):
        '''Unpack elements
        '''
        chain = ''
        if isinstance(elements, Element):
            if elements.type == ElementType.HIDROGEN:
                chain += str(int(elements.node_id)) + ','
                return chain

            chain += Helper.fision(elements.nodes)
        else:
            for element in elements:
                chain += Helper.fision(element)
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
    def get_randon_number_between(min_border, max_border, is_number=False):
        '''Integer random (a, b)
        '''
        if is_number:
            return random.randint(min_border, max_border)
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
        element_set = set(elements)
        random_element = element_set.pop()
        avg_distances = 0
        sum_distance = 0
        distances = []
        selected_elements = []
        selection = Helper.get_randon_number_between(
            2, len(elements), is_number=True)
        for _iteration in range(selection):
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
            distances.append([distance, element])
        avg_distances = sum_distance / len(elements)
        return distances, random_element, avg_distances

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
