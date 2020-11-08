import random


class Helper:
    '''Utilities static methods
    '''
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
        return candidates
