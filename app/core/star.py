import numpy
from utils.utils import Utils
from core.element import Element
import sys
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
        self.utils = Utils()
        self.ignition(base_elements)

    def fusion(self, elem_0, elem_1):
        pass

    def ignition(self, base_elements):
        '''Element creation
        '''
        element = 'H'
        for item in base_elements:
            self.elements.append(
                Element(
                    item[0],
                    item[1],
                    item[2],
                    element
                )
            )
