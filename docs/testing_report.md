# Phase 6 testing report

- Date: 18 November 2026 (Asia/Calcutta)
- Host: Windows 11, Python 3.14.3, Streamlit 1.56.0
- Full suite: 61 tests passed, 0 failed, 0 skipped (run after Phase 6 changes)
- Demonstrations: Phase 1, standard GA, hybrid GA, and full benchmark completed
- Browser: overview, route controls, NN result, hybrid result, and convergence chart inspected
- AppTest: navigation, three algorithms, small benchmark, and invalid settings exercised

Defects fixed: Hybrid-specific controls were hidden until form submission because algorithm selection lived inside the form; long dataset and distance metric values truncated in a laptop viewport. Added targeted regression tests for the controls and algorithm invariants. No optimization mathematics or public interface changed.

Measured before UI correction (seconds, single runs on the 20-location dataset):

| Size | GA | Hybrid GA |
| --- | ---: | ---: |
| 20 population, 30 generations | 0.055 | 0.095 |
| 100 population, 200 generations | 2.216 | 3.562 |
| 150 population, 300 generations | 4.983 | 7.909 |

No algorithm performance optimization was made, so a before/after speed comparison does not apply. The later full benchmark measured mean GA time 2.348 s and mean hybrid time 3.823 s across 20 paired seeds; run conditions and system load differed from the single-run profile.

The project test suite and browser ran on Windows. A separate Python 3.11 interpreter and a clean virtual-environment installation were not tested. Browser interaction did not manually download every CSV, but pure CSV generators and benchmark JSON/CSV exports were checked by automated tests. Saved Phase 4 results were preserved; the Phase 6 benchmark wrote its outputs to a temporary directory.
