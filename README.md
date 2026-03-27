# AFN

AFN is a heuristic approach to solve the Traveling Salesman Problem (TSP)
using a simulation inspired by nuclear fusion inside a star.

## DJ38 - Djibouti Computation Log

- Instance Created: July 29, 2001; duplicate cities removed April 20, 2009
- Number of Cities: 38
- Optimal Value: 6656
- Solved: July 30, 2001
- Solution Method: concorde (default settings), QSopt LP solver
- Solution Time: 0.24 seconds, AMD Athlon 1.33 GHz

## Fusion model

The star simulation uses an energy-driven fusion process instead of pure random
pair selection.

At each cycle, the algorithm:

1. Builds all candidate element pairs.
2. Scores each pair using:
	- Spatial closeness (shorter distance is better)
	- Route gain proxy from leaf-node structure
	- Fusion barrier by element type (H-H easier than He-He/C-C)
	- Star state boost (temperature, density, pressure)
3. Samples a pair with weighted probability from the score distribution.
4. Converts the selected score into a fusion probability with a sigmoid.
5. Updates core temperature, density, and pressure after success/failure.

If no fusion is accepted for several cycles, the star triggers a deterministic
collapse step and fuses the best-scored pair to avoid stagnation.

After star life ends, the route is improved with a local 2-opt pass.

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