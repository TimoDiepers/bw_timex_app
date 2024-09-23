import streamlit as st
import plotly.graph_objects as go

data = {'nodes': [{'direct_emissions_score_normalized': 0.018097400785529915,
   'direct_emissions_score': 0.06782749599240928,
   'cumulative_score': 3.7479136808774136,
   'cumulative_score_normalized': 0.999999999999999,
   'product': 'transport, passenger car, large size, diesel, EURO 5',
   'location': 'RoW',
   'id': 0,
   'database_id': 19434,
   'database': 'ecoinvent-3.10-cutoff',
   'class': 'demand',
   'name': 'transport, passenger car, large size, diesel, EURO 5',
   'label': 'transport, passenger\nRoW\n1.81%',
   'tooltip': '\n                <b>transport, passenger car, large size, diesel, EURO 5</b>\n                <br>Individual impact: 0.068 kg CO2-eq (1.81%)\n                <br>Cumulative impact: 3.748 kg CO2-eq (100.0%)\n            '},
  {'direct_emissions_score_normalized': 0.0,
   'direct_emissions_score': 0.0,
   'cumulative_score': 2.7701496249952977,
   'cumulative_score_normalized': 0.7391177761454696,
   'product': 'passenger car, diesel',
   'location': 'GLO',
   'id': 1,
   'database_id': 5307,
   'database': 'ecoinvent-3.10-cutoff',
   'class': 'market',
   'name': 'market for passenger car, diesel',
   'label': 'market for passenger\nGLO\n0.0%',
   'tooltip': '\n                <b>market for passenger car, diesel</b>\n                <br>Individual impact: 0.0 kg CO2-eq (0.0%)\n                <br>Cumulative impact: 2.77 kg CO2-eq (73.91%)\n            '},
  {'direct_emissions_score_normalized': 0.0,
   'direct_emissions_score': 0.0,
   'cumulative_score': 0.06882416741330609,
   'cumulative_score_normalized': 0.018363327780055432,
   'product': 'passenger car maintenance',
   'location': 'GLO',
   'id': 2,
   'database_id': 9687,
   'database': 'ecoinvent-3.10-cutoff',
   'class': 'market',
   'name': 'market for passenger car maintenance',
   'label': 'market for passenger\nGLO\n0.0%',
   'tooltip': '\n                <b>market for passenger car maintenance</b>\n                <br>Individual impact: 0.0 kg CO2-eq (0.0%)\n                <br>Cumulative impact: 0.069 kg CO2-eq (1.84%)\n            '},
  {'direct_emissions_score_normalized': 0.0,
   'direct_emissions_score': 0.0,
   'cumulative_score': 0.2517002613595501,
   'cumulative_score_normalized': 0.06715743285224889,
   'product': 'diesel, low-sulfur',
   'location': 'RoW',
   'id': 3,
   'database_id': 13043,
   'database': 'ecoinvent-3.10-cutoff',
   'class': 'market',
   'name': 'market for diesel, low-sulfur',
   'label': 'market for diesel, l\nRoW\n0.0%',
   'tooltip': '\n                <b>market for diesel, low-sulfur</b>\n                <br>Individual impact: 0.0 kg CO2-eq (0.0%)\n                <br>Cumulative impact: 0.252 kg CO2-eq (6.72%)\n            '},
  {'direct_emissions_score_normalized': 0.0,
   'direct_emissions_score': 0.0,
   'cumulative_score': 0.1635300888531663,
   'cumulative_score_normalized': 0.043632298600559706,
   'product': 'road',
   'location': 'GLO',
   'id': 4,
   'database_id': 16134,
   'database': 'ecoinvent-3.10-cutoff',
   'class': 'market',
   'name': 'market for road',
   'label': 'market for road\nGLO\n0.0%',
   'tooltip': '\n                <b>market for road</b>\n                <br>Individual impact: 0.0 kg CO2-eq (0.0%)\n                <br>Cumulative impact: 0.164 kg CO2-eq (4.36%)\n            '},
  {'direct_emissions_score_normalized': 0.0,
   'direct_emissions_score': 0.0,
   'cumulative_score': 0.36329068257603353,
   'cumulative_score_normalized': 0.09693144333329048,
   'product': 'brake wear emissions, passenger car',
   'location': 'GLO',
   'id': 5,
   'database_id': 20730,
   'database': 'ecoinvent-3.10-cutoff',
   'class': 'market',
   'name': 'market for brake wear emissions, passenger car',
   'label': 'market for brake wea\nGLO\n0.0%',
   'tooltip': '\n                <b>market for brake wear emissions, passenger car</b>\n                <br>Individual impact: 0.0 kg CO2-eq (0.0%)\n                <br>Cumulative impact: 0.363 kg CO2-eq (9.69%)\n            '}],
 'edges': [{'source_id': 1,
   'target_id': 0,
   'amount': 0.013333333656191826,
   'weight': 29.564711045818783,
   'label': '2.77 kg CO2-eq',
   'class': 'impact',
   'tooltip': '<b>2.77 kg CO2-eq</b> (0.013 kilogram)'},
  {'source_id': 2,
   'target_id': 0,
   'amount': 1.075268846761901e-05,
   'weight': 0.7345331112022173,
   'label': '0.069 kg CO2-eq',
   'class': 'impact',
   'tooltip': '<b>0.069 kg CO2-eq</b> (1.1e-05 unit)'},
  {'source_id': 3,
   'target_id': 0,
   'amount': 0.058591749519109726,
   'weight': 2.6862973140899555,
   'label': '0.252 kg CO2-eq',
   'class': 'impact',
   'tooltip': '<b>0.252 kg CO2-eq</b> (0.059 kilogram)'},
  {'source_id': 4,
   'target_id': 0,
   'amount': 0.0011261963518336415,
   'weight': 1.7452919440223882,
   'label': '0.164 kg CO2-eq',
   'class': 'impact',
   'tooltip': '<b>0.164 kg CO2-eq</b> (0.0011 meter-year)'},
  {'source_id': 5,
   'target_id': 0,
   'amount': -9.332539775641635e-06,
   'weight': 3.8772577333316196,
   'label': '0.363 kg CO2-eq',
   'class': 'impact',
   'tooltip': '<b>0.363 kg CO2-eq</b> (-9.3e-06 kilogram)'}],
 'title': 'Sankey graph result'}

# Step 4: Extract Nodes and Build Mappings
node_labels = []
id_to_index = {}

for index, node in enumerate(data['nodes']):
    node_id = node['id']
    label = node['label']
    node_labels.append(label)
    id_to_index[node_id] = index

# Step 5: Extract Links
source = []
target = []
value = []
link_labels = []

for edge in data['edges']:
    src_id = edge['source_id']
    tgt_id = edge['target_id']
    val = edge['weight']
    label = edge['label']

    # Map node IDs to indices
    src_index = id_to_index[src_id]
    tgt_index = id_to_index[tgt_id]

    source.append(src_index)
    target.append(tgt_index)
    value.append(val)
    link_labels.append(label)

# Step 6: Create the Sankey Diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color='black', width=0.5),
        label=node_labels,
        # color='blue',
        hovertemplate='%{label}<extra></extra>'
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        label=link_labels,
        hovertemplate='Value: %{value}<br />%{label}<extra></extra>'
    )
)])

fig.update_layout(title_text=data.get('title', 'Sankey Diagram'), font_size=10)

st.plotly_chart(fig)