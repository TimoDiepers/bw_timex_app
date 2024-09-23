import panel as pn
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DataTable, TableColumn, PointDrawTool
from bokeh.io import curdoc

# Initialize Panel extension with a dark theme
pn.extension(sizing_mode='stretch_width', theme='dark')

# Apply a dark theme to the Bokeh document
curdoc().theme = 'dark_minimal'

# Initialize data source
data = {'x': [], 'y': []}
source = ColumnDataSource(data=data)

# Create a Bokeh figure
p = figure(
    x_range=(2000, 2050),
    y_range=(0, 1),
    title="Interactive Amount over Time",
    x_axis_label='Time',
    y_axis_label='Amount',
    tools=[],  # Start with no tools
    height=400
)

# Add scatter and line glyphs
renderer = p.scatter('x', 'y', source=source, size=10, color='white')
line = p.line('x', 'y', source=source, line_width=2, color='white')

# Add PointDrawTool
draw_tool = PointDrawTool(renderers=[renderer], add=True)
p.add_tools(draw_tool)
p.toolbar.active_tap = draw_tool  # Set the PointDrawTool as the active tap tool

# Flag to prevent recursive callback calls
updating = False

# Create a checkbox to enable/disable rescaling
rescale_checkbox = pn.widgets.Checkbox(name='Rescale Y-values to Sum to 1', value=True)

# Rescale y-values and sort data whenever the data source changes
def rescale_and_sort(attr, old, new):
    global updating
    if updating:
        return  # Skip the callback if we're already updating

    updating = True  # Set the flag to prevent recursion

    x_values = new['x']
    y_values = new['y']

    # Sort the data by x_values
    sorted_pairs = sorted(zip(x_values, y_values))
    if sorted_pairs:
        sorted_x, sorted_y = zip(*sorted_pairs)
    else:
        sorted_x, sorted_y = [], []

    # Rescale y-values if the checkbox is checked
    if rescale_checkbox.value:
        total_y = sum(sorted_y)
        if total_y == 0:
            # Avoid division by zero
            scaled_y = sorted_y
        else:
            scaled_y = [y / total_y for y in sorted_y]
    else:
        scaled_y = sorted_y

    # Update the data source
    new_data = {'x': list(sorted_x), 'y': list(scaled_y)}
    source.data = new_data

    updating = False  # Reset the flag

# Attach the callback to the data source
source.on_change('data', rescale_and_sort)

# Create a data table to display data points
columns = [
    TableColumn(field='x', title='Time'),
    TableColumn(field='y', title='Amount')
]
data_table = DataTable(source=source, columns=columns, width=400, height=280)

# Create a reset button
reset_button = pn.widgets.Button(name='Reset Data', button_type='danger', width=200)

# Define the reset callback
def reset_callback(event):
    global updating
    updating = True  # Set the flag to prevent recursion
    source.data = {'x': [], 'y': []}
    updating = False  # Reset the flag

reset_button.on_click(reset_callback)

# Create a Panel layout
layout = pn.Column(
    pn.Row(
        p,
        pn.Column(
            pn.pane.Markdown("### Data Points"),
            data_table,
            rescale_checkbox,
            reset_button
        )
    )
)

# Use Dark Theme Template
template = pn.template.FastListTemplate(title="Interactive Amount over Time", theme=pn.template.DarkTheme)
template.main.append(layout)

# Serve the app
template.servable()
