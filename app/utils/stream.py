import math
import numpy


class Reader:
    def __init__(self, file_path, constants):
        self.file_path = file_path
        self.constants = constants
        self.start_parsing = False
        self.matrix = None
        self.coordinates = []

    def extract_components(self, line):
        """Return node number, x_coord, y_coord
        """
        raw_values = line.split(' ')
        return (float(raw_values[0]), float(raw_values[1]), float(raw_values[2]))

    def read_tsp(self):
        '''Get coordinates
        return [node_number, x, y]
        '''
        if self.file_path is None:
            raise ('File not found')
        coordinates = []
        with open(self.file_path) as f:
            for line in f:
                if line.find('NODE_COORD_SECTION') == 0:
                    self.start_parsing = True
                    continue
                if not self.start_parsing:
                    continue
                numbers = self.extract_components(line)
                coordinates.append(
                    [numbers[0], numbers[1], numbers[2]]
                )

        return coordinates
