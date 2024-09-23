import streamlit as st
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go

# Define nodes and links
node_labels = ["Source A", "Source B", "Process C", "Sink D", "Sink E"]
node_colors = ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99"]

source_indices = [0, 1, 0, 2, 3]
target_indices = [2, 3, 3, 4, 4]
values = [8, 4, 2, 8, 4]

# Create the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=node_labels,
        color=node_colors
    ),
    link=dict(
        source=source_indices,
        target=target_indices,
        value=values
    ))])

selected_points = plotly_events(fig)

# Check if any points were clicked
if selected_points:
    point = selected_points[0]
    link_index = point['pointNumber']
    source_node_index = source_indices[link_index]
    target_node_index = target_indices[link_index]
    source_label = node_labels[source_node_index]
    target_label = node_labels[target_node_index]
    st.write(f"You clicked on a flow from **{source_label}** to **{target_label}**.")
else:
    st.write("Click on a flow in the Sankey diagram to see details.")
