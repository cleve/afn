import argparse
from utils.stream import Reader
from core.star import Star
from core.route import build_best_route, tour_length, two_opt
from math import inf


ITERATIONS = 500
DEFAULT_TSP_FILE = 'samples/dj38.tsp'


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='Solve a TSP instance with the AFN star-fusion heuristic.'
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

    args = parser.parse_args(argv)
    if args.iterations < 1:
        parser.error('iterations must be greater than 0')
    return args


def solve_tsp(tsp_file: str, iterations: int):
    reader = Reader(tsp_file)
    base_elements = reader.read_tsp()
    distance_matrix = reader.build_distance_matrix()
    best_length = inf
    best_route = None

    for _ in range(iterations):
        star = Star(base_elements, distance_matrix)
        star.life()
        route = build_best_route(star.elements, distance_matrix)
        route = two_opt(route, distance_matrix)
        current_length = tour_length(route, distance_matrix)
        if current_length < best_length:
            best_length = current_length
            best_route = route

    return best_route, int(best_length)


def main(argv=None):
    args = parse_args(argv)
    best_route, best_length = solve_tsp(args.tsp_file, args.iterations)

    print(' > '.join(best_route), ':', best_length)


if __name__ == "__main__":
    main()
