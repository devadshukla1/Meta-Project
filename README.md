# Smart Last-Mile Delivery Route Optimization

This university project studies the Traveling Salesman Problem (TSP) for a courier that leaves a warehouse, visits each delivery address once, and returns to the warehouse. Choosing a short route can reduce travel effort and delivery time. Phase 1 supplies the data and reusable calculations; Phase 2 adds a standard genetic algorithm (GA).

## Objectives and technology

The project compares a nearest-neighbor baseline, standard genetic algorithm, and hybrid genetic algorithm with 2-Opt local search on an educational TSP delivery dataset.

**Academic Compliance Update:**
All optimization algorithms, pseudorandom number generators, mathematical operations (Newton-Raphson square root, accumulation, extrema), sorting algorithms (Merge Sort), and statistical metrics have been rewritten entirely from scratch in pure Python. No external computational packages or built-in optimization shortcuts (`random`, `math`, `statistics`, `sum()`, `min()`, `max()`, `sorted()`) are used in computational code. See detailed documentation in [docs/manual_algorithm_implementation.md](docs/manual_algorithm_implementation.md).

| Phase | Planned work |
| --- | --- |
| 1 | Dataset and TSP foundation (complete) |
| 2 | Standard genetic algorithm (complete) |
| 3 | Hybrid GA with 2-Opt (complete) |
| 4 | Benchmarking and statistical comparison (complete) |
| 5 | Streamlit dashboard (complete) |
| 6 | Testing and improvements (complete) |
| 7 | Documentation and viva preparation |

## Phase 1 functionality

`core.dataset` returns 20 independent location dictionaries: one warehouse (ID 0) and 19 destinations. `core.tsp` checks coordinates, builds a symmetric distance matrix, validates routes, and calculates complete route distance. `core.utils` provides seeded, independent random generators and valid random routes. `evaluation` is reserved for a later phase.

## Phase 2 genetic algorithm

`algorithms.genetic_algorithm` creates random route populations, scores complete round trips, selects parents through tournaments, combines delivery orders with Order Crossover, and applies swap mutation. Elitism copies the shortest routes to the next generation. The result records the best route, initial and final distances, best-so-far history, and measured execution time. Smaller distance is better; the GA is a heuristic and does not guarantee a global optimum. See [Phase 2 notes](docs/phase2_notes.md) for examples.

Default `GAConfig` values are population size **100**, generations **200**, crossover rate **0.9** per offspring, mutation rate **0.2** per offspring, tournament size **3**, elite count **2**, and seed **42**. These are demonstration settings, not proven optimal values.

**This dataset is fictional and intended for educational optimization experiments. Distances are calculated from synthetic Cartesian coordinates and do not represent actual road distances.** Names are inspired by Delhi-NCR, but coordinates are invented. The computed values have synthetic units.

For points `(x1, y1)` and `(x2, y2)`, Euclidean distance is `sqrt((x2 - x1)^2 + (y2 - y1)^2)`. The matrix stores full precision and uses location ID as its row and column index. Location IDs must be consecutive and ordered from 0.

A route is a Python list such as `[0, 3, 2, 1]`: start at warehouse 0 and include every other ID exactly once. Do not append 0; `calculate_route_distance` adds the final trip to the warehouse automatically.

## Run

Open a terminal in the `RouteOptimizer` folder. No package installation is needed.

```powershell
python -m core.tsp
python -m algorithms.genetic_algorithm
python -m unittest discover -s tests -v
```

The first command prints a reproducible random route; the second runs the GA and prints its best result. The third runs all Phase 1 and Phase 2 tests. In VS Code, open this folder and select a Python 3.11+ interpreter.

## Current limitations and next steps

Distances are straight-line synthetic values, not road travel times or GPS measurements. GA results depend on its parameters and random seed and are not guaranteed optimal. Phase 3 will add hybrid GA with 2-Opt; later phases will compare methods and present results in Streamlit.

## Phase 3

Run `python -m algorithms.hybrid_ga` for the memetic GA demo. It reuses standard GA evolution and adds optional 2-Opt after mutation. Defaults: `local_search_rate=0.2`, `local_search_max_passes=5`. Rate zero reproduces standard GA results. Run `python -m unittest discover -s tests -v` for all phases. See `docs/phase3_notes.md`.

## Phase 4 benchmark

`algorithms.nearest_neighbor` supplies a deterministic baseline. `evaluation.benchmark` compares that baseline with 20 standard GA and 20 hybrid GA runs using seeds 42–61. Default GA settings are population 100, 200 generations, crossover 0.9, mutation 0.2, tournament 3, and elitism 2. Hybrid local search uses rate 0.2 and up to 5 accepted improvements per invocation. All algorithms use the same synthetic distance matrix.

From this folder run `python -m evaluation.benchmark`. Run `python -m unittest discover -s tests -v` to test all phases. The benchmark prints best and mean distances, sample standard deviations, mean execution times, and percentage improvements. It writes `results/benchmark_summary.json`, `results/benchmark_runs.csv`, and `results/convergence_history.json`. Rerunning updates these three files; unrelated files are preserved. See `docs/phase4_notes.md` for interpretation.

The default experiment compares equal GA settings and paired seeds, while hybrid local search adds computational work. Exact objective-evaluation counts are not measured. The one synthetic 20-location instance and computer-dependent timings limit generalization.

## Phase 5 dashboard

The Streamlit app has Overview, Route Optimization, Algorithm Comparison, Dataset Explorer, and About sections. It runs NN, standard GA, and hybrid GA from forms, draws routes from synthetic Cartesian coordinates, charts actual convergence, and supports in-memory CSV downloads. The comparison page offers one-run and multi-run experiments. `app.py` handles the UI; pure CSV and SVG helpers are in `ui/helpers.py`. See `docs/phase5_notes.md`.

In Windows PowerShell, from the `RouteOptimizer` folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m unittest discover -s tests -v
```

If Streamlit is missing, install the requirements in the active environment. If imports fail, start from the project folder and select the same Python interpreter in VS Code. If the default port is busy, add `--server.port 8502`. If the browser does not open automatically, use the local URL printed by Streamlit.

The dashboard uses the same synthetic instance and heuristic algorithms described above; its timings depend on the machine and larger benchmarks can take minutes.

## Phase 6 verification

The quality pass added controlled operator, generation, export, and dashboard regression tests. Run `python -m unittest discover -s tests -v` from this folder. The default dashboard settings work for a route demonstration; for a quick statistical demonstration use 1–3 runs, population 20, and 30 generations. The dashboard warns when a benchmark configuration may take several minutes. See `docs/phase6_notes.md` and `docs/testing_report.md` for the measured results and limitations.
