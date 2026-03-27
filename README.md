# AFN

AFN is a heuristic approach to solve the Traveling Salesman Problem (TSP)
using a simulation inspired by nuclear fusion inside a star.

## Run

From the project root:

```sh
cd app
python3 afn.py [tsp_file] [-i ITERATIONS]
```

## CLI arguments

- `tsp_file`: optional positional argument. Path to a TSPLIB `.tsp` file.
	- Default: `samples/dj38.tsp`
- `-i`, `--iterations`: optional number of simulation runs.
	- Default: `500`
	- Must be greater than `0`

## Examples

Run with defaults:

```sh
cd app
python3 afn.py
```

Run with a custom iteration count:

```sh
cd app
python3 afn.py --iterations 100
```

Run with an explicit TSP file and short iteration flag:

```sh
cd app
python3 afn.py samples/dj38.tsp -i 250
```

The program prints the best route found and its total tour length.