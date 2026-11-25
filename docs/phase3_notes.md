# Phase 3: Hybrid GA and 2-Opt

Local search explores nearby routes. 2-Opt reverses a delivery segment to reconnect two edges. On a unit square, a crossing tour of length `2 + 2*sqrt(2)` (4.8284) becomes the perimeter of length 4. The warehouse stays at index zero, and the closing edge is included.

The objective is `sum(d(route[i], route[i+1])) + d(last, warehouse)`.
First-improvement scans pairs in deterministic order and accepts only a reduction greater than `1e-10`. One pass means one accepted improvement followed by a restart. Search stops after the pass limit or a scan without improvement. The symmetric edge-difference formula filters moves; full route sums confirm acceptance. The public function validates the symmetric matrix and verifies its final distance using Phase 1.

A hybrid or memetic GA combines evolutionary exploration (trying different delivery orders) with exploitation (improving one order locally). Offspring receive local search after mutation. Elites remain unchanged. `local_search_rate=0.2` gives each offspring a 20% chance of refinement; `local_search_max_passes=5` limits each invocation to five accepted improvements. Rate zero preserves the standard GA random sequence exactly.

Workflow: initialize population -> evaluate -> preserve elites -> tournament selection -> OX -> swap mutation -> optional 2-Opt -> next generation -> record convergence -> repeat -> return best route.

Convergence records the initial best distance and best-so-far distance after each generation. It never increases. Applications count invocations; improvements count invocations that shorten a route, not individual moves.

Local search can improve solutions but adds computation and can reduce population diversity. Neither GA nor hybrid GA guarantees a global optimum. A hybrid run may finish worse than a standard GA run; one example cannot establish superiority. Equal generation counts do not imply equal computational effort. Results are reproducible except execution time. Benchmarking is reserved for Phase 4.
