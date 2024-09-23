import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import numpy as np
import bw2data as bd

from datetime import datetime, timedelta
from bw2data.backends import ActivityDataset as AD
from bw2data.subclass_mapping import NODE_PROCESS_CLASS_MAPPING
from bw_temporalis import TemporalDistribution
from bw_temporalis.utils import easy_timedelta_distribution
from bw_timex.utils import add_temporal_distribution_to_exchange

# Initialize Streamlit App
st.set_page_config(page_title="bw_timex_app", layout="wide")

st.markdown(
    body="""
        <style>
            .block-container{
                    padding-top: 25px;
                }
        </style>
    """, 
    unsafe_allow_html=True
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

@st.dialog("Adding Temporal Information", width="large")
def add_temporal_information(selected_exchange):
    st.write(selected_exchange)
    col_input, col_graph = st.columns([1, 2])

    with col_input:
        # Initialize list to store points
        if 'x_points' not in st.session_state:
            st.session_state.x_points = []
        if 'y_points' not in st.session_state:
            st.session_state.y_points = []

        selected_time_resolution_label = st.selectbox("Time Resolution", options=["Years", "Months", "Days", "Hours"])
        selected_time_resolution = RESOLUTION_LABELS[selected_time_resolution_label]
        
        distribution_type = st.selectbox("Distribution Type", options=["uniform", "triangular", "normal"]) #, "manual"
        
        # if distribution_type == "manual":
        #     x_value = st.number_input("Amount", value=0.0, max_value=1)
        #     y_value = st.number_input(f"Timedelta [{selected_time_resolution_label}]", value=0.0)

        #     # Add the point when the button is clicked
        #     if st.button("Add Point"):
        #         st.session_state.points.append((x_value, y_value))
                
        if distribution_type:
            col_start, col_end = st.columns(2)
            with col_start:
                start = st.number_input("Start", value=0)
            with col_end:
                end = st.number_input("End", value=10)
            steps = st.slider("Steps", min_value=3, max_value=end+1, value=end+1)
        
        if distribution_type == "uniform":
            td = easy_timedelta_distribution(
                start=start,
                end=end,
                resolution=selected_time_resolution,
                steps=steps,
                kind="uniform",
            )
            
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
            
        if distribution_type == "normal":
            param = st.slider("Standard Deviation", min_value=0.001, max_value=3.0, value=0.5)
            td = easy_timedelta_distribution(
                start=start,
                end=end,
                resolution=selected_time_resolution,
                steps=steps,
                kind=distribution_type,
                param=param,
            )

        td_df = pd.DataFrame({'date': td.date, 'amount': td.amount})
        
        # Handle years manually (approximate a year as 365.25 days)
        if selected_time_resolution == "Y":
            td_df['date_converted'] = td_df['date'] / np.timedelta64(1, 'D') / 365.25
        elif selected_time_resolution == "M":
            td_df['date_converted'] = td_df['date'] / np.timedelta64(1, 'D') / 30.4375
        else:
            # Conversion factors for other units
            conversion_factor = {
                "D": np.timedelta64(1, 'D'),
                "h": np.timedelta64(1, 'h'),
            }

            # Convert timedelta64 to the chosen unit as floats
            td_df['date_converted'] = td_df['date'] / conversion_factor[selected_time_resolution]
            
        if st.button("Add to Exchange", use_container_width=True, type="primary"):
            selected_exchange["temporal_distribution"] = td
            selected_exchange.save()
            st.rerun()
            
    with col_graph:
        if 'td_df' in st.session_state:
            # Create a scatter plot
            fig = px.scatter(td_df, x='date_converted', y='amount', 
                            labels={'date_converted': f'Timedelta ({selected_time_resolution_label})', 'amount': 'Amount'})
            # Display the plot in Streamlit
            st.plotly_chart(fig)
        
def node_class(database_name):
    backend = bd.databases[database_name].get("backend", "sqlite")
    return NODE_PROCESS_CLASS_MAPPING.get(backend, NODE_PROCESS_CLASS_MAPPING["sqlite"])

def update_node_search_results():
    selected_db = st.session_state.input_db_select
    activity_name = st.session_state.activity_name
    location = st.session_state.location

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
    if selected_db:
        qs = qs.where(mapping["database"] == selected_db)
    if activity_name:
        qs = qs.where(mapping["name"].contains(activity_name))
    if location:
        qs = qs.where(mapping["location"].contains(location))

    # Retrieve candidates based on the filtered query
    candidates = [node_class(obj.database)(obj) for obj in qs]

    # Update the candidates selectbox
    st.session_state.filtered_candidates = candidates

    
# Initialize session state variables
if "current_project" not in st.session_state:
    st.session_state.current_project = None
if "filtered_candidates" not in st.session_state:
    st.session_state.filtered_candidates = []


_, col_project_selection, _ = st.columns(3)
with col_project_selection:
    # Project Selection Section
    if not st.session_state.current_project:
        st.title("📂 Select a Project")

        with st.form(key='project_selection_form'):
            project_names = [project.name for project in bd.projects]
            selected_project = st.selectbox("Choose a Project", options=project_names)

            submit_project = st.form_submit_button("Set Project")

            if submit_project:
                if not selected_project:
                    st.warning("Please select a project.")
                else:
                    bd.projects.set_current(selected_project)
                    st.session_state.current_project = selected_project
                    st.rerun()

if st.session_state.current_project:
    st.title("Temporalize your LCA model")
    tab_search, tab_sankey = st.tabs(["Select from Search", "Select from Sankey"])
    with tab_search:
            col_activity_selection, col_exchange_selection = st.columns(2, gap="medium")

            with col_activity_selection:
                # Create a form for search inputs with a title and description
                with st.form(key='search_form'):
                    st.header("🔍 Search for Activities")
                    st.write("Enter the criteria below to find activities in the database. You can press **Enter** after filling any field to update the results.")

                    input_db_names = list(bd.databases)
                    st.selectbox("Select Input Database", options=input_db_names, key="input_db_select")
                    st.text_input("Activity Name", key="activity_name")
                    st.text_input("Location", key="location")

                    # Form submit button
                    submitted = st.form_submit_button("Search")

                    if submitted:
                        if not st.session_state.input_db_select:
                            st.warning("Please select an input database.")
                        else:
                            with st.spinner("Searching..."):
                                update_node_search_results()
                                if not st.session_state.filtered_candidates:
                                    st.warning("No candidates found matching the search criteria.")
                                else:
                                    st.success(f"Found {len(st.session_state.filtered_candidates)} candidates.")

            with col_exchange_selection:
                # Display Candidates with Pagination
                st.subheader("Available Candidates")

                if st.session_state.filtered_candidates:
                    # Display the selectbox with current page candidates
                    selected_candidate = st.selectbox("Choose Candidate", options=st.session_state.filtered_candidates)
                else:
                    st.info("No candidates to display. Please perform a search.")

                if 'selected_candidate' in locals() and selected_candidate:
                    selected_candidate_exchanges = list(selected_candidate.exchanges())
                    selected_exchange = st.selectbox("Choose Exchange", options=selected_candidate_exchanges)
                    st.session_state.selected_exchange = selected_exchange

                if 'selected_exchange' in locals() and selected_exchange:
                    if selected_exchange.get("temporal_distribution"):
                        st.info("This exchange carries Temporal Information.")
                        selected_exchange["temporal_distribution"]
                        
                        if st.button("Overwrite Temporal Information", type="primary"):
                            add_temporal_information(selected_exchange)
                            
                        if st.button("Remove Temporal Information"):
                            selected_exchange.pop("temporal_distribution")
                            selected_exchange.save()
                            st.success("Temporal Information removed from the Exchange", icon="🗑️")
                    else:
                        st.warning("This exchange carries no Temporal Information.")
                        if st.button("Add Temporal Information", type="primary"):
                            add_temporal_information(selected_exchange)

    with tab_sankey:
        st.write("Sankey Tab")