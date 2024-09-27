import streamlit as st
import bw2data as bd

st.set_page_config(page_title="bw_timex_app", layout="centered", initial_sidebar_state='collapsed')

if "current_project" not in st.session_state:
    st.switch_page("project_selection.py")

_, col, _ = st.columns([1, 2, 1])
with col:
    st.title("What to do?")
    st.text("")
    if st.button("Calculate TimexLCAs", use_container_width=True):
        st.switch_page("pages/calculate.py")
    if st.button("Temporalize Data", use_container_width=True):
        st.switch_page("pages/temporalize.py")

with st.sidebar:
    projects = [p.name for p in bd.projects]
    projects.remove(st.session_state.current_project)
    projects.insert(0, st.session_state.current_project)
    selected_project = st.selectbox("Project Selection", options=projects)
    if st.button("Switch Project", use_container_width=True, type="primary", disabled=selected_project == bd.projects.current):
        st.session_state.current_project = selected_project
        if "tlca_demand_candidates" in st.session_state:
            del st.session_state.tlca_demand_candidates
        if "tlca_demand_activity" in st.session_state:
            del st.session_state.tlca_demand_activity
        st.rerun()