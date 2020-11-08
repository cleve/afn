import numpy
import sys
from core.element import Element
from utils.constants import ElementType
from utils.helper import Helper
numpy.set_printoptions(threshold=sys.maxsize)


class Star:
    """Conditions are:

        Hight temperature: 100MK
        Fusion distance: 1x10-15m
    """

    def __init__(self, base_elements, constants):
        # Debug
        self.DEBUG = True
        self.name = 'sun'
        self.track_fusion = []
        self.elements = []
        self.constants = constants
        self.ignition(base_elements)

    def life(self):
        '''Star life
        '''
        while 1:
            # select an element to fusion it
            element_type_candidate = Helper.get_randon_element()
            search_elements = Helper.get_candidates(
                self.elements, element_type_candidate)
            if len(search_elements) == 0:
                continue
            fusion_candidates = Helper.select_candidates(search_elements)
            print(fusion_candidates)
            self.start_fusion(fusion_candidates)
            break

    def start_fusion(self, fusion_candidates):
        '''Select the elements using temperature and distance
        '''
        temperature = Helper.get_temperature(
            fusion_candidates[0], fusion_candidates[2], len(self.elements))
        print('>>', temperature)

    def fusion(self, elem_0, elem_1):
        '''Fusion two elements
        '''
        pass

    def ignition(self, base_elements):
        '''Element creation
        '''
        element = ElementType.HIDROGEN
        for item in base_elements:
            self.elements.append(
                Element(
                    item[0],
                    item[1],
                    item[2],
                    element
                )
            )
