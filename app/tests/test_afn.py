import unittest

from afn import DEFAULT_TSP_FILE, ITERATIONS, parse_args


class TestAfnCli(unittest.TestCase):

    def test_parse_args_uses_defaults(self):
        args = parse_args([])

        self.assertEqual(args.tsp_file, DEFAULT_TSP_FILE)
        self.assertEqual(args.iterations, ITERATIONS)
        self.assertEqual(args.processes, 1)

    def test_parse_args_accepts_custom_values(self):
        args = parse_args(['samples/dj38.tsp', '--iterations', '50', '--processes', '4'])

        self.assertEqual(args.tsp_file, 'samples/dj38.tsp')
        self.assertEqual(args.iterations, 50)
        self.assertEqual(args.processes, 4)

    def test_parse_args_rejects_non_positive_iterations(self):
        with self.assertRaises(SystemExit):
            parse_args(['samples/dj38.tsp', '--iterations', '0'])

    def test_parse_args_rejects_non_positive_processes(self):
        with self.assertRaises(SystemExit):
            parse_args(['samples/dj38.tsp', '--processes', '0'])


if __name__ == '__main__':
    unittest.main()
