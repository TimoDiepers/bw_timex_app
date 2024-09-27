import json

import streamlit as st
from copy import deepcopy
from abc import abstractmethod
import numpy as np
import pandas as pd
import plotly.express as px
import numpy as np
import bw2data as bd
import bw2calc as bc

from bw2data.backends import ActivityDataset as AD
from bw2data.subclass_mapping import NODE_PROCESS_CLASS_MAPPING
from bw_temporalis import TemporalDistribution
from bw_temporalis.utils import easy_timedelta_distribution
from bw_graph_tools.graph_traversal import NewNodeEachVisitGraphTraversal
from bw_timex.utils import get_exchange

# Initialize Streamlit App
st.set_page_config(
    page_title="bw_timex_app", layout="wide", initial_sidebar_state="collapsed"
)

st.markdown(
    body="""
        <style>
            .block-container {
                    padding-top: 20px;
                    padding-bottom: 0px;
                }
        </style>
    """,
    unsafe_allow_html=True,
)

RESOLUTION_LABELS = {
    "Years": "Y",
    "Months": "M",
    "Weeks": "W",
    "Days": "D",
    "Hours": "h",
    "Minutes": "m",
    "Seconds": "s",
}


if "current_project" not in st.session_state:
    st.switch_page("project_selection.py")


def identify_activity_type(activity):
    """Return the activity type based on its naming."""
    name = activity["name"]
    if "treatment of" in name:
        return "treatment"
    elif "market for" in name:
        # if not "to generic" in name:  # these are not markets, but also transferring activities
        return "market"
    elif "market group" in name:
        # if not "to generic" in name:
        return "marketgroup"
    else:
        return "production"


def reset_candidates_state():
    if "current_candidates" in st.session_state:
        st.session_state.pop("current_candidates")
    if "selected_candidate" in st.session_state:
        st.session_state.pop("selected_candidate")
    if "selected_candidate_exchanges" in st.session_state:
        st.session_state.pop("selected_candidate_exchanges")
    if "selected_exchange" in st.session_state:
        st.session_state.pop("selected_exchange")


