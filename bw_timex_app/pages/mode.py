import streamlit as st

st.set_page_config(page_title="bw_timex_app", layout="centered", initial_sidebar_state='collapsed')

st.title("What do you want to do?")

st.text("")
st.text("")

_, col1, col2, _ = st.columns([1, 3, 3, 1])

with col1:
    if st.button("⏳ Temporalize Exchanges", use_container_width=True):
        st.switch_page("pages/exchange_selection.py")
with col2:
    if st.button("🧮 Calculate LCAs", use_container_width=True):
        st.switch_page("pages/sankey.py")