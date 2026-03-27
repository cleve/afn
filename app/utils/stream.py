from utils.geometry import euclidean_distance


class Reader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.start_parsing = False
        self.matrix = None
        self.coordinates = []

    def _extract_components(self, line):
        """Return node number, x_coord, y_coord
        """
        raw_values = line.split()
        return (float(raw_values[0]), float(raw_values[1]), float(raw_values[2]))

    def build_distance_matrix(self):
        if len(self.coordinates) == 0:
            return None
        coord_len = len(self.coordinates)
        # Zero matrix.
        self.matrix = [[0 for _ in range(coord_len)] for _ in range(coord_len)]
        for ii in range(coord_len):
            for jj in range(ii, coord_len):
                distance = euclidean_distance(self.coordinates[ii], self.coordinates[jj])
                self.matrix[ii][jj] = distance
                self.matrix[jj][ii] = distance

        return self.matrix

    def read_tsp(self):
        '''Get coordinates
        return [node_number, x, y]
        '''
        if self.file_path is None:
            raise FileNotFoundError('File not found')
        coordinates = []
        with open(self.file_path) as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line == 'NODE_COORD_SECTION':
                    self.start_parsing = True
                    continue
                if stripped_line == 'EOF':
                    break
                if not self.start_parsing:
                    continue
                if not stripped_line:
                    continue
                numbers = self._extract_components(stripped_line)
                self.coordinates.append(
                    (numbers[1], numbers[2])
                )
                coordinates.append(
                    (numbers[0], numbers[1], numbers[2])
                )

        return coordinates
