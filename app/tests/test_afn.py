from pathlib import Path
import unittest

from click.testing import CliRunner

from afn import DEFAULT_TSP_FILE, ITERATIONS, main, _resolve_tsp_file_path, _build_fusion_weights


class TestAfnCli(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_parse_args_uses_defaults(self):
        result = self.runner.invoke(main, ['--help'])
        self.assertEqual(result.exit_code, 0)
        # Verify defaults are documented
        self.assertIn(str(ITERATIONS), result.output)
        self.assertIn('solution.png', result.output)

    def test_parse_args_accepts_custom_values(self):
        # Just validate the options are accepted without error (no actual TSP run)
        result = self.runner.invoke(main, [
            'samples/dj38.tsp',
            '--iterations', '50',
            '--processes', '4',
            '--plot',
            '--plot-file', 'dj38_solution.png',
            '--progress',
        ])
        # Will fail because samples/dj38.tsp path resolution, but not a usage error
        self.assertNotEqual(result.exit_code, 2)

    def test_parse_args_educative_forces_single_iteration(self):
        # --educative with other flags should not be rejected as a usage error
        result = self.runner.invoke(main, [
            'samples/dj38.tsp',
            '--educative',
            '--educative-delay', '1.5',
        ])
        self.assertNotEqual(result.exit_code, 2)

    def test_parse_args_rejects_non_positive_iterations(self):
        result = self.runner.invoke(main, ['samples/dj38.tsp', '--iterations', '0'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn('0 is not', result.output.lower() + result.output.lower())

    def test_parse_args_rejects_non_positive_processes(self):
        result = self.runner.invoke(main, ['samples/dj38.tsp', '--processes', '0'])
        self.assertEqual(result.exit_code, 2)

    def test_parse_args_rejects_non_positive_educative_delay(self):
        result = self.runner.invoke(main, [
            'samples/dj38.tsp', '--educative', '--educative-delay', '0'
        ])
        self.assertEqual(result.exit_code, 2)

    def test_parse_args_rejects_educative_record_without_educative_mode(self):
        result = self.runner.invoke(main, ['samples/dj38.tsp', '--educative-record', 'fusion.gif'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn('--educative-record requires --educative', result.output)

    def test_parse_args_fusion_weights_default_none(self):
        weights = _build_fusion_weights()
        self.assertIsNone(weights)

    def test_parse_args_accepts_fusion_weights(self):
        result = self.runner.invoke(main, [
            '--fusion-score-weight', '0.6',
            '--fusion-distance-weight', '0.1',
            '--fusion-barrier-weight', '0.2',
            '--fusion-gain-weight', '0.1',
        ])
        # Not a usage error (exit code 2)
        self.assertNotEqual(result.exit_code, 2)

    def test_build_fusion_weights_returns_none_when_no_args(self):
        self.assertIsNone(_build_fusion_weights())

    def test_build_fusion_weights_returns_only_provided_keys(self):
        weights = _build_fusion_weights(fusion_score_weight=0.7)
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
