import streamlit as st
import re

from db_mongo.db_util import create_document
from mathpixAPI.mathpix_pdf import process_pdf, download_result
from split.split_mmd import get_list_tex

st.set_page_config(
    page_title="Mathpix API(PDF) 테스트",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# 수능 AI plus"
    }
)

st.title("Mathpix API 테스트")

if 'exercises' not in st.session_state:
    st.session_state['exercises'] = []
if 'url_images' not in st.session_state:
    st.session_state['url_images'] = []

st.subheader("PDF 파일 업로드")
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요.", type="pdf")

if uploaded_file is not None:
    if st.button("PDF 처리 시작", use_container_width=True):
        with st.spinner("PDF 처리 중..."):
            pdf_id = process_pdf(uploaded_file)
            st.success(f"PDF 업로드 완료. PDF ID: {pdf_id}")
            # MMD 다운로드
            mmd_content = download_result(pdf_id, "mmd").decode("utf-8")

            if mmd_content is not None:
                st.session_state['exercises'], st.session_state['url_images'] = \
                    [exercise for exercise in get_list_tex(mmd_content)]
                # MMD 원본 보기
                st.subheader(f"{uploaded_file.name}.mmd")
                # st.write(mmd_content)

def update_item(type_item: str, idx: int) -> None:
    st.session_state[type_item][idx] = st.session_state[f"{type_item}_{idx}"]

# MMD 분리된 것 보기
for idx, exercise in enumerate(st.session_state['exercises']):
    num_images = len(re.findall(r'%\[그림 위치]%', exercise))
    num_sections = len(re.findall(r'section', exercise))
    st.text_area(label="문제" + str(idx + 1) \
                       + f", 그림 수: {str(num_images)}," \
                       + f" 잡다한 것: {str(num_sections)}", value=exercise, height=400
                 , key=f"exercises_{idx}"
                 , on_change=update_item
                 , args=('exercises', idx)
                 )
    st.write(st.session_state['url_images'][idx])

with st.sidebar:
    if st.button("DB 저장", use_container_width=True):
        for idx, exercise in enumerate(st.session_state['exercises']):
            db_id = create_document(
                    {
                    "exercise": exercise,
                    "url_images": st.session_state['url_images'][idx]
                    }
                )
            st.write(f"ID: {db_id}")
