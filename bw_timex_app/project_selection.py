import streamlit as st
import bw2data as bd

st.set_page_config(page_title="bw_timex_app", layout="wide", initial_sidebar_state="collapsed")

_, col_project_selection, _ = st.columns(3)
with col_project_selection:
    # Project Selection Section
    st.header("📂 Choose a Project")

    with st.form(key='project_selection_form'):
        project_names = [project.name for project in bd.projects]
        selected_project = st.selectbox("Choose a Project", options=project_names)
        submit_project = st.form_submit_button("Set Project")

        if submit_project:
            if not selected_project:
                st.warning("Please select a project.")
            else:
                bd.projects.set_current(selected_project)
                st.session_state.current_project = selected_project
                with st.spinner("Loading..."):
                    st.switch_page("pages/mode.py")