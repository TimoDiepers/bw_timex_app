import streamlit as st
import bw2data as bd
import bw2io as bi

st.set_page_config(page_title="bw_timex_app", layout="centered", initial_sidebar_state="collapsed")

if 'current_project' not in st.session_state:
    st.session_state.current_project = None

_, col, _ = st.columns([1, 2, 1])
with col:
    st.title("Select a Project")
    st.text("")
    project_names = [project.name for project in bd.projects]
    selected_project = st.selectbox("Your Available Projects", options=project_names)

    if st.button("Activate", use_container_width=True, type="primary"):
        bd.projects.set_current(selected_project)
        st.session_state.current_project = selected_project
        
        if "Mobility example" not in bd.databases:
            bi.add_example_database()
            
        st.switch_page("pages/mode.py")