"""RouteOptimizer dashboard. Start with python -m streamlit run app.py."""

import time

import streamlit as st

from algorithms.genetic_algorithm import run_genetic_algorithm
from algorithms.hybrid_ga import run_hybrid_ga
from algorithms.nearest_neighbor import nearest_neighbor
from core.dataset import get_delivery_locations
from core.tsp import create_distance_matrix, validate_route
from ui.helpers import (csv_text, history_csv, improvement_text, locations_csv,
                        make_ga_config, matrix_csv, route_csv, route_svg)

st.set_page_config(page_title="RouteOptimizer", page_icon="🚚", layout="wide")
st.markdown("""<style>.block-container{max-width:1400px;padding-top:2rem}
[data-testid="stMetric"]{background:#1e293b;padding:1rem;border-radius:14px}
h1,h2,h3{letter-spacing:-.02em}</style>""", unsafe_allow_html=True)


@st.cache_data
def project_data():
    places = get_delivery_locations()
    return places, create_distance_matrix(places)


try:
    locations, matrix = project_data()
except (ValueError, KeyError, OSError) as error:
    st.error(f"Could not load dataset: {error}")
    st.stop()

NAMES = ("Nearest Neighbor", "Standard Genetic Algorithm",
         "Hybrid Genetic Algorithm + 2-Opt")
DISCLAIMER = ("This visualization uses fictional Cartesian coordinates for educational purposes. "
              "It does not represent actual road geography or driving distances.")


def parameters(algorithm=None):
    name = algorithm
    if name == NAMES[0]:
        return name, {}
    values = {}
    values["population_size"] = int(st.number_input("Population size", 2, 500, 100))
    values["generations"] = int(st.number_input("Generations", 1, 1000, 200))
    values["crossover_rate"] = st.slider("Crossover rate", 0.0, 1.0, 0.9, 0.05)
    values["mutation_rate"] = st.slider("Mutation rate", 0.0, 1.0, 0.2, 0.05)
    values["tournament_size"] = int(st.number_input("Tournament size", 2, 500, 3,
                                                     help="Cannot exceed population size."))
    values["elitism_count"] = int(st.number_input("Elite routes", 1, 499, 2,
                                                   help="Must be less than population size."))
    values["seed"] = int(st.number_input("Seed", -1000000, 1000000, 42))
    if name is None or name == NAMES[2]:
        values["local_search_rate"] = st.slider("2-Opt application rate", 0.0, 1.0, 0.2, 0.05)
        values["local_search_max_passes"] = int(st.number_input("Maximum 2-Opt improvements", 1, 50, 5))
    return name, values


def run_one(name, values):
    if name == NAMES[0]:
        start = time.perf_counter()
        route, distance = nearest_neighbor(matrix)
        return {"name": name, "route": route, "distance": distance,
                "time": time.perf_counter() - start, "settings": "Deterministic baseline"}
    hybrid = name == NAMES[2]
    config = make_ga_config(values, hybrid)
    output = run_hybrid_ga(matrix, config) if hybrid else run_genetic_algorithm(matrix, config)
    item = {"name": name, "route": output.best_route, "distance": output.best_distance,
            "time": output.execution_time, "settings": config.to_dict(), "seed": output.seed,
            "initial": output.initial_best_distance, "generations": output.generations_completed,
            "history": output.convergence_history}
    if hybrid:
        item.update(applications=output.local_search_applications,
                    improvements=output.local_search_improvements)
    return item


def route_plot(route=None):
    st.markdown(route_svg(locations, route), unsafe_allow_html=True)
    st.caption(DISCLAIMER)


def chart(series):
    rows = [{"Generation": index, **{name: values[index] for name, values in series.items()}}
            for index in range(len(next(iter(series.values()))))]
    st.line_chart(rows, x="Generation", y=list(series),
                  y_label="Best-so-far synthetic distance units")


def show_route(item):
    if not validate_route(item["route"], len(locations)):
        st.error("The algorithm returned an invalid route.")
        return
    st.caption(f"Result from {item['name']} with settings: {item['settings']}")
    cols = st.columns(4)
    cols[0].metric("Distance · synthetic units", f"{item['distance']:.2f}")
    cols[1].metric("Execution time", f"{item['time']:.3f} s")
    cols[2].metric("Delivery stops", len(item["route"]) - 1)
    cols[3].metric("Route valid", "Yes")
    if "initial" in item:
        more = st.columns(4)
        more[0].metric("Initial best", f"{item['initial']:.2f}")
        more[1].metric("Improvement", improvement_text(item["initial"], item["distance"]))
        more[2].metric("Generations", item["generations"])
        more[3].metric("Seed", item["seed"])
    if "applications" in item:
        a, b = st.columns(2)
        a.metric("2-Opt applications", item["applications"])
        b.metric("2-Opt improvements", item["improvements"])
    route_plot(item["route"])
    st.write("Visit order: " + " → ".join(locations[index]["name"]
                                           for index in item["route"] + [0]))
    st.download_button("Download route CSV", route_csv(item["route"], locations,
                       item["name"], item.get("seed"), item["settings"]),
                       "optimized_route.csv", "text/csv")
    if "history" in item:
        st.subheader("Convergence")
        chart({item["name"]: item["history"]})
        st.download_button("Download convergence CSV", history_csv({item["name"]: item["history"]}),
                           "convergence.csv", "text/csv")
    else:
        st.info("Nearest Neighbor constructs a route in one pass, so it has no generation history.")


