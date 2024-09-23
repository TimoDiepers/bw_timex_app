import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import bw2data as bd
from bw_temporalis import TemporalDistribution
from bw_timex.utils import add_temporal_distribution_to_exchange
from bw2data.backends import ActivityDataset as AD
from bw2data.subclass_mapping import NODE_PROCESS_CLASS_MAPPING

def node_class(database_name):
    return NODE_PROCESS_CLASS_MAPPING[bd.databases[database_name].get("backend", "sqlite")]

# Set the current project
bd.projects.set_current("timex")

input_db_names = list(bd.databases)

# Main search fields
selected_db = st.selectbox("Select Input Database", options=input_db_names, key="input_db_select")
search_query = st.text_input("Search")


# Collapsible section for advanced search
with st.expander("Advanced Search Options"):
    activity_name = st.text_input("Activity Name")
    location = st.text_input("Location")

# Button to trigger search
if selected_db and search_query:
    search_results = bd.Database(selected_db).search(search_query)
    if search_results:
        selected_input = st.selectbox(
            "Select Input Node",
            options=search_results,
            format_func=lambda node: f"{node['database']}, {node['name']}, {node['location']})",
            key="input_node_select"
        )
    else:
        st.warning("No input nodes found. Please refine your search.")

if selected_db and activity_name and location:
    node = bd.get_node(database=selected_db, name=activity_name, location=location)
    if node:
        selected_input = st.selectbox(
            "Select Input Node",
            options=[node],
            format_func=lambda node: f"{node['name']}, {node['location']} ({node['database']})",
            key="input_node_select"
        )

# with col1:
#     st.subheader("Input Node")

#     # Let user select database
#     input_db_names = list(bd.databases)
#     selected_input_db = st.selectbox("Select Input Database", options=input_db_names, key="input_db_select")

#     input_search_query = st.text_input("Search for Input Node", key="input_search")
#     input_node = None

#     if input_search_query and selected_input_db:
#         # Search the selected database
#         input_db = bd.Database(selected_input_db)
#         input_search_results = input_db.search(input_search_query)
#         if input_search_results:
#             # Display search results
#             input_node_options = input_search_results
#             selected_input = st.selectbox(
#                 "Select Input Node",
#                 options=input_node_options,
#                 format_func=lambda x: f"{x['name']} ({x['database']}, {x['code']})",
#                 key="input_node_select"
#             )
#             input_node = selected_input
#         else:
#             st.warning("No input nodes found. Please refine your search or enter details manually.")
#     else:
#         st.info("Please select a database and enter a search query.")

#     # Alternatively, allow users to enter input node details manually
#     st.write("Or enter Input Node details manually:")
#     input_code = st.text_input("Input Code", key="input_code")
#     input_database = st.text_input("Input Database", key="input_database")


# # Prepare exchange keyword arguments
# exchange_kwargs = {}
# if input_node:
#     exchange_kwargs['input_node'] = input_node
# elif input_code and input_database:
#     exchange_kwargs['input_code'] = input_code
#     exchange_kwargs['input_database'] = input_database
# else:
#     st.error("Please specify the input node either by selecting from search results or by entering code and database.")

# if output_node:
#     exchange_kwargs['output_node'] = output_node
# elif output_code and output_database:
#     exchange_kwargs['output_code'] = output_code
#     exchange_kwargs['output_database'] = output_database
# else:
#     st.error("Please specify the output node either by selecting from search results or by entering code and database.")

# st.header("Input Temporal Distribution Data")

# st.write("Enter the time deltas or absolute dates and corresponding amounts in the table below.")

# # Initialize an empty DataFrame
# if 'df' not in st.session_state:
#     st.session_state.df = pd.DataFrame({
#         'Time Type': ['Delta'],
#         'Resolution': ['year'],
#         'Value': [2],
#         'Amount': [0.6]
#     })

# # Display the DataFrame editor using the standard data_editor
# df = st.data_editor(
#     st.session_state.df,
#     num_rows="dynamic",
#     use_container_width=True,
#     hide_index=True,
#     column_config={
#         "Time Type": st.column_config.SelectboxColumn(
#             "Time Type",
#             options=["Delta", "Absolute"],
#         ),
#         "Resolution": st.column_config.SelectboxColumn(
#             "Resolution",
#             options=["year", "month", "day", "hour"],
#         ),
#         "Value": st.column_config.TextColumn("Value"),
#         "Amount": st.column_config.NumberColumn("Amount"),
#     }
# )

# # Update session state
# st.session_state.df = df

# def create_temporal_distribution(df):
#     dates = []
#     amounts = []
#     for _, row in df.iterrows():
#         time_type = row['Time Type']
#         value = row['Value']
#         amount = row['Amount']
#         if time_type == 'Delta':
#             resolution = row['Resolution']
#             if resolution == 'year':
#                 delta = np.timedelta64(int(value), 'Y')
#             elif resolution == 'month':
#                 delta = np.timedelta64(int(value), 'M')
#             elif resolution == 'day':
#                 delta = np.timedelta64(int(value), 'D')
#             elif resolution == 'hour':
#                 delta = np.timedelta64(int(value), 'h')
#             dates.append(delta)
#         elif time_type == 'Absolute':
#             try:
#                 absolute_time = np.datetime64(value)
#                 dates.append(absolute_time)
#             except:
#                 raise ValueError(f"Invalid datetime format: {value}")
#         amounts.append(float(amount))
#     return TemporalDistribution(date=np.array(dates), amount=np.array(amounts))

# if st.button("Add Temporal Distribution to Exchange"):
#     try:
#         # Validate exchange keyword arguments
#         if not exchange_kwargs:
#             st.error("Exchange information is incomplete.")
#             st.stop()

#         # Create the TemporalDistribution object
#         temporal_distribution = create_temporal_distribution(df)

#         # Add the temporal distribution to the exchange
#         add_temporal_distribution_to_exchange(
#             temporal_distribution=temporal_distribution,
#             **exchange_kwargs
#         )

#         st.success("Temporal distribution added to the exchange successfully!")
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
