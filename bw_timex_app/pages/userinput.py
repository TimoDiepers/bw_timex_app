import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from bw_temporalis.utils import easy_timedelta_distribution

RESOLUTION_LABELS = {
    "Years": "Y",
    "Months": "M",
    "Weeks": "W",
    "Days": "D",
    "Hours": "h",
    "Minutes": "m",
    "Seconds": "s",
}

st.session_state.selected_exchange

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
        start = st.number_input("Start", value=0)
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
        
    st.session_state.td_df = td_df
    
    added = False
    if st.button("Add this TemporalDistribution", use_container_width=True):
        st.session_state.selected_exchange["temporal_distribution"] = td
        st.session_state.selected_exchange.save()
        added = True
        
    if added:
        st.success("TemporalDistribution added to the Exchange", icon="🎉")
    st.page_link("exchange_selection.py", label="Go Back and Select Another Activity", icon="↪️")  

with col_graph:
    if 'td_df' in st.session_state:
        # Create a scatter plot
        fig = px.scatter(td_df, x='date_converted', y='amount', 
                        labels={'date_converted': f'Timedelta ({selected_time_resolution_label})', 'amount': 'Amount'})
        # Display the plot in Streamlit
        st.plotly_chart(fig)