import os
import tempfile
import unittest

from utils.stream import Reader


class TestReader(unittest.TestCase):

    def test_read_tsp_handles_whitespace_and_eof(self):
        with tempfile.NamedTemporaryFile('w', delete=False) as handle:
            handle.write(
                'NAME: sample\n'
                'TYPE: TSP\n'
                'NODE_COORD_SECTION\n'
                '1   0   0\n'
                '2  3  4\n'
                'EOF\n'
            )
            file_path = handle.name

        try:
            reader = Reader(file_path)
            coordinates = reader.read_tsp()
            distance_matrix = reader.build_distance_matrix()

            self.assertEqual(coordinates, [(1.0, 0.0, 0.0), (2.0, 3.0, 4.0)])
            self.assertEqual(distance_matrix[0][1], 5.0)
            self.assertEqual(distance_matrix[1][0], 5.0)
        finally:
            os.unlink(file_path)


if __name__ == '__main__':
    unittest.main()