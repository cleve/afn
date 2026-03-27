from collections import Counter
import random

from core.element import Element
from utils.constants import ElementType, Constants
from utils.helper import Helper
from utils.geometry import midpoint
from core.route import optimize_internal_structure


class Star:
    """Conditions are:

        Hight temperature: 100MK
        Fusion distance: 1x10-15m
    """

    def __init__(self, base_elements, distance_matrix):
        """Star init

        Args:
            base_elements (list): [node_number, x, y]
            distance_matrix (list): matrix repr
        """
        self.name = 'sun'
        self.distance_matrix = distance_matrix
        self.track_fusion = []
        self._elements = []
        self._ignition(base_elements)

    @property
    def elements(self):
        return self._elements
    
    def life(self):
        '''Start star life
        '''
        idle_cycles = 0
        max_idle_cycles = max(10, len(self._elements) * 8)

        while len(self._elements) > 2:
            fusion_candidates = self._get_random_fusion_candidates()
            fused = False

            if fusion_candidates is not None:
                fused = self._start_fusion(fusion_candidates)

            if fused:
                idle_cycles = 0
                continue

            idle_cycles += 1
            if idle_cycles < max_idle_cycles:
                continue

            fallback_candidates = self._get_fallback_pair()
            if fallback_candidates is None:
                break

            self._fusion(fallback_candidates[0], fallback_candidates[1])
            idle_cycles = 0

    def _get_random_fusion_candidates(self):
        element_type_candidate = Helper.get_random_element()
        same_elements = Helper.get_candidates(self._elements, element_type_candidate)
        if len(same_elements) >= 2:
            return Helper.select_candidates(same_elements)

        candidates_by_type = {
            element_type: elements
            for element_type, elements in self._group_elements_by_type().items()
            if len(elements) >= 2
        }
        if not candidates_by_type:
            return None

        element_type = max(candidates_by_type, key=lambda candidate_type: len(candidates_by_type[candidate_type]))
        return Helper.select_candidates(candidates_by_type[element_type])

    def _group_elements_by_type(self):
        grouped_elements = {}
        for element in self._elements:
            grouped_elements.setdefault(element.element_type, []).append(element)
        return grouped_elements

    def _get_fallback_pair(self):
        if len(self._elements) < 2:
            return None

        element_counts = Counter(element.element_type for element in self._elements)
        same_type_pairs = [
            element_type for element_type, count in element_counts.items()
            if count >= 2
        ]
        if same_type_pairs:
            prioritized_type = max(same_type_pairs, key=element_counts.get)
            candidates = self._group_elements_by_type()[prioritized_type]
        else:
            candidates = self._elements

        anchor = min(candidates, key=lambda element: (element.x, element.y, element.node_id))
        partner = min(
            (element for element in candidates if element is not anchor),
            key=lambda element: Helper.get_distance(anchor.get_coordinates(), element.get_coordinates())
        )
        return (anchor, partner)

    def _start_fusion(self, fusion_candidates) -> bool:
        '''Select the elements using temperature and distance
        '''
        temperature = Helper.get_temperature(
            fusion_candidates.candidates, fusion_candidates.avg_distance, len(self._elements))
        if temperature.element is None:
            return False

        if temperature.temperature > Constants.LIMIT_TEMPERATURE and random.random() > 0.5:
            self._fusion(fusion_candidates.element, temperature.element)
            return True
        return False

    def _get_next_element_type(self, element_type):
        '''Get next type of element after fusion
        '''
        if element_type == ElementType.HIDROGEN:
            return ElementType.HELIUM
        elif element_type == ElementType.HELIUM:
            return ElementType.CARBON
        return ElementType.CARBON

    def _resolve_element_type(self, elem_0, elem_1):
        if elem_0.element_type == elem_1.element_type:
            return self._get_next_element_type(elem_0.element_type)
        return max(elem_0.element_type, elem_1.element_type, key=lambda item: item.value)

    def _fusion(self, elem_0, elem_1):
        '''Fusion two elements
        '''
        mid_point = midpoint(elem_0, elem_1)
        new_element_type = self._resolve_element_type(elem_0, elem_1)
        new_element = Element(
            1, mid_point[0], mid_point[1], new_element_type)
        # Id for the new element
        new_element.node_id = str(id(new_element))
        # Optimal internal structure
        optimize_internal_structure(elem_0, elem_1, self.distance_matrix)
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
