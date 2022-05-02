from core.element import Element
from utils.constants import ElementType, Constants
from utils.helper import Helper


class Star:
    """Conditions are:

        Hight temperature: 100MK
        Fusion distance: 1x10-15m
    """

    def __init__(self, base_elements):
        """Star init

        Args:
            base_elements (list): [node_number, x, y]
            constants (Constant): class
        """
        self.name = 'sun'
        self.track_fusion = []
        self._elements = []
        self._ignition(base_elements)

    @property
    def elements(self):
        return self._elements
    
    def life(self):
        '''Start star life
        '''
        while 1:
            # select an element to fusion it
            element_type_candidate = Helper.get_randon_element()
            same_elements = Helper.get_candidates(
                self._elements, element_type_candidate)
            # We need at least two elements to fusion it
            if len(same_elements) < 2:
                continue
            fusion_candidates = Helper.select_candidates(same_elements)
            self._start_fusion(fusion_candidates)
            if len(self._elements) == 2:
                break

    def _start_fusion(self, fusion_candidates) -> None:
        '''Select the elements using temperature and distance
        '''
        temperature = Helper.get_temperature(
            fusion_candidates.candidates, fusion_candidates.avg_distance, len(self._elements))
        if temperature.temperature > Constants.LIMIT_TEMPERATURE and Helper.get_randon_number_between(0, 1, True) > 0.5:
            self._fusion(fusion_candidates.element, temperature.element)

    def _get_next_element_type(self, element_type):
        '''Get next type of element after fusion
        '''
        if element_type == ElementType.HIDROGEN:
            return ElementType.HELIUM
        elif element_type == ElementType.HELIUM:
            return ElementType.CARBON
        return ElementType.CARBON

    def _fusion(self, elem_0, elem_1):
        '''Fusion two elements
        '''
        mid_point = Helper.get_mid_point(elem_0, elem_1)
        new_element_type = self._get_next_element_type(elem_0.element_type)
        new_element = Element(
            1, mid_point[0], mid_point[1], new_element_type)
        # Id for the new element
        new_element.node_id = str(id(new_element))
        # Tracking elements
        new_element.nodes = [elem_0, elem_1]
        new_elements = set(self._elements)
        # Elements to remove
        fusioned = {elem_0, elem_1}
        self._elements = list(new_elements - fusioned)
        self._elements.append(new_element)

    def _ignition(self, base_elements):
        '''Elements creation, at the begining every element
        is hidrogen.
        '''
        for item in base_elements:
            self._elements.append(
                Element(
                    item[0],
                    item[1],
                    item[2],
                    ElementType.HIDROGEN
                )
            )
