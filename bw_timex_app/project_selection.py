import os

import streamlit as st
import bw2data as bd

os.environ['BRIGHTWAY2_DIR']='/tmp/'

st.set_page_config(page_title="bw_timex_app", layout="centered", initial_sidebar_state="collapsed")

if 'current_project' not in st.session_state:
    st.session_state.current_project = None

def add_timex_getting_started_project():
    bd.projects.set_current("timex_getting_started")

    bd.Database("biosphere").write(
        {
            ("biosphere", "CO2"): {
                "type": "emission",
                "name": "CO2",
            },
        }
    )

    bd.Database("background_2020").write(
        {
            ("background_2020", "B"): {
                "name": "B",
                "location": "somewhere",
                "reference product": "B",
                "exchanges": [
                    {
                        "amount": 1,
                        "type": "production",
                        "input": ("background_2020", "B"),
                    },
                    {
                        "amount": 11,
                        "type": "biosphere",
                        "input": ("biosphere", "CO2"),
                    },
                ],
            },
        }
    )

    bd.Database("foreground").write(
        {
            ("foreground", "A"): {
                "name": "A",
                "location": "somewhere",
                "reference product": "A",
                "exchanges": [
                    {
                        "amount": 1,
                        "type": "production",
                        "input": ("foreground", "A"),
                    },
                    {
                        "amount": 3,
                        "type": "technosphere",
                        "input": ("background_2020", "B"),
                    },
                    {
                        "amount": 5,
                        "type": "biosphere",
                        "input": ("biosphere", "CO2"),
                    }
                ],
            },
        }
    )

    bd.Method(("our", "method")).write(
        [
            (("biosphere", "CO2"), 1),
        ]
    )

    bd.Database("background_2030").write(
        {
            ("background_2030", "B"): {
                "name": "B",
                "location": "somewhere",
                "reference product": "B",
                "exchanges": [
                    {
                        "amount": 1,
                        "type": "production",
                        "input": ("background_2030", "B"),
                    },
                    {
                        "amount": 7,
                        "type": "biosphere",
                        "input": ("biosphere", "CO2"),
                    },
                ],
            },
        }
    )

