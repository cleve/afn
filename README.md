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

## Star mass

Each star simulation is independently assigned a **mass class** that controls
the trade-off between speed and exploration depth.

| Property | Massive star (~30 % of runs) | Non-massive star (~70 % of runs) |
|---|---|---|
| Life length | Shorter (`max(5, n)` idle cycles) | Longer (`max(10, 2n)` idle cycles) |
| Fusion neighbourhood | Nearest 25 % of elements | Nearest 60 % of elements |
| Candidate pairs per step | Small, focused | Wide, exploratory |
| Speed | Faster iterations | Slower iterations |

**Neighbourhood selection** avoids evaluating all O(n²) element pairs on every
step. Instead, each element considers only its K nearest neighbours (by
euclidean coordinate distance), reducing the per-step cost to O(n·K). When K
reaches n − 1 (small instances), it falls back automatically to all pairs.

The mixed ensemble of massive and non-massive stars gives the overall
iteration budget both fast shallow runs and slower deeper runs, improving
solution quality without a uniform cost increase.

## Install

```sh
poetry install
```

To enable the optional plot feature:

```sh
poetry install -E plot
```

## Run

From the project root:

```sh
poetry run afn [tsp_file] [-i ITERATIONS] [-p PROCESSES] [--plot] [--plot-file OUTPUT.png] [--progress]

# Educative mode
poetry run afn [tsp_file] --educative [--educative-delay SECONDS] [--educative-record OUTPUT.gif|OUTPUT.mp4]
```

### Educative mode behavior

Educative mode is designed for step-by-step visualization and teaching:

- It always forces one iteration and one process.
- It animates each fusion event in three phases:
	- Selection: candidate pair is highlighted.
	- Compression: both elements move conceptually toward the fusion site.
	- Fusion: merged site is marked and star-state charts are updated.
- It shows two synchronized panels:
	- Spatial fusion process (nodes and fusion points).
	- Star life evolution (temperature, pressure, density, element count).

Input file resolution is flexible for convenience:

- Uses path as provided when it exists.
- Falls back to `app/<tsp_file>`.
- Falls back to `app/samples/<filename>`.

This means commands such as `poetry run afn dj38.tsp --educative` work from the project root.

When matplotlib runs in a non-interactive backend (for example, `Agg` in headless environments),
the app cannot open a live window. In that case, educative mode automatically records a GIF named
`educative_fusion.gif` unless `--educative-record` is explicitly provided.

## CLI arguments

- `tsp_file`: optional positional argument. Path to a TSPLIB `.tsp` file.
	- Default: `app/samples/dj38.tsp`
- `-i`, `--iterations`: optional number of simulation runs.
	- Default: `500`
	- Must be greater than `0`
- `-p`, `--processes`: optional number of worker processes.
	- Default: `1`
	- Must be greater than `0`
- `--plot`: optional flag to generate a solution plot image.
	- Default: disabled
- `--plot-file`: output path for the generated image.
	- Default: `solution.png`
- `--progress`: show a live progress bar with completion percent.
	- Default: disabled
- `--educative`: run a visual educational mode with animated fusion steps.
	- Forces exactly one iteration and one process
	- Opens a live graphic window showing fusion process and star-state evolution
    - In non-interactive backends, records a GIF automatically instead of opening a window
- `--educative-delay`: seconds between educational animation frames.
	- Default: `1.0`
	- Must be greater than `0`
- `--educative-record`: optional output animation file path in educational mode.
	- Supports formats allowed by matplotlib writers, such as `.gif` or `.mp4`

## Examples

Run with defaults:

```sh
poetry run afn
```

Run with a custom iteration count:

```sh
poetry run afn --iterations 100
```

Run with an explicit TSP file and short iteration flag:

```sh
poetry run afn app/samples/dj38.tsp -i 250
```

Run with multiple processes:

```sh
poetry run afn app/samples/dj38.tsp -i 1000 -p 4
```

Run and generate a plot image:

```sh
poetry run afn app/samples/dj38.tsp -i 300 -p 4 --plot --plot-file dj38_solution.png
```

Run with a progress bar:

```sh
poetry run afn app/samples/dj38.tsp -i 500 -p 4 --progress
```

Run educational mode (one forced iteration):

```sh
poetry run afn app/samples/dj38.tsp --educative --educative-delay 1.2
```

Run educational mode and record the animation:

```sh
poetry run afn app/samples/dj38.tsp --educative --educative-record fusion.gif
```

## Output format

The program prints:

- Input file
- Iteration count
- Process count
- Best route length
- Elapsed execution time
- Best route sequence
- Plot file path (when plotting is enabled)
- Fusion event count (in educative mode)
- Animation recording path (when recording is enabled or auto-fallback is used)