@st.dialog("Adding Temporal Information", width="large")
def add_temporal_information(selected_exchange):
    st.write(selected_exchange)
    col_input, col_graph = st.columns([1, 2])
    td = None

    with col_input:
        # Initialize list to store points
        if "manual_amounts" not in st.session_state:
            st.session_state.manual_amounts = []
        if "manual_dates" not in st.session_state:
            st.session_state.manual_dates = []

        distribution_type = st.selectbox(
            "Distribution Type", options=["uniform", "triangular", "normal", "manual"]
        )  # , "manual"

        selected_time_resolution_label = st.selectbox(
            "Time Resolution", options=["Years", "Months", "Days", "Hours"]
        )
        selected_time_resolution = RESOLUTION_LABELS[selected_time_resolution_label]

        if distribution_type:
            col_start, col_end = st.columns(2)
            with col_start:
                start = st.number_input("Start", value=0)
            with col_end:
                end = st.number_input("End", value=10)
            min_steps = 1
            steps = st.slider(
                "Steps", min_value=min_steps, max_value=abs(end) + 1, value=abs(end) + 1
            )

        if distribution_type == "uniform":
            td = easy_timedelta_distribution(
                start=start,
                end=end,
                resolution=selected_time_resolution,
                steps=steps,
                kind="uniform",
            )
            min_steps = 3

        if distribution_type == "triangular":
            param = st.slider("Mode", min_value=0.001, max_value=float(end), value=1.0)

            td = easy_timedelta_distribution(
                start=start,
                end=end,
                resolution=selected_time_resolution,
                steps=steps,
                kind=distribution_type,
                param=param,
            )
            min_steps = 3

        if distribution_type == "normal":
            param = st.slider(
                "Standard Deviation", min_value=0.001, max_value=3.0, value=0.5
            )
            td = easy_timedelta_distribution(
                start=start,
                end=end,
                resolution=selected_time_resolution,
                steps=steps,
                kind=distribution_type,
                param=param,
            )

        if distribution_type == "manual":

            # Add the point when the button is clicked
            amounts_input = st.text_input("Share (Array)", value="[0.1, 0.2, 0.7]")
            st.session_state.manual_amounts = np.array(eval(amounts_input))
            dates_input = st.text_input("Dates (Array)", value="[-5, 0, 2]")
            st.session_state.manual_dates = np.array(eval(dates_input))

            if sum(st.session_state.manual_amounts) != 1:
                st.error(f"The current amounts don't add up to 1")
            else:
                timedelta_type = f"timedelta64[{selected_time_resolution}]"
                td = TemporalDistribution(
                    date=np.array(st.session_state.manual_dates, dtype=timedelta_type),
                    amount=np.array(st.session_state.manual_amounts),
                )
        if td:
            td_df = pd.DataFrame({"date": td.date, "amount": td.amount})

            # Handle years manually (approximate a year as 365.25 days)
            if selected_time_resolution == "Y":
                td_df["date_converted"] = (
                    td_df["date"] / np.timedelta64(1, "D") / 365.25
                )
            elif selected_time_resolution == "M":
                td_df["date_converted"] = (
                    td_df["date"] / np.timedelta64(1, "D") / 30.4375
                )
            else:
                # Conversion factors for other units
                conversion_factor = {
                    "D": np.timedelta64(1, "D"),
                    "h": np.timedelta64(1, "h"),
                }

                # Convert timedelta64 to the chosen unit as floats
                td_df["date_converted"] = (
                    td_df["date"] / conversion_factor[selected_time_resolution]
                )

        if st.button(
            "Add to Exchange", use_container_width=True, type="primary", disabled=not td
        ):
            selected_exchange["temporal_distribution"] = td
            selected_exchange.save()
            st.rerun()
            # st.toast("Temporal Information added to the Exchange", icon="🎉")

    with col_graph:
        # Create a scatter plot
        if td:
            fig = px.scatter(
                td_df,
                x="date_converted",
                y="amount",
                labels={
                    "date_converted": f"Timedelta ({selected_time_resolution_label})",
                    "amount": "Amount",
                },
            )
            # Display the plot in Streamlit
            st.plotly_chart(fig)
        else:
            st.info("No Temporal Distribution to display.")


def node_class(database_name):
    backend = bd.databases[database_name].get("backend", "sqlite")
    return NODE_PROCESS_CLASS_MAPPING.get(backend, NODE_PROCESS_CLASS_MAPPING["sqlite"])


@st.cache_data
def find_candidates(db, activity_name=None, location=None):
    # Mapping from input field to model attributes
    mapping = {
        "database": AD.database,
        "name": AD.name,
        "location": AD.location,
        # "product": AD.product,
    }

    # Start with the query set
    qs = AD.select()

    # Apply filters based on user inputs
    qs = qs.where(mapping["database"] == db)

    if activity_name:
        qs = qs.where(mapping["name"].contains(activity_name))
    if location:
        qs = qs.where(mapping["location"].contains(location))

    # Retrieve candidates based on the filtered query
    return [node_class(obj.database)(obj) for obj in qs]


