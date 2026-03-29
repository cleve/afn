from pathlib import Path
import unittest

from afn import DEFAULT_TSP_FILE, ITERATIONS, parse_args, _resolve_tsp_file_path, _build_fusion_weights


class TestAfnCli(unittest.TestCase):

    def test_parse_args_uses_defaults(self):
        args = parse_args([])

        self.assertEqual(args.tsp_file, DEFAULT_TSP_FILE)
        self.assertEqual(args.iterations, ITERATIONS)
        self.assertEqual(args.processes, 1)
        self.assertFalse(args.plot)
        self.assertEqual(args.plot_file, 'solution.png')
        self.assertFalse(args.progress)
        self.assertFalse(args.educative)
        self.assertEqual(args.educative_delay, 1.0)
        self.assertIsNone(args.educative_record)

    def test_parse_args_accepts_custom_values(self):
        args = parse_args([
            'samples/dj38.tsp',
            '--iterations', '50',
            '--processes', '4',
            '--plot',
            '--plot-file', 'dj38_solution.png',
            '--progress'
        ])

        self.assertEqual(args.tsp_file, 'samples/dj38.tsp')
        self.assertEqual(args.iterations, 50)
        self.assertEqual(args.processes, 4)
        self.assertTrue(args.plot)
        self.assertEqual(args.plot_file, 'dj38_solution.png')
        self.assertTrue(args.progress)

    def test_parse_args_educative_forces_single_iteration(self):
        args = parse_args([
            'samples/dj38.tsp',
            '--educative',
            '--iterations', '99',
            '--processes', '7',
            '--educative-delay', '1.5',
            '--educative-record', 'fusion.gif',
        ])

        self.assertTrue(args.educative)
        self.assertEqual(args.iterations, 1)
        self.assertEqual(args.processes, 1)
        self.assertEqual(args.educative_delay, 1.5)
        self.assertEqual(args.educative_record, 'fusion.gif')

    def test_parse_args_rejects_non_positive_iterations(self):
        with self.assertRaises(SystemExit):
            parse_args(['samples/dj38.tsp', '--iterations', '0'])

    def test_parse_args_rejects_non_positive_processes(self):
        with self.assertRaises(SystemExit):
            parse_args(['samples/dj38.tsp', '--processes', '0'])

    def test_parse_args_rejects_non_positive_educative_delay(self):
        with self.assertRaises(SystemExit):
            parse_args(['samples/dj38.tsp', '--educative', '--educative-delay', '0'])

    def test_parse_args_rejects_educative_record_without_educative_mode(self):
        with self.assertRaises(SystemExit):
            parse_args(['samples/dj38.tsp', '--educative-record', 'fusion.gif'])

    def test_parse_args_fusion_weights_default_none(self):
        args = parse_args([])

        self.assertIsNone(args.fusion_score_weight)
        self.assertIsNone(args.fusion_distance_weight)
        self.assertIsNone(args.fusion_barrier_weight)
        self.assertIsNone(args.fusion_gain_weight)

    def test_parse_args_accepts_fusion_weights(self):
        args = parse_args([
            '--fusion-score-weight', '0.6',
            '--fusion-distance-weight', '0.1',
            '--fusion-barrier-weight', '0.2',
            '--fusion-gain-weight', '0.1',
        ])

        self.assertAlmostEqual(args.fusion_score_weight, 0.6)
        self.assertAlmostEqual(args.fusion_distance_weight, 0.1)
        self.assertAlmostEqual(args.fusion_barrier_weight, 0.2)
        self.assertAlmostEqual(args.fusion_gain_weight, 0.1)

    def test_build_fusion_weights_returns_none_when_no_args(self):
        args = parse_args([])

        self.assertIsNone(_build_fusion_weights(args))

    def test_build_fusion_weights_returns_only_provided_keys(self):
        args = parse_args(['--fusion-score-weight', '0.7'])

        weights = _build_fusion_weights(args)
        self.assertIsNotNone(weights)
        self.assertEqual(weights, {'score': 0.7})

    def test_resolve_tsp_file_path_accepts_bare_sample_name(self):
        resolved = _resolve_tsp_file_path('dj38.tsp')

        self.assertTrue(Path(resolved).exists())
        self.assertEqual(Path(resolved).name, 'dj38.tsp')

    def test_resolve_tsp_file_path_accepts_samples_relative_path(self):
        resolved = _resolve_tsp_file_path('samples/dj38.tsp')

        self.assertTrue(Path(resolved).exists())
        self.assertEqual(Path(resolved).name, 'dj38.tsp')


if __name__ == '__main__':
    unittest.main()
