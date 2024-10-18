import streamlit as st
import re

from io import StringIO

from split.split_mmd import get_list_tex
from split.url_images import get_list_image


st.set_page_config(
    page_title="수능 AI plus",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# 수능 AI plus"
    }
)

if 'exercises' not in st.session_state:
    st.session_state['exercises'] = []
if 'url_images' not in st.session_state:
    st.session_state['url_images'] = []

# HWP 에서 생성한 PDF 로 생성한 Tex 파일을 업로드
st.subheader("TeX 파일 업로드")
exercises_file = st.file_uploader(label="HWP로 생성한 TeX 파일을 업로드하세요. (미주: [정답], [해설])"
                                  , type=["md", "mmd"])

if exercises_file is not None:
    st.subheader("Split MMD Sources")
    ## 업로드한 Tex 파일을 문항과 해설로 분할
    if st.button("MMD 파일 분리", use_container_width=True):
        ## 문제와 해설 분할
        tex_org_exercises = StringIO(exercises_file.getvalue().decode("utf-8"))
        st.session_state['exercises'] = \
            [exercise for exercise in get_list_tex(tex_org_exercises.getvalue())]
        st.session_state['url_images'] = \
            [get_list_image(exercise) for exercise in st.session_state['exercises']]
        for idx, exercise in enumerate(st.session_state['exercises']):
            st.session_state['exercises'][idx] = re.sub(r'!\[]\(.*?\)','%그림 위치%', exercise)

        tex_org_exercises.close()
    st.write(f"'{exercises_file.name}' 을 {len(st.session_state['exercises'])}개의 파일로 분리. ")

def update_item(type_item: str, idx: int) -> None:
    st.session_state[type_item][idx] = st.session_state[f"{type_item}_{idx}"]

for idx, exercise in enumerate(st.session_state['exercises']):
    num_images = len(re.findall('\%그림 위치\%', exercise))
    num_sections = len(re.findall('section', exercise))
    st.text_area(label="문제" + str(idx + 1) \
                       + f", 그림 수: {str(num_images)}," \
                       + f" 잡다한 것: {str(num_sections)}", value=exercise, height=400
                 , key=f"exercises_{idx}"
                 , on_change=update_item
                 , args=('exercises', idx))
    st.write(st.session_state['url_images'][idx])