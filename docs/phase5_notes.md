# Phase 5 dashboard notes

RouteOptimizer is a Streamlit classroom interface over the existing Python algorithms. The sidebar has Overview, Route Optimization, Algorithm Comparison, Dataset Explorer, and About the Project. Overview introduces the problem. Route Optimization runs Nearest Neighbor, standard GA, or hybrid GA from a form. Algorithm Comparison runs a single-seed Quick Comparison across all three algorithms. Dataset Explorer shows the fictional coordinates and calculated matrix; About explains the method and limitations.

Set population, generations, operator probabilities, tournament size, elite count, and seed before selecting Run Optimization. Hybrid GA also exposes 2-Opt application rate and improvement limit. The configuration classes validate combinations such as tournament size versus population size. A spinner appears while an algorithm runs. Results remain in Streamlit session state after control changes and carry the settings used to produce them. A new run replaces the previous result. Nothing runs merely because a slider changes.

The route graphic is SVG generated from the synthetic Cartesian coordinates. It marks warehouse and destinations differently and draws every route edge, including the final return. It is not a road map. The convergence chart uses the actual best-so-far history, including generation zero. A flat segment means no new best route during those generations. NN has no generation history.

Algorithm Comparison runs Nearest Neighbor, standard GA, and hybrid GA with shared genetic parameters and a single random seed. Hybrid GA performs additional local-search work, so matching generation counts do not match computation budgets.

Download buttons provide location and matrix CSVs, a route CSV including the warehouse return, Quick Comparison CSV, and convergence histories. Downloads are generated in memory and do not change saved Phase 4 results. Pure CSV and SVG helpers live in `ui/helpers.py`; `app.py` handles Streamlit presentation; algorithms and offline benchmarking stay separate.

For a 5–8 minute demonstration: show Overview and Dataset Explorer, run NN, then standard GA and hybrid GA from Route Optimization, open Algorithm Comparison, explain distance versus execution time and convergence, and download the comparison CSV.

This demonstration uses one synthetic 20-location instance with Euclidean distances. It has no traffic, real roads, capacity, time windows, or global-optimality guarantee. Longer benchmark settings can take minutes. Run `python -m streamlit run app.py` from the project folder.
