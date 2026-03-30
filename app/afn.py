import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import random
import sys
from time import perf_counter

try:
    __version__ = version('afn')
except PackageNotFoundError:
    __version__ = 'unknown'

from utils.stream import Reader
from utils.plotter import plot_tsp_solution, animate_fusion_process
from core.star import Star
from core.route import build_best_route, tour_length, two_opt
from math import inf


ITERATIONS = 500
DEFAULT_TSP_FILE = 'samples/dj38.tsp'
APP_ROOT = Path(__file__).resolve().parent


def _resolve_tsp_file_path(tsp_file: str) -> str:
    candidate = Path(tsp_file)
    if candidate.exists():
        return str(candidate)

    search_candidates = [
        APP_ROOT / candidate,
        APP_ROOT / 'samples' / candidate.name,
    ]

    for item in search_candidates:
        if item.exists():
            return str(item)

    return tsp_file


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='Solve a TSP instance with the AFN star-fusion heuristic.'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )
    parser.add_argument(
        'tsp_file',
        nargs='?',
        default=DEFAULT_TSP_FILE,
        help='Path to a TSPLIB .tsp file (default: %(default)s).'
    )
    parser.add_argument(
        '-i',
        '--iterations',
        type=int,
        default=ITERATIONS,
        help='Number of star simulation runs (default: %(default)s).'
    )
    parser.add_argument(
        '-p',
        '--processes',
        type=int,
        default=1,
        help='Number of worker processes for simulation batches (default: %(default)s).'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate a PNG plot with the proposed TSP cycle.'
    )
    parser.add_argument(
        '--plot-file',
        default='solution.png',
        help='Output image path when --plot is enabled (default: %(default)s).'
    )
    parser.add_argument(
        '--progress',
        action='store_true',
        help='Show a progress bar with completion percentage.'
    )
    parser.add_argument(
        '--educative',
        action='store_true',
        help='Run educational mode with a live fusion animation (forces one iteration and one process).'
    )
    parser.add_argument(
        '--educative-delay',
        type=float,
        default=1.0,
        help='Seconds between educational animation frames (default: %(default)s).'
    )
    parser.add_argument(
        '--educative-record',
        default=None,
        help='Optional animation output file (.gif or .mp4) in educational mode.'
    )
    parser.add_argument(
        '--fusion-score-weight',
        type=float,
        default=None,
        help='Weight for the score term in the fusion probability formula (default: 0.50).'
    )
    parser.add_argument(
        '--fusion-distance-weight',
        type=float,
        default=None,
        help='Weight for the distance term in the fusion probability formula (default: 0.20).'
    )
    parser.add_argument(
        '--fusion-barrier-weight',
        type=float,
        default=None,
        help='Weight for the barrier term in the fusion probability formula (default: 0.20).'
    )
    parser.add_argument(
        '--fusion-gain-weight',
        type=float,
        default=None,
        help='Weight for the route-gain term in the fusion probability formula (default: 0.10).'
    )

    args = parser.parse_args(argv)
    if args.iterations < 1:
        parser.error('iterations must be greater than 0')
    if args.processes < 1:
        parser.error('processes must be greater than 0')
    if args.educative_delay <= 0:
        parser.error('educative-delay must be greater than 0')
    if args.educative_record and not args.educative:
        parser.error('educative-record requires --educative')
    if args.educative:
        args.iterations = 1
        args.processes = 1
    return args


def _build_fusion_weights(args) -> dict | None:
    overrides = {}
    if args.fusion_score_weight is not None:
        overrides['score'] = args.fusion_score_weight
    if args.fusion_distance_weight is not None:
        overrides['distance'] = args.fusion_distance_weight
    if args.fusion_barrier_weight is not None:
        overrides['barrier'] = args.fusion_barrier_weight
    if args.fusion_gain_weight is not None:
        overrides['route_gain'] = args.fusion_gain_weight
    return overrides if overrides else None


def _is_hamiltonian_route(route: list[str], expected_nodes: set[str]) -> bool:
    if len(route) != len(expected_nodes):
        return False
    if len(set(route)) != len(route):
        return False
    return set(route) == expected_nodes