def calculate(demand, method, **kwargs):

    lca = bc.LCA(demand={demand: 1}, method=method)
    lca.lci(factorize=True)
    lca.lcia()
    data = NewNodeEachVisitGraphTraversal.calculate(
        lca_object=lca,
        **kwargs,
    )

    dict_view = {
        "Score": [],
        "Product": [],
        "Producer": [],
        "Consumer": [],
    }
    dict_store = {
        "producer_node": [],
        "consumer_node": [],
        "score": [],
    }

    for edge in data["edges"]:
        if edge.producer_index != -1 and edge.consumer_index != -1:
            producer_node = bd.get_node(
                id=data["nodes"][edge.producer_unique_id].activity_datapackage_id
            )
            consumer_node = bd.get_node(
                id=data["nodes"][edge.consumer_unique_id].activity_datapackage_id
            )

            dict_store["producer_node"].append(producer_node)
            dict_store["consumer_node"].append(consumer_node)
            dict_store["score"].append(
                abs(data["nodes"][edge.producer_unique_id].cumulative_score)
            )

            producer_name = producer_node.get("name", "(unnamed)")
            producer_product = producer_node.get("reference product", "")
            producer_location = producer_node.get("location", "(unknown)")
            consumer_name = consumer_node.get("name", "(unnamed)")
            consumer_location = consumer_node.get("location", "(unknown)")
            score = abs(data["nodes"][edge.producer_unique_id].cumulative_score)

            dict_view["Producer"].append(f"{producer_name} ({producer_location})")
            dict_view["Product"].append(producer_product)
            dict_view["Consumer"].append(f"{consumer_name} ({consumer_location})")
            dict_view["Score"].append(score)

    return dict_view, dict_store


def clear_variables():
    if "tlca_demand_candidates" in st.session_state:
        del st.session_state.tlca_demand_candidates
    if "tlca_demand_activity" in st.session_state:
        del st.session_state.tlca_demand_activity
    if "current_candidates" in st.session_state:
        del st.session_state.current_candidates
    if "current_demand_candidates" in st.session_state:
        del st.session_state.current_demand_candidates
    if "selected_candidate" in st.session_state:
        del st.session_state.selected_candidate
    if "selected_candidate_exchanges" in st.session_state:
        del st.session_state.selected_candidate_exchanges
    if "selected_exchange" in st.session_state:
        del st.session_state.selected_exchange
    if "manual_amounts" in st.session_state:
        del st.session_state.manual_amounts
    if "manual_dates" in st.session_state:
        del st.session_state.manual_dates
    if "st.session_state.selected_exchange_has_td" in st.session_state:
        del st.session_state.selected_exchange_has_td


st.title("Temporalize your Data")
if "current_candidates" not in st.session_state:
    st.session_state.current_candidates = []
if "current_demand_candidates" not in st.session_state:
    st.session_state.current_demand_candidates = []
if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None
if "selected_demand_candidate" not in st.session_state:
    st.session_state.selected_demand_candidate = None
if "st.session_state.selected_exchange_has_td" not in st.session_state:
    st.session_state.selected_exchange_has_td = None

