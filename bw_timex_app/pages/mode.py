import streamlit as st

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
    if st.button("Calculate TimexLCAs", use_container_width=True, type="primary"):
        st.switch_page("pages/mode.py")
    if st.button("Select a different Project", use_container_width=True):
        st.switch_page("project_selection.py")