import streamlit as st

st.set_page_config(
    page_title="bw_timex_app", layout="centered", initial_sidebar_state="collapsed"
)

# st.markdown("""
#     <style>
#     a[href] {
#         text-decoration: underline;
#         color: #9c5ffd;
#     }
#     </style>
#     """, unsafe_allow_html=True)

_, col_welcome, _ = st.columns([1, 5, 1])
with col_welcome:
    st.title(" Welcome ⏳🌿")
    st.write("This is the `bw_timex` web app. Here, you can temporalize your data, calculate time-explicit LCAs and interactively investigate the results.")
    st.write("")
    st.write("To learn more about the `bw_timex` package, check out our [docs](https://docs.brightway.dev/projects/bw-timex/en/latest/). The source code for this app is availabe [on GitHub](https://github.com/TimoDiepers/bw_timex_app).")
    st.write("")
    
    if st.button("Get Started", use_container_width=True, type="primary"):
        st.switch_page("pages/project_selection.py")