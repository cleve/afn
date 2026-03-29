from itertools import combinations
from math import exp
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

    DEFAULT_FUSION_WEIGHTS = {
        'score': 0.50,
        'distance': 0.20,
        'barrier': 0.20,
        'route_gain': 0.10,
    }

    def __init__(self, base_elements, distance_matrix, fusion_weights: dict | None = None):
        """Star init

        Args:
            base_elements (list): [node_number, x, y]
            distance_matrix (list): matrix repr
            fusion_weights (dict | None): optional overrides for fusion-probability weights.
                Keys: 'score', 'distance', 'barrier', 'route_gain'.
                Missing keys fall back to DEFAULT_FUSION_WEIGHTS.
        """
        self.name = 'sun'
        self.distance_matrix = distance_matrix
        self.track_fusion = []
        self.fusion_events = []
        self._elements = []
        self._initial_count = len(base_elements)
        self.core_temperature = Constants.LIMIT_TEMPERATURE * 1.05
        self.density = 1.0
        self.pressure = 1.0
        self._fusion_weights = {**self.DEFAULT_FUSION_WEIGHTS, **(fusion_weights or {})}
        self._ignition(base_elements)

    @property
    def elements(self):
        return self._elements
    
    def life(self):
        '''Start star life
        '''
        idle_cycles = 0
        max_idle_cycles = max(10, len(self._elements) * 2)
        step = 0

        while len(self._elements) > 2:
            step += 1
            fusion_pair = self._select_pair_for_fusion()
            if fusion_pair is None:
                break

            fusion_event = self._start_fusion(fusion_pair, step)

            if fusion_event is not None:
                self.fusion_events.append(fusion_event)
                idle_cycles = 0
                continue

            idle_cycles += 1
            collapse_probability = self._collapse_probability(idle_cycles, max_idle_cycles)
            if idle_cycles < max_idle_cycles and random.random() > collapse_probability:
                self._update_core_state(False, 0.0)
                continue

            fallback_pair = self._get_fallback_pair()
            if fallback_pair is None:
                break

            fallback_midpoint = self._fusion(fallback_pair[0], fallback_pair[1])
            self._update_core_state(True, fallback_pair[2]['score'])
            self.track_fusion.append((
                fallback_pair[0].node_id,
                fallback_pair[1].node_id,
                round(fallback_pair[2]['score'], 4),
                1.0
            ))
            self.fusion_events.append(
                self._build_fusion_event(
                    step=step,
                    elem_0=fallback_pair[0],
                    elem_1=fallback_pair[1],
                    profile=fallback_pair[2],
                    probability=1.0,
                    midpoint=fallback_midpoint,
                    forced=True
                )
            )
            idle_cycles = 0

    def _build_fusion_event(self, step, elem_0, elem_1, profile, probability, midpoint, forced=False):
        return {
            'step': step,
            'left_id': str(elem_0.node_id),
            'right_id': str(elem_1.node_id),
            'left_pos': elem_0.get_coordinates(),
            'right_pos': elem_1.get_coordinates(),
            'midpoint': midpoint,
            'score': float(profile.get('score', 0.0)),
            'probability': float(probability),
            'forced': forced,
            'temperature': float(self.core_temperature),
            'density': float(self.density),
            'pressure': float(self.pressure),
            'elements_count': len(self._elements),
        }

    def _get_pair_candidates(self):
        if len(self._elements) < 2:
            return []

        pairs = []
        avg_pair_distance = self._average_pair_distance()
        for left, right in combinations(self._elements, 2):
            distance = Helper.get_distance(left.get_coordinates(), right.get_coordinates())
            barrier = self._fusion_barrier(left, right)
            route_gain = self._route_gain(left, right)
            local_heat = (left.local_heat + right.local_heat) / 2.0
            score = self._pair_score(distance, avg_pair_distance, barrier, route_gain, local_heat)
            profile = {
                'score': score,
                'distance': distance,
                'avg_distance': avg_pair_distance,
                'barrier': barrier,
                'route_gain': route_gain,
            }
            pairs.append((left, right, profile))
        return pairs

    def _average_pair_distance(self):
        if len(self._elements) < 2:
            return 1.0

        total = 0.0
        count = 0
        for left, right in combinations(self._elements, 2):
            total += Helper.get_distance(left.get_coordinates(), right.get_coordinates())
            count += 1
        return total / count if count else 1.0

    def _fusion_barrier(self, elem_0, elem_1):
        if elem_0.element_type == ElementType.HIDROGEN and elem_1.element_type == ElementType.HIDROGEN:
            return 0.35
        if elem_0.element_type == ElementType.HELIUM and elem_1.element_type == ElementType.HELIUM:
            return 0.90
        if elem_0.element_type == ElementType.CARBON and elem_1.element_type == ElementType.CARBON:
            return 1.10
        return 0.65

    def _leaf_nodes(self, element):
        if not element.nodes:
            return [element]
        return self._leaf_nodes(element.nodes[0]) + self._leaf_nodes(element.nodes[1])

    def _route_gain(self, elem_0, elem_1):
        leaf_0 = self._leaf_nodes(elem_0)
        leaf_1 = self._leaf_nodes(elem_1)

        nearest_bridge = min(
            self.distance_matrix[int(left.node_id) - 1][int(right.node_id) - 1]
            for left in leaf_0
            for right in leaf_1
        )

        spread_0 = 0.0
        spread_1 = 0.0
        if len(leaf_0) > 1:
            spread_0 = max(
                self.distance_matrix[int(left.node_id) - 1][int(right.node_id) - 1]
                for left, right in combinations(leaf_0, 2)
            )
        if len(leaf_1) > 1:
            spread_1 = max(
                self.distance_matrix[int(left.node_id) - 1][int(right.node_id) - 1]
                for left, right in combinations(leaf_1, 2)
            )

        baseline = 1.0 + spread_0 + spread_1
        return max(0.0, (spread_0 + spread_1 - nearest_bridge) / baseline)

    def _pair_score(self, distance, avg_pair_distance, barrier, route_gain, local_heat=0.0):
        distance_term = 1.0 / (1.0 + distance)

        density_factor = max(0.2, self.density)
        normalized_distance = avg_pair_distance / (distance + 1e-9)
        pressure_boost = 0.20 * self.pressure + 0.15 * normalized_distance

        return (
            0.45 * distance_term
            + 0.40 * route_gain
            - 0.15 * barrier
            + 0.12 * density_factor
            + pressure_boost
            + 0.10 * local_heat
        )

    def _select_pair_for_fusion(self):
        pair_candidates = self._get_pair_candidates()
        if not pair_candidates:
            return None

        max_score = max(candidate[2]['score'] for candidate in pair_candidates)
        min_weight = 1e-6
        selection_temperature = self._selection_temperature()
        weighted = []
        for elem_0, elem_1, profile in pair_candidates:
            noisy_score = profile['score'] + self._stochastic_noise(0.05)
            weight = max(min_weight, exp((noisy_score - max_score) / selection_temperature))
            weighted.append((elem_0, elem_1, profile, weight))

        total_weight = sum(item[3] for item in weighted)
        threshold = random.uniform(0.0, total_weight)
        cumulative = 0.0
        for elem_0, elem_1, profile, weight in weighted:
            cumulative += weight
            if cumulative >= threshold:
                return (elem_0, elem_1, profile)

        elem_0, elem_1, profile, _ = weighted[-1]
        return (elem_0, elem_1, profile)

    def _get_fallback_pair(self):
        pair_candidates = self._get_pair_candidates()
        if not pair_candidates:
            return None
        return max(pair_candidates, key=lambda candidate: candidate[2]['score'])

    def _selection_temperature(self):
        # Higher pressure and density sharpen selection; early stages remain more exploratory.
        stage_ratio = len(self._elements) / max(1, self._initial_count)
        base = 0.45 + 0.45 * stage_ratio
        pressure_effect = 1.0 / (1.0 + 0.20 * self.pressure)
        density_effect = 1.0 / (1.0 + 0.30 * self.density)
        return max(0.20, min(1.20, base * pressure_effect * density_effect))

    def _stochastic_noise(self, scale=0.05):
        return random.uniform(-scale, scale)

    def _collapse_probability(self, idle_cycles: int, max_idle_cycles: int):
        idle_ratio = idle_cycles / max(1, max_idle_cycles)
        thermal_ratio = self.core_temperature / Constants.LIMIT_TEMPERATURE
        pressure_ratio = self.pressure / 2.5
        activation = 2.6 * idle_ratio + 0.25 * pressure_ratio - 0.15 * thermal_ratio
        return 1.0 / (1.0 + exp(-activation))

    def _fusion_probability(self, profile):
        if isinstance(profile, dict):
            score = profile.get('score', 0.0)
            distance = profile.get('distance', 1.0)
            avg_distance = profile.get('avg_distance', 1.0)
            barrier = profile.get('barrier', 0.7)
            route_gain = profile.get('route_gain', 0.0)
        else:
            score = profile
            distance = 1.0
            avg_distance = 1.0
            barrier = 0.7
            route_gain = 0.0

        thermal_drive = (
            (self.core_temperature / Constants.LIMIT_TEMPERATURE)
            + 0.30 * self.density
            + 0.20 * self.pressure
        )

        score_probability = 1.0 / (1.0 + exp(-((score + 0.40 * thermal_drive) / 0.90)))
        distance_probability = exp(-distance / (avg_distance + 1e-9))
        barrier_probability = exp(-barrier / max(0.25, thermal_drive))

        w = self._fusion_weights
        probability = (
            w['score'] * score_probability
            + w['distance'] * distance_probability
            + w['barrier'] * barrier_probability
            + w['route_gain'] * route_gain
        )
        return max(0.0, min(1.0, probability))

    def _update_core_state(self, fused: bool, score: float):
        if fused:
            self.core_temperature = max(
                Constants.LIMIT_TEMPERATURE * 0.9,
                self.core_temperature + 2.0 + 4.0 * max(0.0, score)
            )
            self.pressure = min(2.5, self.pressure + 0.08)
        else:
            self.core_temperature = max(
                Constants.LIMIT_TEMPERATURE * 0.7,
                self.core_temperature * 0.992
            )
            self.pressure = max(0.7, self.pressure * 0.996)

        self.density = max(0.2, len(self._elements) / max(1, self._initial_count))
        # Decay local heat each cycle
        for elem in self._elements:
            elem.local_heat = max(0.0, elem.local_heat * 0.80)

    def _start_fusion(self, fusion_pair, step):
        '''Select the elements using temperature and distance
        '''
        elem_0, elem_1, profile = fusion_pair
        probability = self._fusion_probability(profile)
        if random.random() <= probability:
            fusion_midpoint = self._fusion(elem_0, elem_1)
            self._update_core_state(True, profile['score'])
            self.track_fusion.append((
                elem_0.node_id,
                elem_1.node_id,
                round(profile['score'], 4),
                round(probability, 4)
            ))
            return self._build_fusion_event(
                step=step,
                elem_0=elem_0,
                elem_1=elem_1,
                profile=profile,
                probability=probability,
                midpoint=fusion_midpoint,
                forced=False
            )

        self._update_core_state(False, profile['score'])
        return None

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

    def _propagate_fusion_heat(self, site_x, site_y, energy: float):
        '''Distribute heat from a fusion event to surviving elements.

        Uses a Gaussian kernel so nearby elements receive more heat than
        distant ones.  The characteristic radius is scaled by the average
        pair distance so that the effect is meaningful regardless of problem
        size.
        '''
        avg_dist = self._average_pair_distance()
        sigma = max(1.0, avg_dist * 0.5)
        for elem in self._elements:
            d = Helper.get_distance((site_x, site_y), elem.get_coordinates())
            heat = energy * exp(-(d ** 2) / (2.0 * sigma ** 2))
            elem.local_heat = min(1.0, elem.local_heat + heat)

    def _fusion(self, elem_0, elem_1):
        '''Fusion two elements
        '''
        mid_point = midpoint(elem_0, elem_1)
        new_element_type = self._resolve_element_type(elem_0, elem_1)
        new_element = Element(
            1, mid_point[0], mid_point[1], new_element_type)
        # Id for the new element
        new_element.node_id = -(len(self.track_fusion) + 1)
        # Optimal internal structure
        optimize_internal_structure(elem_0, elem_1, self.distance_matrix)
        # Tracking elements
        new_element.nodes = [elem_0, elem_1]
        new_elements = set(self._elements)
        # Elements to remove
        fusioned = {elem_0, elem_1}
        self._elements = list(new_elements - fusioned)
        self._elements.append(new_element)
        # Heat wave from the fusion site
        self._propagate_fusion_heat(mid_point[0], mid_point[1], energy=0.30)
        return mid_point

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
