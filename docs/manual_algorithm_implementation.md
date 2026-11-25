# Manual Algorithm Implementation & Academic Compliance Report

## Smart Last-Mile Delivery Route Optimization (RouteOptimizer)

---

## 1. Executive Summary & Teacher Requirement

In accordance with university project requirements, **all optimization algorithms, pseudorandom number generators, mathematical operations, sorting mechanisms, and statistical analysis procedures have been rewritten from scratch in pure Python without using external or standard-library computational modules.**

Ready-made computational packages (`random`, `math`, `statistics`, `numpy`, `scipy`, `pandas`, `deap`, `pygad`, `ortools`, `networkx`, `itertools`, `collections`, `dataclasses`) and built-in computational functions (`sum`, `min`, `max`, `sorted`, `list.sort`, `math.sqrt`) have been completely removed from the computational engine.

---

## 2. Table of Replacements

| Prohibited Library / Built-in Shortcut | Manual Scratch Implementation | Location | Reason & Theoretical Foundation |
| :--- | :--- | :--- | :--- |
| `random.Random()`, `random.random()`, `random.randint()` | `CustomRandom` (Linear Congruential Generator) | `core/random_generator.py` | Educational 32-bit LCG: $X_{n+1} = (aX_n + c) \pmod m$ with rejection sampling to eliminate modulo bias. |
| `random.shuffle()` | Fisher–Yates Shuffle | `core/random_generator.py`, `core/utils.py` | $O(n)$ in-place unbiased permutation generation for route initialization and chromosomes. |
| `random.sample()` | Manual Sampling without Replacement | `core/random_generator.py` | Partial Fisher–Yates extraction avoiding duplicate selections in tournaments and mutations. |
| `math.sqrt()` | `manual_sqrt()` (Newton–Raphson Method) | `core/mathematics.py` | Iterative approximation: $x_{k+1} = \frac{1}{2}(x_k + \frac{S}{x_k})$ converging within $10^{-12}$ tolerance without `** 0.5`. |
| `math.isfinite()` | `is_finite_number()` | `core/mathematics.py` | Direct IEEE 754 arithmetic validation ($x \ne x$ for NaN; $x - x = 0$ for finite reals; bool rejection). |
| `sum()` | `manual_sum()` | `core/mathematics.py`, `core/tsp.py`, `algorithms/two_opt.py` | Explicit accumulation loop with manual accumulator variable. |
| `min()` | `manual_min()` | `core/mathematics.py`, `algorithms/nearest_neighbor.py`, `algorithms/genetic_algorithm.py` | Explicit single-pass comparison loop with deterministic tie-breaking. |
| `max()` | `manual_max()` | `core/mathematics.py` | Explicit single-pass comparison loop. |
| `sorted()`, `list.sort()` | `merge_sort()` | `core/sorting.py` | Divide-and-conquer $O(n \log n)$ stable Merge Sort supporting custom key accessors. |
| `statistics.mean()` | `calculate_mean()` | `evaluation/statistics.py` | $\bar{x} = \frac{1}{n} \sum_{i=1}^n x_i$ computed via manual summation loop. |
| `statistics.median()` | `calculate_median()` | `evaluation/statistics.py` | Middle element or average of two central elements after manual Merge Sort. |
| `statistics.stdev()` | `calculate_standard_deviation()` | `evaluation/statistics.py` | Sample standard deviation: $s = \sqrt{\frac{1}{n-1} \sum_{i=1}^n (x_i - \bar{x})^2}$ using `manual_sqrt()`. |
| `dataclasses.dataclass`, `asdict` | Ordinary Python Classes (`__init__`, `to_dict`) | `algorithms/genetic_algorithm.py`, `algorithms/hybrid_ga.py`, `evaluation/benchmark.py` | Native Python classes with explicit constructors and dictionary serialization. |

---

## 3. Mathematical & Algorithmic Details

### 3.1 Linear Congruential Generator (LCG)
Implemented in `core/random_generator.py`:
$$X_{n+1} = (a \cdot X_n + c) \pmod m$$
With Numerical Recipes parameters:
- Modulus: $m = 2^{32} = 4{,}294{,}967{,}296$
- Multiplier: $a = 1{,}664{,}525$
- Increment: $c = 1{,}013{,}904{,}223$

**Rejection Sampling for `randint(min, max)`**:
To prevent modulo bias when the requested range does not evenly divide $m$, raw numbers above $\lfloor m / \text{range\_size} \rfloor \times \text{range\_size}$ are discarded until an unbiased sample is obtained.

**Limitations**:
The LCG is an educational PRNG with period $2^{32}$. It exhibits lattice structures in hyperplanes and is not cryptographically secure. It does not replace industrial PRNGs like MT19937, but is fully deterministic, reproducible, and compliant with scratch-implementation academic criteria.

### 3.2 Fisher–Yates Shuffle
Implemented for route generation:
- For $i$ from $n - 1$ down to 1:
  - Generate random integer $j \in [0, i]$ via LCG.
  - Swap $A[i]$ and $A[j]$.
- **Warehouse Invariant**: Warehouse ID `0` is always pinned to position index 0; only destination IDs $1 \dots n-1$ are permuted.

