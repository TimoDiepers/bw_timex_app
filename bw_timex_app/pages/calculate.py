import streamlit as st
import pandas as pd
import bw2data as bd
from datetime import datetime
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
        
@st.fragment
def show_results():
    tlca = st.session_state.tlca
    st.write("Static score: ", tlca.static_score)

    from dynamic_characterization.ipcc_ar6 import characterize_co2
    emission_id = bd.get_node(code="CO2").id

    characterization_function_dict = {
        emission_id: characterize_co2,
    }

    def plot_characterized_inventory(tlca):
        from bw_timex.utils import resolve_temporalized_node_name
        # Prepare the plot data
        metric_ylabels = {
            "radiative_forcing": "radiative forcing [W/m²]",
            "GWP": f"GWP{tlca.current_time_horizon} [kg CO₂-eq]",
        }

        plot_data = tlca.characterized_inventory.copy()

        # Sum emissions within activities
        plot_data = plot_data.groupby(["date", "activity"]).sum().reset_index()
        plot_data["amount_sum"] = plot_data["amount"].cumsum()

        # Create a mapping for activity names
        activity_name_cache = {}
        for activity in plot_data["activity"].unique():
            if activity not in activity_name_cache:
                activity_name_cache[activity] = resolve_temporalized_node_name(
                    tlca.activity_time_mapping_dict_reversed[activity][0][1]
                )
        plot_data["activity_label"] = plot_data["activity"].map(activity_name_cache)

        # Create a wide-form DataFrame suitable for st.scatter_chart
        # We'll pivot the table so each activity is a separate column
        plot_data_wide = plot_data.pivot(index="date", columns="activity_label", values="amount")

        # Plot using Streamlit's st.scatter_chart
        st.scatter_chart(plot_data_wide, x_label="time", y_label=metric_ylabels[tlca.current_metric], size=40)

    col_th_rf, col_th_rf_f = st.columns([4, 1])
    with col_th_rf:
        time_horizon_rf = st.slider("Time Horizon for Radiative Forcing", min_value=2, max_value=1000, value=100, step=1)
    with col_th_rf_f:
        fixed_th_rf = st.checkbox("Fixed", value=False, key="fixed_checkbox_rf")
    tlca.dynamic_lcia(
        metric="radiative_forcing",
        time_horizon=time_horizon_rf,
        fixed_time_horizon=fixed_th_rf,
        characterization_function_dict=characterization_function_dict,
    )
    plot_characterized_inventory(tlca)
    
    col_th_gwp, col_th_gwp_f = st.columns([4, 1])
    with col_th_gwp:
        time_horizon_gwp = st.slider("Time Horizon for GWP", min_value=2, max_value=1000, value=100, step=1)
    with col_th_gwp_f:
        fixed_th_gwp = st.checkbox("Fixed", value=False, key="fixed_checkbox_gwp")
    tlca.dynamic_lcia(
        metric="GWP",
        time_horizon=time_horizon_gwp,
        fixed_time_horizon=fixed_th_gwp,
        characterization_function_dict=characterization_function_dict,
    )

    plot_characterized_inventory(tlca)
        
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

    # selected_dbs = st.multiselect("Databases to use", options=list(bd.databases))
    
    data = {
        'Database': [],
        'Representative Date': [],
    }
    df = pd.DataFrame(data)
    df["Database"] = df["Database"].astype(str)
    df["Representative Date"] = df["Representative Date"].astype(str)
    
    st.write("")
    st.write("*Assign representative dates to databases. Use a format like `2024-09-26' for temporally fixed and 'dynamic' for temporally distributed databases.*")
    editor = st.data_editor(
        df,
        column_config={
            'Database': st.column_config.SelectboxColumn(options=bd.databases),
            'Representative Date': st.column_config.TextColumn()
        },
        num_rows="dynamic",  # Allow dynamic rows
        use_container_width=True,
        hide_index=True,
    )
    
    # for db in selected_dbs:
    #     st.date_input(f"Representative Date for '{db}'", key=f"start_date_{db}")
    calculated = False
    if st.button("Calculate", use_container_width=True, type="primary", disabled=st.session_state.tlca_demand_activity is None):
        from bw_timex import TimexLCA
        def custom_convert_to_datetime(x):
            if x == 'dynamic':
                return x
            else:
                return datetime.strptime(x, "%Y-%m-%d")
        database_date_dict = dict(zip(editor['Database'], editor['Representative Date'].apply(custom_convert_to_datetime)))
        tlca = TimexLCA(
            demand={st.session_state.tlca_demand_activity: amount},
            method=selected_method,
            database_date_dict=database_date_dict,
        )

        timeline = tlca.build_timeline()
        st.dataframe(timeline)

        tlca.lci()
        tlca.static_lcia()
        st.session_state.tlca = tlca
        calculated = True
        
if calculated:
    show_results()        
        
with st.sidebar:
    if st.button("Calculate TimexLCAs", use_container_width=True, type="primary"):
        st.switch_page("pages/mode.py")
    if st.button("Select a different Project", use_container_width=True):
        st.switch_page("project_selection.py")