import os

import streamlit as st
import bw2data as bd
import bw2io as bi

os.environ['BRIGHTWAY2_DIR']='/tmp/'

st.set_page_config(page_title="bw_timex_app", layout="centered", initial_sidebar_state="collapsed")

if 'current_project' not in st.session_state:
    st.session_state.current_project = None

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
            if "Mobility example" not in bd.databases:
                bi.add_example_database()
            st.switch_page("pages/mode.py")
    else:
        if st.button("Activate Selected Projet", use_container_width=True, type="primary"):
            bd.projects.set_current(selected_project)
            st.session_state.current_project = selected_project
            # if "Mobility example" not in bd.databases:
            #     bi.add_example_database()
            st.switch_page("pages/mode.py")