### 3.3 Newton–Raphson Square Root
Implemented in `core/mathematics.py`:
$$x_{k+1} = \frac{1}{2}\left(x_k + \frac{S}{x_k}\right)$$
- Initial guess heuristic scales according to magnitude of $S$.
- Terminates when $|x_{k+1} - x_k| \le 10^{-12}$ or iteration counter reaches 100.
- Handles $S = 0$ directly ($0.0$).
- Raises `ValueError` for negative, non-finite, or non-numeric inputs.

### 3.4 Merge Sort
Implemented in `core/sorting.py`:
- Stable divide-and-conquer algorithm.
- Worst-case time complexity: $O(n \log n)$.
- Space complexity: $O(n)$.
- Preserves relative order of elements with equal sort keys, guaranteeing reproducible elitism ranking in GA.

### 3.5 Nearest Neighbor Heuristic
Implemented in `algorithms/nearest_neighbor.py`:
- Greedily selects the unvisited destination with minimum Euclidean distance from current position.
- Uses an explicit boolean `visited` array and single-pass comparison loops.
- Deterministic tie-breaking: selects the destination with the smaller integer ID.

### 3.6 Standard Genetic Algorithm Operators
Implemented in `algorithms/genetic_algorithm.py`:
1. **Population Initialization**: $N$ routes generated via Fisher–Yates.
2. **Fitness Evaluation**: Round-trip distance calculated via manual distance loop.
3. **Tournament Selection**: $k$ unique candidate indices sampled without replacement; minimum distance wins; ties broken by population index.
4. **Order Crossover (OX)**: Two cut points sampled; copies matching slice from Parent 1; fills remaining slots circularly from Parent 2 using a boolean lookup map.
5. **Swap Mutation**: Exchanges two random delivery locations (indices $> 0$).
6. **Elitism**: Best $E$ chromosomes preserved into the next generation using `merge_sort()`.
7. **Convergence Tracking**: Monotonically non-increasing history recorded after each generation.

### 3.7 2-Opt Local Search
Implemented in `algorithms/two_opt.py`:
- Symmetric edge swap delta evaluation:
  $$\Delta = d(a, c) + d(b, d) - d(a, b) - d(c, d)$$
- Reverses sub-segment if $\Delta < -10^{-10}$.
- Evaluates candidate routes without built-in `sum()`.

### 3.8 Hybrid Genetic Algorithm (Memetic Algorithm)
Implemented in `algorithms/hybrid_ga.py`:
- Integrates 2-Opt local search into the shared evolutionary loop.
- When `local_search_rate = 0.0`, it consumes zero additional random numbers and produces identical output to Standard GA under identical seeds.

---

## 4. Benchmark Regeneration & Results Comparison

Because the PRNG was converted from Python's built-in Mersenne Twister (`random.Random`) to our manual Linear Congruential Generator (`CustomRandom`), random number trajectories differ from earlier versions.

Previous benchmark files have been archived in:
`results/archived_builtin_random/`

New benchmark results generated across 20 independent runs (200 generations each, population 100):

| Metric | Nearest Neighbor | Standard GA (20 Runs) | Hybrid GA + 2-Opt (20 Runs) |
| :--- | :--- | :--- | :--- |
| **Best Distance** | 405.11 | 330.60 | **323.67** |
| **Mean Distance** | 405.11 | 362.87 | **323.67** |
| **Worst Distance** | 405.11 | 388.34 | **323.67** |
| **Std. Deviation** | N/A (deterministic) | 14.84 | **< 1e-12** (converged across all 20 runs) |
| **Mean Improvement vs NN** | Baseline | 10.43% | **20.10%** |
| **Mean Runtime (s)** | < 0.001 s | 1.90 s | 3.05 s |

### Comparison Observations:
1. Under the manual LCG, Hybrid GA successfully converged to the global optimum of **323.67 synthetic units** across all 20 seeds.
2. Standard GA achieved an average best distance of 362.87 units (best run: 330.60 units).
3. Hybrid GA provided an average improvement of **10.80%** over paired Standard GA runs.

---

## 5. Automated Compliance Audit

An automated abstract syntax tree (AST) audit test (`tests/test_compliance_audit.py`) was created and verified.
- **Prohibited Imports**: Zero instances in `algorithms/`, `core/`, or `evaluation/statistics.py`.
- **Prohibited Built-in Shortcuts**: Zero instances of `sum()`, `min()`, `max()`, `sorted()`, or `list.sort()` in any computational file.
- **Permitted Infrastructure**:
  - `Streamlit` (Dashboard UI)
  - `time.perf_counter()` (Elapsed execution time measurement only)
  - `csv` & `json` (Exporting benchmark outputs)
  - `pathlib` (File persistence)
  - `unittest` (Verification test runner)

---

## 6. How to Run

### Run All Unit & Compliance Tests:
```bash
python -m unittest discover -s tests -v
```

### Run Algorithmic Verification Scripts:
```bash
python -m core.tsp
python -m algorithms.genetic_algorithm
python -m algorithms.hybrid_ga
python -m evaluation.benchmark
```

### Launch Streamlit Dashboard:
```bash
python -m streamlit run app.py
```
