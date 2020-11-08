import numpy
import sys
from core.element import Element
from utils.constants import ElementType
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

    def fusion(self, elem_0, elem_1):
        '''Main process
        '''

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
