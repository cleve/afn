import math
import numpy

class Reader:
    def __init__(self, file_path, constants):
        self.file_path = file_path
        self.constants = constants
        self.start_parsing = False
        self.matrix = None
        self.coordinates = []

    def get_distance(self, p_0, p_1):
        """ p_0 is a tuple (x_0, y_0) and P_1 is a tuple (x_1, y_1)
        """
        distance = math.sqrt((p_1[0] - p_0[0])**2 + (p_1[1] - p_0[1])**2)
        if self.constants.INTEGER:
            return int(distance)
        return distance

    def extract_components(self, line):
        """Return node number, x_coord, y_coord
        """
        raw_values = line.split(' ')
        return (float(raw_values[0]), float(raw_values[1]), float(raw_values[2]))

    def build_distance_matrix(self):
        if len(self.coordinates) == 0:
            return None
        coord_len = len(self.coordinates)
        # Zero matrix.
        self.matrix = numpy.zeros((coord_len, coord_len), dtype=float)
        for ii in range(coord_len):
            for jj in range(coord_len):
                self.matrix[ii][jj] = self.get_distance(self.coordinates[ii], self.coordinates[jj])
        
        return self.matrix

    def read_tsp(self):
        if self.file_path is None:
            return self.matrix

        with open (self.file_path) as f:
            for line in f:
                if line.find('NODE_COORD_SECTION') == 0:
                    self.start_parsing = True
                    continue
                if not self.start_parsing:
                    continue
                numbers = self.extract_components(line)
                self.coordinates.append(
                    [numbers[1], numbers[2]]
                )
        
        return self.build_distance_matrix()
    