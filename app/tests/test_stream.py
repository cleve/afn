import os
import tempfile
import unittest

from utils.stream import Reader


def _write_tsp(content: str) -> str:
    """Write content to a temp file and return its path."""
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.tsp') as handle:
        handle.write(content)
        return handle.name


class TestReader(unittest.TestCase):

    def test_read_tsp_handles_whitespace_and_eof(self):
        file_path = _write_tsp(
            'NAME: sample\n'
            'TYPE: TSP\n'
            'NODE_COORD_SECTION\n'
            '1   0   0\n'
            '2  3  4\n'
            'EOF\n'
        )
        try:
            reader = Reader(file_path)
            coordinates = reader.read_tsp()
            distance_matrix = reader.build_distance_matrix()

            self.assertEqual(coordinates, [(1.0, 0.0, 0.0), (2.0, 3.0, 4.0)])
            self.assertEqual(distance_matrix[0][1], 5.0)
            self.assertEqual(distance_matrix[1][0], 5.0)
        finally:
            os.unlink(file_path)

    def test_read_tsp_without_eof_sentinel(self):
        """File that ends without an EOF line should still parse correctly."""
        file_path = _write_tsp(
            'NAME: no_eof\n'
            'NODE_COORD_SECTION\n'
            '1  0  0\n'
            '2  1  0\n'
        )
        try:
            reader = Reader(file_path)
            coordinates = reader.read_tsp()
            self.assertEqual(len(coordinates), 2)
            self.assertEqual(coordinates[0], (1.0, 0.0, 0.0))
            self.assertEqual(coordinates[1], (2.0, 1.0, 0.0))
        finally:
            os.unlink(file_path)

    def test_read_tsp_skips_blank_lines_in_section(self):
        """Blank lines inside NODE_COORD_SECTION must be ignored."""
        file_path = _write_tsp(
            'NODE_COORD_SECTION\n'
            '\n'
            '1  0  0\n'
            '\n'
            '2  3  4\n'
            'EOF\n'
        )
        try:
            reader = Reader(file_path)
            coordinates = reader.read_tsp()
            self.assertEqual(len(coordinates), 2)
        finally:
            os.unlink(file_path)

    def test_read_tsp_preserves_decimal_coordinates(self):
        """Floating-point coordinates must be read without truncation."""
        file_path = _write_tsp(
            'NODE_COORD_SECTION\n'
            '1  11003.6111  42102.5000\n'
            '2  11108.6111  42373.8889\n'
            'EOF\n'
        )
        try:
            reader = Reader(file_path)
            coordinates = reader.read_tsp()
            self.assertAlmostEqual(coordinates[0][1], 11003.6111, places=3)
            self.assertAlmostEqual(coordinates[0][2], 42102.5000, places=3)
            self.assertAlmostEqual(coordinates[1][1], 11108.6111, places=3)
        finally:
            os.unlink(file_path)

    def test_read_tsp_node_ids_are_sequential(self):
        """Node IDs (first column) must be parsed as the first tuple element."""
        file_path = _write_tsp(
            'NODE_COORD_SECTION\n'
            '5  10  20\n'
            '7  30  40\n'
            'EOF\n'
        )
        try:
            reader = Reader(file_path)
            coordinates = reader.read_tsp()
            self.assertEqual(coordinates[0][0], 5.0)
            self.assertEqual(coordinates[1][0], 7.0)
        finally:
            os.unlink(file_path)

    def test_read_tsp_ignores_header_lines(self):
        """Lines before NODE_COORD_SECTION must not be parsed as nodes."""
        file_path = _write_tsp(
            'NAME: test\n'
            'COMMENT: some comment\n'
            'DIMENSION: 2\n'
            'EDGE_WEIGHT_TYPE: EUC_2D\n'
            'NODE_COORD_SECTION\n'
            '1  0  0\n'
            '2  1  1\n'
            'EOF\n'
        )
        try:
            reader = Reader(file_path)
            coordinates = reader.read_tsp()
            self.assertEqual(len(coordinates), 2)
        finally:
            os.unlink(file_path)

    def test_build_distance_matrix_diagonal_is_zero(self):
        """Every node must have zero distance to itself."""
        file_path = _write_tsp(
            'NODE_COORD_SECTION\n'
            '1  0  0\n'
            '2  3  4\n'
            '3  6  8\n'
            'EOF\n'
        )
        try:
            reader = Reader(file_path)
            reader.read_tsp()
            matrix = reader.build_distance_matrix()
            for i in range(3):
                self.assertEqual(matrix[i][i], 0)
        finally:
            os.unlink(file_path)

    def test_build_distance_matrix_is_symmetric(self):
        """Distance from A to B must equal distance from B to A."""
        file_path = _write_tsp(
            'NODE_COORD_SECTION\n'
            '1  0  0\n'
            '2  3  4\n'
            '3  6  0\n'
            'EOF\n'
        )
        try:
            reader = Reader(file_path)
            reader.read_tsp()
            matrix = reader.build_distance_matrix()
            n = len(matrix)
            for i in range(n):
                for j in range(n):
                    self.assertAlmostEqual(matrix[i][j], matrix[j][i])
        finally:
            os.unlink(file_path)

    def test_build_distance_matrix_returns_none_when_empty(self):
        """build_distance_matrix must return None if no coordinates were parsed."""
        reader = Reader('unused_path')
        self.assertIsNone(reader.build_distance_matrix())

    def test_read_tsp_raises_when_file_path_is_none(self):
        """Reader must raise FileNotFoundError when file_path is None."""
        reader = Reader(None)
        with self.assertRaises(FileNotFoundError):
            reader.read_tsp()


if __name__ == '__main__':
    unittest.main()