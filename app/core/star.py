from core.element import Element
from utils.constants import ElementType
from utils.helper import Helper


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
            # We need at least two elements to fusion it
            if len(search_elements) < 2:
                continue
            fusion_candidates = Helper.select_candidates(search_elements)
            self.start_fusion(fusion_candidates)
            if len(self.elements) == 2:
                break

    def start_fusion(self, fusion_candidates):
        '''Select the elements using temperature and distance
        '''
        temperature = Helper.get_temperature(
            fusion_candidates[0], fusion_candidates[2], len(self.elements))
        if temperature > 170 and Helper.get_randon_number_between(0, 1, True) > 0.5:
            final_candidate = Helper.random_list_element(fusion_candidates[0])
            self.fusion(fusion_candidates[1], final_candidate[1])

    def get_next_element_type(self, element_type):
        '''Get next type of element after fusion
        '''
        if element_type == ElementType.HIDROGEN:
            return ElementType.HELIUM
        elif element_type == ElementType.HELIUM:
            return ElementType.CARBON
        return ElementType.CARBON

    def fusion(self, elem_0, elem_1):
        '''Fusion two elements
        '''
        mid_point = Helper.get_mid_point(elem_0, elem_1)
        new_element_type = self.get_next_element_type(elem_0.type)
        new_element = Element(
            1, mid_point[0], mid_point[1], new_element_type)
        # Id for the new element
        new_element.node_id = str(id(new_element))
        # Tracking elements
        new_element.nodes = [elem_0, elem_1]
        new_elements = set(self.elements)
        # Elements to remove
        fusioned = {elem_0, elem_1}
        self.elements = list(new_elements - fusioned)
        self.elements.append(new_element)

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
