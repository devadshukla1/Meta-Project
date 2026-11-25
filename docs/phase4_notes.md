# Phase 4: Benchmarking and performance analysis

Benchmarking means running algorithms on the same problem and recording their results. Here Nearest Neighbor (NN), standard GA, and hybrid GA solve one fictional 20-location TSP. NN repeatedly picks the nearest unvisited location, breaking ties by smaller ID. It provides a simple deterministic reference; its single result is not an independent random sample.

GA and hybrid GA each run 20 times with paired seeds 42 through 61. A seed initializes the random generator so route and convergence results can be reproduced. The same seed schedule controls an experiment, but the algorithms can consume random numbers differently. Multiple runs show variability that one run hides.

Mean is the arithmetic average. Median is the middle value after sorting. Sample standard deviation measures spread around the mean using `n-1` in the denominator; it is unavailable for one observation. Best and worst are the minimum and maximum distances. A shorter route is better. A shorter measured execution time means less runtime on this machine, but timings vary with load and hardware.

Percentage improvement is `(reference_distance - candidate_distance) / reference_distance * 100`. Positive values mean a shorter candidate route. Zero reference distance yields an unavailable value. The benchmark reports individual improvements against NN and paired hybrid-over-GA improvements; the mean of percentages differs from the percentage computed from mean distances.

Convergence history records best-so-far distance at generation zero and after each generation. Mean convergence averages the same generation across runs. These histories can show when progress slowed, but no charts are generated in this phase.

Computational budget means how much work an algorithm gets. GA and hybrid GA share population size, generations, operator rates, and seed schedule. Hybrid GA additionally performs 2-Opt searches, so equal generations do not mean equal work. Runtime is reported alongside quality. Exact objective-evaluation counts are not measured; a 2-Opt edge check has a different cost from a full route evaluation.

The measured default experiment in this workspace found NN distance 405.11, standard GA mean 356.26 and best 330.60, and hybrid GA mean and best 323.67 synthetic units. Across those 20 runs, hybrid GA took more time on average. This observation describes this dataset and seed schedule only. The coordinates are fictional, road distances are not modeled, timing varies, and no method guarantees a global optimum. The preferred method depends on the quality and runtime needed.

Run `python -m evaluation.benchmark` to repeat the experiment. It updates only `results/benchmark_summary.json`, `results/benchmark_runs.csv`, and `results/convergence_history.json`; other files are preserved. The summary stores settings, dataset details, NN, descriptive statistics, paired comparison summary, and budget notes. CSV has one row per GA or hybrid run. The convergence JSON stores individual and mean histories.