st.sidebar.title("RouteOptimizer")
page = st.sidebar.radio("Navigate", ("Overview", "Route Optimization", "Algorithm Comparison",
                                     "Dataset Explorer", "About the Project"))
st.title("RouteOptimizer")
st.caption("Smart Last-Mile Delivery Route Optimization Using Genetic Algorithms")

if page == "Overview":
    st.write("An interactive optimization system that compares traditional and evolutionary approaches for solving the Traveling Salesman Problem.")
    for col, label, value in zip(st.columns(4), ("Locations", "Warehouses", "Algorithms", "Dataset"),
                                 (len(locations), sum(p["type"] == "warehouse" for p in locations),
                                  len(NAMES), "Synthetic")):
        col.metric(label, value)
    st.subheader("The delivery problem")
    st.write("Start at the warehouse, visit each destination once, and return. Nearest Neighbor selects the next closest stop. GA explores many route orders. Hybrid GA adds 2-Opt local improvement.")
    st.info("Quick start: run each method on Route Optimization, then compare them with shared seeds on Algorithm Comparison.")
    route_plot()

elif page == "Route Optimization":
    st.header("Route Optimization")
    selected = st.selectbox("Algorithm", NAMES)
    with st.form("optimization_form"):
        _, values = parameters(algorithm=selected)
        submitted = st.form_submit_button("Run Optimization", type="primary")
    if submitted:
        try:
            with st.spinner("Running optimization..."):
                st.session_state["latest_optimization_result"] = run_one(selected, values)
        except Exception as error:
            st.error(f"Optimization failed. Check settings: {error}")
    if "latest_optimization_result" in st.session_state:
        show_route(st.session_state["latest_optimization_result"])
    else:
        st.info("Choose an algorithm and select Run Optimization.")

elif page == "Algorithm Comparison":
    st.header("Algorithm Comparison")
    st.info("Standard GA and Hybrid GA use comparable genetic parameters and the same random seed. Hybrid GA performs additional local-search operations, so equal generations do not imply equal computational cost.")
    with st.form("comparison_form"):
        _, values = parameters()
        submitted = st.form_submit_button("Run Comparison", type="primary")
    if submitted:
        try:
            with st.spinner("Running all three algorithms..."):
                runs = [run_one(name, values) for name in NAMES]
            st.session_state["latest_comparison"] = {"runs": runs,
                                                      "settings": values.copy()}
        except Exception as error:
            st.error(f"Comparison failed. Check settings: {error}")
    latest = st.session_state.get("latest_comparison")
    if latest:
        st.caption(f"Showing Quick Comparison from settings: {latest['settings']}")
        runs = latest["runs"]
        reference = runs[0]["distance"]
        st.table([{"Algorithm": run["name"], "Distance": run["distance"],
                   "Time (s)": run["time"], "vs NN": improvement_text(reference, run["distance"]),
                   "Valid": validate_route(run["route"], len(locations))} for run in runs])
        series = {run["name"]: run["history"] for run in runs if "history" in run}
        chart(series)
        st.download_button("Download comparison CSV", csv_text(
            ("algorithm", "distance", "execution_seconds", "improvement_over_nn", "valid"),
            ((run["name"], run["distance"], run["time"],
              improvement_text(reference, run["distance"]),
              validate_route(run["route"], len(locations))) for run in runs)),
            "quick_comparison.csv", "text/csv")

elif page == "Dataset Explorer":
    st.header("Dataset Explorer")
    st.info(DISCLAIMER + " Euclidean distances are symmetric.")
    st.table(locations)
    route_plot()
    st.download_button("Download locations CSV", locations_csv(locations),
                       "delivery_locations.csv", "text/csv")
    with st.expander("Distance matrix (synthetic distance units)"):
        st.dataframe(matrix, use_container_width=True)
    st.download_button("Download distance matrix CSV", matrix_csv(matrix),
                       "distance_matrix.csv", "text/csv")

else:
    st.header("About the Project")
    st.write("Smart Last-Mile Delivery Route Optimization Using a Hybrid Genetic Algorithm and 2-Opt Local Search")
    st.write("Objective: minimize complete round-trip distance, starting at warehouse 0 and visiting every destination exactly once.")
    st.write("The synthetic dataset produces a symmetric distance matrix. GA initializes a population, selects parents by tournament, uses Order Crossover and swap mutation, and preserves elite routes. Hybrid GA refines selected offspring with 2-Opt. Benchmarking reports descriptive statistics across shared seeds.")
    st.write("Limitations: fictional coordinates, Euclidean distances, no traffic or road network, no vehicle capacity or time windows, and no global-optimality guarantee.")
