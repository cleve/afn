from utils.helper import Helper


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

    def build_distance_matrix(self):
        if len(self.coordinates) == 0:
            return None
        coord_len = len(self.coordinates)
        # Zero matrix.
        self.matrix = [ [ 0 for i in range(coord_len) ] for j in range(coord_len) ]
        for ii in range(coord_len):
            for jj in range(coord_len):
                self.matrix[ii][jj] = Helper.get_distance(
                    self.coordinates[ii], self.coordinates[jj])

        return self.matrix

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
                self.coordinates.append(
                    [numbers[1], numbers[2]]
                )
                coordinates.append(
                    [numbers[0], numbers[1], numbers[2]]
                )

        return coordinates
