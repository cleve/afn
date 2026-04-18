import click
from concurrent.futures import ProcessPoolExecutor, as_completed
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import random
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


def _build_fusion_weights(
    fusion_score_weight=None,
    fusion_distance_weight=None,
    fusion_barrier_weight=None,
    fusion_gain_weight=None,
) -> dict | None:
    overrides = {}
    if fusion_score_weight is not None:
        overrides['score'] = fusion_score_weight
    if fusion_distance_weight is not None:
        overrides['distance'] = fusion_distance_weight
    if fusion_barrier_weight is not None:
        overrides['barrier'] = fusion_barrier_weight
    if fusion_gain_weight is not None:
        overrides['route_gain'] = fusion_gain_weight
    return overrides if overrides else None


def _is_hamiltonian_route(route: list[str], expected_nodes: set[str]) -> bool:
    if len(route) != len(expected_nodes):
        return False
    if len(set(route)) != len(route):
        return False
    return set(route) == expected_nodes


def _run_batch(batch_iterations: int, base_elements, distance_matrix, expected_nodes, fusion_weights: dict | None = None, massive: bool | None = None):
    best_length = inf
    best_route = []

    for _ in range(batch_iterations):
        use_massive = massive if massive is not None else random.random() < 0.30
        star = Star(base_elements, distance_matrix, fusion_weights=fusion_weights, massive=use_massive)
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


_W = 68  # visual width for horizontal rules


def _hr(color: str = 'bright_black') -> str:
    return click.style('  ' + '─' * _W, fg=color)


def _print_banner():
    click.echo()
    click.echo(
        click.style('  ✦  AFN', fg='bright_yellow', bold=True)
        + click.style('  ·  Artificial Fusion Navigator', dim=True)
    )
    click.echo(_hr('yellow'))
    click.echo()


def _print_section(title: str):
    click.echo()
    click.echo(click.style(f'  {title}', fg='cyan', bold=True))
    click.echo(click.style('  ' + '─' * 32, fg='cyan', dim=True))


def _print_row(key: str, value: str, highlight: bool = False, key_width: int = 18):
    styled_key = click.style(f'  {key:<{key_width}}', dim=True)
    styled_val = click.style(value, fg='bright_white', bold=highlight)
    click.echo(styled_key + styled_val)


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


def solve_tsp(tsp_file: str, iterations: int, processes: int = 1, show_progress: bool = False, fusion_weights: dict | None = None, massive: bool | None = None):
    resolved_tsp_file = _resolve_tsp_file_path(tsp_file)
    reader = Reader(resolved_tsp_file)
    base_elements = reader.read_tsp()
    distance_matrix = reader.build_distance_matrix()
    if distance_matrix is None:
        raise ValueError('TSP file does not contain coordinates.')
    expected_nodes = {str(int(item[0])) for item in base_elements}

    best_length = inf
    best_route = []

    bar_args = dict(
        length=iterations,
        label=click.style('  Simulating', fg='cyan'),
        bar_template='%(label)s  %(bar)s  %(info)s',
        fill_char=click.style('█', fg='yellow'),
        empty_char=click.style('░', fg='bright_black', dim=True),
        color=True,
        show_eta=True,
        show_pos=True,
    )

    if processes == 1:
        with click.progressbar(**bar_args) as bar:
            for _ in range(iterations):
                route, length = _run_batch(1, base_elements, distance_matrix, expected_nodes, fusion_weights=fusion_weights, massive=massive)
                if route and length < best_length:
                    best_length = length
                    best_route = route
                if show_progress:
                    bar.update(1)
    else:
        chunks = _progress_chunks(iterations, processes)
        with click.progressbar(**bar_args) as bar:
            with ProcessPoolExecutor(max_workers=processes) as executor:
                futures = {
                    executor.submit(_run_batch, chunk, base_elements, distance_matrix, expected_nodes, fusion_weights, massive): chunk
                    for chunk in chunks
                }

                for future in as_completed(futures):
                    route, length = future.result()
                    if route and length < best_length:
                        best_length = length
                        best_route = route
                    if show_progress:
                        bar.update(futures[future])

    if not best_route:
        raise RuntimeError('No route was generated by the simulation.')
    if not _is_hamiltonian_route(best_route, expected_nodes):
        raise RuntimeError('Generated route is not a valid Hamiltonian cycle.')

    verified_length = tour_length(best_route, distance_matrix, close_loop=True)
    return best_route, int(verified_length), base_elements


def solve_tsp_educative(tsp_file: str, fusion_weights: dict | None = None, massive: bool = False):
    resolved_tsp_file = _resolve_tsp_file_path(tsp_file)
    reader = Reader(resolved_tsp_file)
    base_elements = reader.read_tsp()
    distance_matrix = reader.build_distance_matrix()
    if distance_matrix is None:
        raise ValueError('TSP file does not contain coordinates.')
    expected_nodes = {str(int(item[0])) for item in base_elements}

    star = Star(base_elements, distance_matrix, fusion_weights=fusion_weights, massive=massive)
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
    arrow = click.style(' → ', fg='bright_black')
    chunks = []
    for index in range(0, len(route), chunk_size):
        nodes = [click.style(n, fg='bright_white') for n in route[index:index + chunk_size]]
        chunks.append('  ' + arrow.join(nodes))
    return '\n'.join(chunks)