def _run_batch(batch_iterations: int, base_elements, distance_matrix, expected_nodes, fusion_weights: dict | None = None):
    best_length = inf
    best_route = []

    for _ in range(batch_iterations):
        massive = random.random() < 0.30  # ~30 % of stars are massive (shorter life, smaller neighbourhood)
        star = Star(base_elements, distance_matrix, fusion_weights=fusion_weights, massive=massive)
        star.life()
        route = build_best_route(star.elements, distance_matrix)
        if not _is_hamiltonian_route(route, expected_nodes):
            continue
        route = two_opt(route, distance_matrix)
        if not _is_hamiltonian_route(route, expected_nodes):
            continue
        current_length = tour_length(route, distance_matrix)
        if current_length < best_length:
            best_length = current_length
            best_route = route

    return best_route, best_length


def _print_progress(completed: int, total: int, prefix: str = 'Progress', width: int = 30):
    if total <= 0:
        return

    ratio = completed / total
    filled = int(width * ratio)
    bar = '#' * filled + '-' * (width - filled)
    percent = ratio * 100
    sys.stdout.write(f'\r{prefix} [{bar}] {percent:6.2f}% ({completed}/{total})')
    sys.stdout.flush()

    if completed >= total:
        sys.stdout.write('\n')
        sys.stdout.flush()


def _split_iterations(total_iterations: int, workers: int):
    effective_workers = min(total_iterations, workers)
    base = total_iterations // effective_workers
    remainder = total_iterations % effective_workers

    chunks = []
    for index in range(effective_workers):
        chunk_size = base + (1 if index < remainder else 0)
        chunks.append(chunk_size)
    return chunks


