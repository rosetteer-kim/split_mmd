import streamlit as st

test_split_page = st.Page("streamlit_pages/test_split.py", title="분리 테스트", icon=":material/content_cut:")
test_mathpixAPI_page = st.Page("streamlit_pages/test_mathpixAPI.py", title="Mathpix API(PDF) 테스트", icon=":material/content_cut:")

pg = st.navigation([test_split_page, test_mathpixAPI_page])
pg.run()