def _print_result(tsp_file: str, iterations: int, processes: int, best_length: int, elapsed: float, best_route: list[str], plot_file: str | None = None):
    _print_banner()
    _print_section('Configuration')
    _print_row('Input file', tsp_file)
    _print_row('Iterations', f'{iterations:,}')
    _print_row('Processes', str(processes))
    _print_section('Result')
    _print_row('Tour length', f'{best_length:,}', highlight=True)
    _print_row('Elapsed', f'{elapsed:.3f} s')
    if plot_file is not None:
        _print_row('Plot', plot_file)
    _print_section('Route')
    click.echo(_format_route(best_route))
    click.echo()
    click.echo(_hr('yellow'))
    click.echo()


def _print_educative_result(tsp_file: str, best_length: int, elapsed: float, best_route: list[str], fusion_events_count: int, record_file: str | None = None):
    _print_banner()
    _print_section('Configuration')
    _print_row('Input file', tsp_file)
    _print_row('Mode', 'educative  (1 iteration · 1 process)')
    _print_section('Result')
    _print_row('Tour length', f'{best_length:,}', highlight=True)
    _print_row('Fusion events', str(fusion_events_count))
    _print_row('Elapsed', f'{elapsed:.3f} s')
    if record_file:
        _print_row('Animation', record_file)
    _print_section('Route')
    click.echo(_format_route(best_route))
    click.echo()
    click.echo(_hr('yellow'))
    click.echo()


@click.command()
@click.version_option(__version__, prog_name='afn')
@click.argument('tsp_file', default=DEFAULT_TSP_FILE, required=False)
@click.option('-i', '--iterations', default=ITERATIONS, show_default=True, type=click.IntRange(min=1), help='Number of star simulation runs.')
@click.option('-p', '--processes', default=1, show_default=True, type=click.IntRange(min=1), help='Number of worker processes for simulation batches.')
@click.option('--plot', is_flag=True, help='Generate a PNG plot with the proposed TSP cycle.')
@click.option('--plot-file', default='solution.png', show_default=True, help='Output image path when --plot is enabled.')
@click.option('--progress', is_flag=True, help='Show a progress bar with completion percentage.')
@click.option('--educative', is_flag=True, help='Run educational mode with a live fusion animation (forces one iteration and one process).')
@click.option('--educative-delay', default=1.0, show_default=True, type=click.FloatRange(min=0, min_open=True), help='Seconds between educational animation frames.')
@click.option('--educative-record', default=None, help='Optional animation output file (.gif or .mp4) in educational mode.')
@click.option('--massive', is_flag=True, help='Force every star to use massive mode (shorter life, smaller neighbourhood, faster iterations).')
@click.option('--fusion-score-weight', default=None, type=float, help='Weight for the score term in the fusion probability formula (default: 0.50).')
@click.option('--fusion-distance-weight', default=None, type=float, help='Weight for the distance term in the fusion probability formula (default: 0.20).')
@click.option('--fusion-barrier-weight', default=None, type=float, help='Weight for the barrier term in the fusion probability formula (default: 0.20).')
@click.option('--fusion-gain-weight', default=None, type=float, help='Weight for the route-gain term in the fusion probability formula (default: 0.10).')
def main(
    tsp_file, iterations, processes, plot, plot_file, progress,
    educative, educative_delay, educative_record, massive,
    fusion_score_weight, fusion_distance_weight, fusion_barrier_weight, fusion_gain_weight,
):
    """Solve a TSP instance with the AFN star-fusion heuristic."""
    if educative_record and not educative:
        raise click.UsageError('--educative-record requires --educative')

    fusion_weights = _build_fusion_weights(
        fusion_score_weight, fusion_distance_weight,
        fusion_barrier_weight, fusion_gain_weight,
    )

    start_time = perf_counter()

    if educative:
        best_route, best_length, base_elements, fusion_events = solve_tsp_educative(
            tsp_file,
            fusion_weights=fusion_weights,
            massive=massive,
        )
        recorded_file = animate_fusion_process(
            base_elements,
            fusion_events,
            delay_seconds=educative_delay,
            record_file=educative_record,
        )
        elapsed = perf_counter() - start_time
        _print_educative_result(
            tsp_file,
            best_length,
            elapsed,
            best_route,
            len(fusion_events),
            recorded_file,
        )
        return

    best_route, best_length, base_elements = solve_tsp(
        tsp_file,
        iterations,
        processes,
        show_progress=progress,
        fusion_weights=fusion_weights,
        massive=True if massive else None,
    )
    elapsed = perf_counter() - start_time
    plot_path = None
    if plot:
        plot_tsp_solution(base_elements, best_route, plot_file, close_loop=True)
        plot_path = plot_file

    _print_result(tsp_file, iterations, processes, best_length, elapsed, best_route, plot_path)


if __name__ == "__main__":
    main()
