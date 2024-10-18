import streamlit as st

pdf_typeA_page = st.Page("pages/pdf_typeA_page.py", title="PDF Type A", icon=":material/content_cut:")

pg = st.navigation([pdf_typeA_page, ])
pg.run()