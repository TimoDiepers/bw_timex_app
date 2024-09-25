import streamlit as st

import bw2data as bd
from bw2data.backends import ActivityDataset as AD
from bw2data.subclass_mapping import NODE_PROCESS_CLASS_MAPPING
from bw_timex import TimexLCA

st.set_page_config(page_title="bw_timex_app", layout="centered", initial_sidebar_state='collapsed')

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

if "current_project" not in st.session_state:
    st.switch_page("project_selection.py")

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

def node_class(database_name):
    backend = bd.databases[database_name].get("backend", "sqlite")
    return NODE_PROCESS_CLASS_MAPPING.get(backend, NODE_PROCESS_CLASS_MAPPING["sqlite"])

@st.dialog("Select a Demand Activity")
def select_demand_activity():
    input_db_names = list(bd.databases)
    selected_db = st.selectbox(
        "Database", options=input_db_names, key="input_db_demand_select"
    )
    activity_name = st.text_input(
        "Activity Name", key="activity_name_demand"
    )
    location = st.text_input("Location", key="location_demand")
    
    demand_choice = None
    
    if st.button("Apply Filter", use_container_width=True):
        st.session_state.tlca_demand_candidates = (
            find_candidates(selected_db, activity_name, location)
        )
        if len(st.session_state.tlca_demand_candidates) == 0:
            st.warning(
                "No candidates found matching the search criteria."
            )
        elif len(st.session_state.tlca_demand_candidates) == 1:
            st.success("Found 1 candidate.")
        else:
            st.success(
                f"Found {len(st.session_state.tlca_demand_candidates)} candidates."
            )
            
    demand_choice = st.selectbox(
        "Available Candidates", options=st.session_state.tlca_demand_candidates
    )
        
    if st.button("Select", use_container_width=True, type="primary", disabled=demand_choice is None):
        # st.toast(f"Selected {st.session_state.tlca_demand_activity}", icon="🎉")
        st.session_state.tlca_demand_activity = demand_choice
        st.rerun()
        
st.title("Calculate TimexLCAs")
        
if "tlca_demand_candidates" not in st.session_state:
    st.session_state.tlca_demand_candidates = []

if "tlca_demand_activity" not in st.session_state:
    st.session_state.tlca_demand_activity = None

with st.container(border=True):
    st.subheader("Calculation Setup")
    col_activity, col_change = st.columns([3, 1], vertical_alignment="center")
    
    with col_activity:
        activity_display = st.session_state.get('tlca_demand_activity', 'None')
        st.markdown(f"Selected Demand Activity: **`{activity_display}`**")
    
    with col_change:
        activity_label = "Change" if st.session_state.get('tlca_demand_activity') else "Search Activities"
        if st.button(activity_label, use_container_width=True):
            select_demand_activity()

    col_amt, col_method = st.columns(2)
    with col_amt:
        amount = st.number_input("Demand Amount", key="demand_amount", min_value=0.0, value=1.0, step=0.1)
    with col_method:
        selected_method = st.selectbox("Method", options=getattr(bd, 'methods', []))

    selected_dbs = st.multiselect("Databases to use", options=list(bd.databases))
    for db in selected_dbs:
        st.write(f"- {db}")
    if st.button("Calculate", use_container_width=True, type="primary", disabled=st.session_state.tlca_demand_activity is None):
        st.write("Calculating...")
            