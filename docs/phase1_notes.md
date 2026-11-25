# Phase 1 notes for viva

## What is TSP?

The Traveling Salesman Problem asks for the shortest round trip that visits every location once. Here the courier starts at warehouse 0, completes all deliveries, and returns there.

## Why is it a combinatorial optimization problem?

The answer is an ordering of delivery stops. With 19 destinations, there are `19!` possible orders if the start is fixed. Trying every order quickly becomes impractical as the number of stops grows, so later phases will use search methods.

## Why use a symmetric distance matrix?

The synthetic Cartesian distance from A to B equals the distance from B to A. A symmetric matrix stores the distance for each pair and lets route calculations look it up quickly. The diagonal is zero because travel from a point to itself has zero distance. Real roads may be one-way or asymmetric; this model does not capture that.

## Why validate routes?

A route with a missing destination, repeated destination, or wrong starting point does not represent the required delivery job. Validation prevents a misleading distance from being reported for such a route. It also rejects booleans, which Python otherwise treats like integers.

## Why use reproducible random seeds?

A seeded `random.Random` object gives the same shuffled route when created with the same seed. This helps debug code and compare later algorithms fairly. It does not change the global random state.

## How will later phases use these modules?

The standard GA can generate initial routes with `core.utils`, then score them with `core.tsp`. The hybrid GA can use the same scoring and validation after its 2-Opt improvements. Both can share the dataset and distance matrix, keeping the algorithms independent of the future Streamlit interface.

**This dataset is fictional and intended for educational optimization experiments. Distances are calculated from synthetic Cartesian coordinates and do not represent actual road distances.**
