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
    def __init__(self, distance_matrix, constants):
        self.name = 'sun'
        self.track_fusion = []
        self.constants = constants
        self.utils = Utils()

        # Debug
        self.DEBUG = True

        # Geometry.
        self.distances = distance_matrix

        # Physics parameters.
        self.temperature_map = numpy.zeros(
            (len(self.distances), len(self.distances)),
            dtype=int
        )

    def build_temperature_map(self, current_length):
        region = self.constants.REGION
        # Can be split
        if current_length > region:
            zones = current_length // region
            if self.DEBUG:
                print('Using', region, 'regions of total of', current_length)
            for ii in range(zones):
                row_index_ii = ii+ii*region
                col_index_ii = ii+region*(ii+1)
                for jj in range(zones):
                    row_index_jj = jj+jj*region
                    col_index_jj = jj+region*(jj+1)
                    if row_index_jj > current_length:
                        row_index_jj = current_length
                    if col_index_jj > current_length:
                        col_index_jj = current_length
                    if row_index_ii > current_length:
                        row_index_ii = current_length
                    if col_index_ii > current_length:
                        col_index_ii = current_length
                    sub_matrix = self.distances[row_index_ii:col_index_ii + 1, row_index_jj:col_index_jj + 1]
                    average_distance = self.utils.matrix_avg(sub_matrix)
                    
                    self.temperature_map[row_index_ii:col_index_ii + 1, row_index_jj:col_index_jj + 1] = average_distance
                    if self.DEBUG:
                        print('Average value: ', average_distance)
                        print('For sub-matrix: ')
                        print(sub_matrix)

    def fusion(self, elem_0, elem_1):
        pass

    def ignition(self):
        candidates = []
        current_length = len(self.distances)
        # Initial temperature map
        self.build_temperature_map(current_length)
        # Start elements
        for ii in range(current_length):
            temp_prob = 0
            element_tuple = (0, 0)
            for jj in range(current_length):
                temperature = self.temperature_map[ii][jj]
                distance = self.distances[ii][jj]
                prob = temperature / distance if distance > 0 else 0
                if prob > temp_prob:
                    temp_prob = prob
                    element_tuple = (ii, jj)
            
            print(temp_prob, element_tuple)
                