def _progress_chunks(total_iterations: int, workers: int):
    """Create smaller chunks so progress can update frequently in process mode."""
    if total_iterations <= 0:
        return []

    # Aim for multiple updates per worker while keeping process overhead reasonable.
    target_chunks = max(workers * 8, workers)
    chunk_size = max(1, total_iterations // target_chunks)

    chunks = []
    remaining = total_iterations
    while remaining > 0:
        current = min(chunk_size, remaining)
        chunks.append(current)
        remaining -= current
    return chunks


def solve_tsp(tsp_file: str, iterations: int, processes: int = 1, show_progress: bool = False, fusion_weights: dict | None = None):
    resolved_tsp_file = _resolve_tsp_file_path(tsp_file)
    reader = Reader(resolved_tsp_file)
    base_elements = reader.read_tsp()
    distance_matrix = reader.build_distance_matrix()
    if distance_matrix is None:
        raise ValueError('TSP file does not contain coordinates.')
    expected_nodes = {str(int(item[0])) for item in base_elements}

    best_length = inf
    best_route = []

    if processes == 1:
        for step in range(iterations):
            route, length = _run_batch(1, base_elements, distance_matrix, expected_nodes, fusion_weights=fusion_weights)
            if route and length < best_length:
                best_length = length
                best_route = route
            if show_progress:
                _print_progress(step + 1, iterations)
    else:
        chunks = _progress_chunks(iterations, processes)
        completed = 0
        with ProcessPoolExecutor(max_workers=processes) as executor:
            futures = {
                executor.submit(_run_batch, chunk, base_elements, distance_matrix, expected_nodes, fusion_weights): chunk
                for chunk in chunks
            }

            for future in as_completed(futures):
                route, length = future.result()
                if route and length < best_length:
                    best_length = length
                    best_route = route
                if show_progress:
                    completed += futures[future]
                    _print_progress(completed, iterations)

    if not best_route:
        raise RuntimeError('No route was generated by the simulation.')
    if not _is_hamiltonian_route(best_route, expected_nodes):
        raise RuntimeError('Generated route is not a valid Hamiltonian cycle.')

    verified_length = tour_length(best_route, distance_matrix, close_loop=True)
    return best_route, int(verified_length), base_elements


def solve_tsp_educative(tsp_file: str, fusion_weights: dict | None = None):
    resolved_tsp_file = _resolve_tsp_file_path(tsp_file)
    reader = Reader(resolved_tsp_file)
    base_elements = reader.read_tsp()
    distance_matrix = reader.build_distance_matrix()
    if distance_matrix is None:
        raise ValueError('TSP file does not contain coordinates.')
    expected_nodes = {str(int(item[0])) for item in base_elements}

    star = Star(base_elements, distance_matrix, fusion_weights=fusion_weights)
    star.life()

    route = build_best_route(star.elements, distance_matrix)
    if not _is_hamiltonian_route(route, expected_nodes):
        raise RuntimeError('Generated route is not a valid Hamiltonian cycle.')

    route = two_opt(route, distance_matrix)
    if not _is_hamiltonian_route(route, expected_nodes):
        raise RuntimeError('Generated route is not a valid Hamiltonian cycle.')

    best_length = int(tour_length(route, distance_matrix, close_loop=True))
    return route, best_length, base_elements, star.fusion_events


def _format_route(route: list[str], chunk_size: int = 8) -> str:
    chunks = []
    for index in range(0, len(route), chunk_size):
        chunks.append(' > '.join(route[index:index + chunk_size]))
    return '\n'.join(chunks)


def _print_result(tsp_file: str, iterations: int, processes: int, best_length: int, elapsed: float, best_route: list[str], plot_file: str | None = None):
    separator = '=' * 72
    print(separator)
    print('AFN TSP RESULT')
    print(separator)
    print()
    print('Run configuration')
    print(f'  Input file : {tsp_file}')
    print(f'  Iterations : {iterations}')
    print(f'  Processes  : {processes}')
    print()
    print('Outcome')
    print(f'  Best length : {best_length}')
    print(f'  Elapsed     : {elapsed:.3f}s')
    if plot_file is not None:
        print(f'  Plot file   : {plot_file}')
    print()
    print('Best route')
    print(_format_route(best_route))
    print()
    print(separator)


def _print_educative_result(tsp_file: str, best_length: int, elapsed: float, best_route: list[str], fusion_events_count: int, record_file: str | None = None):
    separator = '=' * 72
    print(separator)
    print('AFN EDUCATIVE RESULT')
    print(separator)
    print()
    print('Run configuration')
    print(f'  Input file         : {tsp_file}')
    print('  Iterations         : 1 (forced by educative mode)')
    print('  Processes          : 1 (forced by educative mode)')
    print()
    print('Outcome')
    print(f'  Best length        : {best_length}')
    print(f'  Fusion events      : {fusion_events_count}')
    print(f'  Elapsed            : {elapsed:.3f}s')
    if record_file:
        print(f'  Animation recording: {record_file}')
    print()
    print('Best route')
    print(_format_route(best_route))
    print()
    print(separator)


def main(argv=None):
    args = parse_args(argv)
    start_time = perf_counter()

    if args.educative:
        best_route, best_length, base_elements, fusion_events = solve_tsp_educative(
            args.tsp_file,
            fusion_weights=_build_fusion_weights(args),
        )
        recorded_file = animate_fusion_process(
            base_elements,
            fusion_events,
            delay_seconds=args.educative_delay,
            record_file=args.educative_record,
        )
        elapsed = perf_counter() - start_time
        _print_educative_result(
            args.tsp_file,
            best_length,
            elapsed,
            best_route,
            len(fusion_events),
            recorded_file,
        )
        return

    best_route, best_length, base_elements = solve_tsp(
        args.tsp_file,
        args.iterations,
        args.processes,
        show_progress=args.progress,
        fusion_weights=_build_fusion_weights(args),
    )
    elapsed = perf_counter() - start_time
    plot_path = None
    if args.plot:
        plot_tsp_solution(base_elements, best_route, args.plot_file, close_loop=True)
        plot_path = args.plot_file

    _print_result(args.tsp_file, args.iterations, args.processes, best_length, elapsed, best_route, plot_path)


if __name__ == "__main__":
    main()