tab_search, tab_calc = st.tabs(
    ["Direct Activity Selection", "Select from Contributions"]
)
with tab_search:
    col_activity_selection, col_exchange_selection = st.columns(2, gap="medium")
    with col_activity_selection:
        # Create a form for search inputs with a title and description
        with st.container(border=True):
            st.subheader("🔍 Activity Selection")

            input_db_names = list(bd.databases)
            selected_db = st.selectbox(
                "Database", options=input_db_names, key="input_db_select"
            )
            activity_name = st.text_input("Activity Name", key="activity_name")
            location = st.text_input("Location", key="location")

            # Form submit button
            if st.button("Apply Filter", use_container_width=True):
                if not selected_db:
                    st.warning("Please select an input database.")
                else:
                    with st.spinner("Filtering..."):
                        st.session_state.current_candidates = find_candidates(
                            selected_db, activity_name, location
                        )

            if len(st.session_state.current_candidates) == 0:
                st.info("No candidates to display.")
            else:
                if len(st.session_state.current_candidates) >= 100:
                    st.warning(
                        "Too many candidates to display. Please refine your search."
                    )
                else:
                    st.session_state.selected_candidate = st.selectbox(
                        "Choose Candidate", options=st.session_state.current_candidates
                    )

    with col_exchange_selection:
        with st.container(border=True):
            st.subheader("Exchange Selection")
            if "selected_candidate" in st.session_state:
                if st.session_state.selected_candidate:
                    st.session_state.selected_candidate_exchanges = list(
                        st.session_state.selected_candidate.exchanges()
                    )
                else:
                    st.session_state.selected_candidate_exchanges = []
                selected_exchange = st.selectbox(
                    "Choose Exchange",
                    options=st.session_state.selected_candidate_exchanges,
                )
                st.session_state.selected_exchange = selected_exchange

                if st.session_state.selected_exchange:
                    st.session_state.selected_exchange_has_td = (
                        st.session_state.selected_exchange.get("temporal_distribution")
                    )
                    if st.session_state.selected_exchange_has_td:

                        st.info("This Exchange carries Temporal Information.")
                        st.write(
                            st.session_state.selected_exchange["temporal_distribution"]
                        )
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(
                                "Overwrite Temporal Information",
                                type="primary",
                                key="overwrite_search",
                                use_container_width=True,
                            ):
                                add_temporal_information(
                                    st.session_state.selected_exchange
                                )
                        with col2:
                            if st.button(
                                "Remove Temporal Information",
                                key="remove_search",
                                use_container_width=True,
                            ):
                                st.session_state.selected_exchange.pop(
                                    "temporal_distribution"
                                )
                                st.session_state.selected_exchange.save()
                                st.success(
                                    "Temporal Information removed from the Exchange",
                                    icon="🗑️",
                                )
                    else:
                        st.warning("This Exchange carries no Temporal Information.")
                        if st.button(
                            "Add Temporal Information",
                            type="primary",
                            key="add_td_search",
                            use_container_width=True,
                        ):
                            add_temporal_information(st.session_state.selected_exchange)