def add_timex_ev_example_project():
    bd.projects.set_current("timex_ev_example")
    biosphere = bd.Database("biosphere")
    biosphere.write(
        {
            ("biosphere", "CO2"): {
                "type": "emission",
                "name": "carbon dioxide",
            },
        }
    )

    background_2020 = bd.Database("background_2020")
    background_2030 = bd.Database("background_2030")
    background_2040 = bd.Database("background_2040")

    background_2020.write({})
    background_2030.write({})
    background_2040.write({})

    background_databases = [
        background_2020,
        background_2030,
        background_2040,
    ]
    
    process_co2_emissions = {
        "glider": (10, 5, 2.5), # for 2020, 2030 and 2040
        "powertrain": (20, 10, 7.5),
        "battery": (10, 5, 4),
        "electricity": (0.5, 0.25, 0.075),
        "glider_eol": (0.01, 0.0075, 0.005),
        "powertrain_eol": (0.01, 0.0075, 0.005),
        "battery_eol": (1, 0.5, 0.25),
    }

    node_co2 = biosphere.get("CO2")

    for component_name, gwis in process_co2_emissions.items():
        for database, gwi in zip(background_databases, gwis):
            database.new_node(component_name, name=component_name, location="somewhere").save()
            component = database.get(component_name)
            component["reference product"] = component_name        
            component.save()
            production_amount = -1 if "eol" in component_name else 1
            component.new_edge(input=component, amount=production_amount, type="production").save()
            component.new_edge(input=node_co2, amount=gwi, type="biosphere").save()       

    ELECTRICITY_CONSUMPTION = 0.2 # kWh/km
    MILEAGE = 150_000 # km
    LIFETIME = 15 # years

    # Overall mass: 1200 kg
    MASS_GLIDER = 840 # kg
    MASS_POWERTRAIN = 80 # kg
    MASS_BATTERY = 280 # kg
        
    if "foreground" in bd.databases:
        del bd.databases["foreground"] # to make sure we create the foreground from scratch
    foreground = bd.Database("foreground")
    foreground.register()
    
    ev_production = foreground.new_node("ev_production", name="production of an electric vehicle", unit="unit")
    ev_production['reference product'] = "electric vehicle"
    ev_production.save()

    driving = foreground.new_node("driving", name="driving an electric vehicle", unit="transport over an ev lifetime")
    driving['reference product'] = "transport"
    driving.save()

    used_ev = foreground.new_node("used_ev", name="used electric vehicle", unit="unit")
    used_ev['reference product'] = "used electric vehicle"
    used_ev.save()
    
    glider_production = background_2020.get(code="glider")
    powertrain_production = background_2020.get(code="powertrain")
    battery_production = background_2020.get(code="battery")

    ev_production.new_edge(input=ev_production, amount=1, type="production").save()

    glider_to_ev = ev_production.new_edge(
        input=glider_production,
        amount=MASS_GLIDER, 
        type="technosphere"
    )
    powertrain_to_ev = ev_production.new_edge(
        input=powertrain_production, 
        amount=MASS_POWERTRAIN, 
        type="technosphere"
    )
    battery_to_ev = ev_production.new_edge(
        input=battery_production, 
        amount=MASS_BATTERY, 
        type="technosphere"
    )

    glider_eol = background_2020.get(name="glider_eol")
    powertrain_eol = background_2020.get(name="powertrain_eol")
    battery_eol = background_2020.get(name="battery_eol")

    used_ev.new_edge(input=used_ev, amount=-1, type="production").save()  # -1 as this gets rid of a used car

    used_ev_to_glider_eol = used_ev.new_edge(
        input=glider_eol,
        amount=-MASS_GLIDER,
        type="technosphere",
    )
    used_ev_to_powertrain_eol = used_ev.new_edge(
        input=powertrain_eol,
        amount=-MASS_POWERTRAIN,
        type="technosphere",
    )
    used_ev_to_battery_eol = used_ev.new_edge(
        input=battery_eol,
        amount=-MASS_BATTERY,
        type="technosphere",
    )

    electricity_production = background_2020.get(name="electricity")

    driving.new_edge(input=driving, amount=1, type="production").save()

    driving_to_used_ev = driving.new_edge(input=used_ev, amount=-1, type="technosphere")
    ev_to_driving = driving.new_edge(
        input=ev_production, 
        amount=1, 
        type="technosphere"
    )
    electricity_to_driving = driving.new_edge(
        input=electricity_production,
        amount=ELECTRICITY_CONSUMPTION * MILEAGE,
        type="technosphere",
    )
    
    from bw_temporalis import TemporalDistribution, easy_timedelta_distribution
    import numpy as np

    td_assembly_and_delivery = TemporalDistribution(
        date=np.array([-3, -2], dtype="timedelta64[M]"), amount=np.array([0.2, 0.8])
    )

    td_glider_production = TemporalDistribution(
        date=np.array([-2, -1, 0], dtype="timedelta64[Y]"), amount=np.array([0.7, 0.1, 0.2])
    )

    td_produce_powertrain_and_battery = TemporalDistribution(
        date=np.array([-1], dtype="timedelta64[Y]"), amount=np.array([1])
    )

    td_use_phase = easy_timedelta_distribution(
        start=0,
        end=LIFETIME,
        resolution="Y",
        steps=(LIFETIME + 1),
        kind="uniform", # you can also do "normal" or "triangular" distributions
    )

    td_disassemble_used_ev = TemporalDistribution(
        date=np.array([LIFETIME + 1], dtype="timedelta64[Y]"), amount=np.array([1])
    )

    td_treating_waste = TemporalDistribution(
        date=np.array([3], dtype="timedelta64[M]"), amount=np.array([1])
    )

    glider_to_ev["temporal_distribution"] = td_glider_production
    glider_to_ev.save()

    powertrain_to_ev["temporal_distribution"] = td_produce_powertrain_and_battery
    powertrain_to_ev.save()

    battery_to_ev["temporal_distribution"] = td_produce_powertrain_and_battery
    battery_to_ev.save()

    ev_to_driving["temporal_distribution"] = td_assembly_and_delivery
    ev_to_driving.save()

    electricity_to_driving["temporal_distribution"] = td_use_phase
    electricity_to_driving.save()

    driving_to_used_ev["temporal_distribution"] = td_disassemble_used_ev
    driving_to_used_ev.save()

    used_ev_to_glider_eol["temporal_distribution"] = td_treating_waste
    used_ev_to_glider_eol.save()

    used_ev_to_powertrain_eol["temporal_distribution"] = td_treating_waste
    used_ev_to_powertrain_eol.save()

    used_ev_to_battery_eol["temporal_distribution"] = td_treating_waste
    used_ev_to_battery_eol.save()

    bd.Method(("GWP", "example")).write(
        [
            (("biosphere", "CO2"), 1),
        ]
    )
        
if "timex_getting_started" not in bd.projects:
    add_timex_getting_started_project()
if "timex_ev_example" not in bd.projects:
    add_timex_ev_example_project()

_, col, _ = st.columns([1, 2, 1])
with col:
    st.title("Select a Project")
    st.text("")
    project_names = [project.name for project in bd.projects] + ["Create New Project..."]
    selected_project = st.selectbox("Your Available Projects", options=project_names)
    
    new_project_name = None
    if selected_project == "Create New Project...":
        new_project_name = st.text_input("New Project Name")
        if st.button("Create New Project", use_container_width=True, type="primary", disabled=not new_project_name):
            bd.projects.set_current(new_project_name)
            st.switch_page("pages/mode.py")
    else:
        if st.button("Activate Selected Projet", use_container_width=True, type="primary"):
            bd.projects.set_current(selected_project)
            st.session_state.current_project = selected_project
            
            st.switch_page("pages/mode.py")