with tab_calc:
    col_demand_selection, col_lca, col_df = st.columns([1, 1, 2])
    with col_demand_selection:
        # Create a form for search inputs with a title and description
        with st.container(border=True):
            st.subheader("🔍 Demand Selection")

            input_db_names = list(bd.databases)
            selected_db = st.selectbox(
                "Database", options=input_db_names, key="input_db_demand_select"
            )
            activity_name = st.text_input("Activity Name", key="activity_name_demand")
            location = st.text_input("Location", key="location_demand")
            if "current_demand_candidates" not in st.session_state:
                st.session_state.current_demand_candidates = []

            if st.button(
                "Apply Filter", use_container_width=True, key="apply_filter_demand"
            ):
                if not selected_db:
                    st.warning("Please select an input database.")
                else:
                    with st.spinner("Filtering..."):
                        st.session_state.current_demand_candidates = find_candidates(
                            selected_db, activity_name, location
                        )

            if len(st.session_state.current_demand_candidates) == 0:
                st.info("No candidates to display")
            else:
                if len(st.session_state.current_demand_candidates) >= 100:
                    st.warning(
                        "Too many candidates to display. Please refine your search."
                    )
                else:
                    st.session_state.selected_demand_candidate = st.selectbox(
                        "Choose Candidate",
                        options=st.session_state.current_demand_candidates,
                        key="select_demand_candidate",
                    )

    with col_lca:
        with st.container(border=True):
            st.subheader("🧮  Calculation")
            st.write(
                "Select a Method and Start the LCA and Graph Traversal Calculations to find the most important exchanges."
            )
            st.markdown(
                f"Selected Demand:`{st.session_state.selected_demand_candidate}`"
            )

            selected_method = st.selectbox("Method", options=bd.methods)
            # cutoff = st.slider("Cutoff", min_value=0.005, max_value=1.000, value=0.010, step=0.001)
            col1, col2, col3 = st.columns(3)
            with col1:
                cutoff = st.number_input(
                    "Cutoff", value=0.010, step=0.001, min_value=0.001, max_value=1.000
                )
            with col2:
                max_calc = st.number_input(
                    "Max Calc", value=1000, step=100, min_value=0, max_value=10000
                )
            with col3:
                max_depth = st.number_input(
                    "Max Depth", value=3, step=1, min_value=0, max_value=1000
                )

            calc_button_disabled = (
                not st.session_state.selected_demand_candidate or not selected_method
            )

            submitted = st.button(
                "Calculate", use_container_width=True, disabled=calc_button_disabled
            )
            if (
                submitted
                and "selected_demand_candidate" in st.session_state
                and selected_method
            ):
                with st.spinner("*Crunching the numbers...*"):
                    dict_view, dict_store = calculate(
                        st.session_state.selected_demand_candidate,
                        selected_method,
                        cutoff=cutoff,
                        max_calc=max_calc,
                        max_depth=max_depth,
                    )
                    df_view = pd.DataFrame(dict_view)
                    df_view.sort_values(by="Score", ascending=False, inplace=True)
                    st.session_state.df_view = df_view

                    df_store = pd.DataFrame(dict_store)
                    df_store.sort_values(by="score", ascending=False, inplace=True)
                    st.session_state.df_store = df_store

    with col_df:
        st.subheader("☁️ Top Contributing Exchanges")
        st.write("Pick an Exchange by Selecting the Row (click the left most column).")
        if "df_view" not in st.session_state:
            st.session_state.df_view = pd.DataFrame(
                {
                    "Score": [],
                    "Product": [],
                    "Producer": [],
                    "Consumer": [],
                }
            )
        if "df_store" not in st.session_state:
            st.session_state.df_store = pd.DataFrame(
                {
                    "producer_node": [],
                    "consumer_node": [],
                    "score": [],
                }
            )
        event = st.dataframe(
            st.session_state.df_view,
            key="df",
            selection_mode="single-row",
            on_select="rerun",
            hide_index=True,
        )
        selected_row = st.session_state.df_store.iloc[event.selection.rows]
        if not selected_row.empty:
            selected_exchange = get_exchange(
                input_node=selected_row["producer_node"].iloc[0],
                output_node=selected_row["consumer_node"].iloc[0],
            )
            st.session_state.selected_exchange = selected_exchange
            st.write(selected_exchange)
            if "selected_exchange" in st.session_state:
                if st.session_state.selected_exchange.get("temporal_distribution"):
                    st.info("This Exchange carries Temporal Information.")
                    st.write(
                        st.session_state.selected_exchange["temporal_distribution"]
                    )
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(
                            "Overwrite Temporal Information",
                            type="primary",
                            key="overwrite_calc",
                            use_container_width=True,
                        ):
                            add_temporal_information(st.session_state.selected_exchange)
                    with col2:
                        if st.button(
                            "Remove Temporal Information",
                            key="remove_search",
                            use_container_width=True,
                        ):
                            st.session_state.selected_exchange.pop(
                                "temporal_distribution"
                            )
                            st.session_state.selected_exchange.save()
                            st.success(
                                "Temporal Information removed from the Exchange",
                                icon="🗑️",
                            )

                else:
                    st.warning("This Exchange carries no Temporal Information.")
                    if st.button(
                        "Add Temporal Information",
                        type="primary",
                        key="add_td_calc",
                    ):
                        add_temporal_information(st.session_state.selected_exchange)

with st.sidebar:
    projects = [p.name for p in bd.projects]
    projects.remove(st.session_state.current_project)
    projects.insert(0, st.session_state.current_project)
    selected_project = st.selectbox("Project Selection", options=projects)
    if st.button(
        "Switch Project",
        use_container_width=True,
        type="primary",
        disabled=selected_project == bd.projects.current,
    ):
        st.session_state.current_project = selected_project
        bd.projects.set_current(selected_project)
        clear_variables()

    st.divider()
    mode = st.selectbox("Mode Selection", options=["Temporalization", "Calculation"])
    if st.button(
        "Switch Mode",
        use_container_width=True,
        type="primary",
        disabled=mode == "Temporalization",
    ):
        clear_variables()
        st.switch_page("pages/calculate.py")
