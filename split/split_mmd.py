import re

def get_list_tex(src_mmd: str) -> list[str]:
    texts = split_by_numbered_lines(src_mmd)
    texts = process_list(texts)
    texts = [text.strip() for text in texts]
    # 특정 단어 삭제
    texts = [remove_words(text) for text in texts]
    # \section*{section_title}부터 끝까지 삭제
    texts = [remove_section_to_end(text) for text in texts]
    # 문서 상단에 '대학수학능력시험'을 포함한 부분 삭제
    texts = [text for text in texts if not re.findall("대학수학능력시험", text)]
    # 한글 문자 또는 \( 또는 \)를 포함하는 항목만 선택
    korean_pattern = re.compile('[가-힣]|\\(|\\)')
    texts = [text for text in texts if korean_pattern.search(text)]
    ## 18byte 이하인 항목 제거
    texts = [text for text in texts if len(text) > 18]

    return texts

def remove_words(text: str) -> str:
    words = ['\section*{수학 영역}']
    pattern = '|'.join(map(re.escape, words))
    text = re.sub(pattern,'', text)
    return text.strip()
# \section*{section_title}부터 끝까지 삭제
def remove_section_to_end(text: str) -> str:
    words = ['\section*{공통과목}', '\section*{미적분}', '\section*{확률과 통계}', '\section*{단답형}'
        , '\section*{- 수학 영역}', '\section*{* 확인 사항}', '\section*{5 지선다형}', '\\footnotetext']
    pattern = '|'.join(map(re.escape, words))
    regex = re.compile(pattern)
    match = regex.search(text)
    if match:
        text = text[:match.start()]
    words2 = ['- 수학 영역', '* 확인 사항', '5 지선다형']
    pattern2 = '|'.join(map(re.escape, words2))
    regex2 = re.compile(pattern2, re.IGNORECASE)
    match2 = regex2.search(text)
    if match2:
        text = text[:match2.start()]
    return text.strip()

def split_by_numbered_lines(text: str) -> list[str]:
    # 스캔한 모의고사의 정답은 따로 이미지로 처리하기로 하자.
    # 자동 처리된 부분: 이감모의고사 문제,
    pattern = (r'^\d{1,3}\.\s|^\d{1,3}\)\s|^\\section\*\{\d{1,3}\)\s|' # 수학비서 HWP
               r'^\\section\*\{\d{1,3}\}$|' # 서바이벌 정규 문제. 
               r'^\d{1,3}\s?\.$|^\\section\*\{\d{1,3}\s?\.\}$|' # 킬링캠프 해설
               r'^\\section\*\{\d{1,3}\s?\.\s?정답\s?\(?\d{1,3}\)?\}$' # 이감모의고사 해설
               )

    # 텍스트를 라인으로 분할
    lines = text.split('\n')

    result = []
    current_section = []

    for line in lines:
        if re.match(pattern, line):
            if current_section:
                result.append('\n'.join(current_section))
                current_section = []
        current_section.append(re.sub(pattern, '', line))
        # current_section.append(line)

    if current_section:
        result.append('\n'.join(current_section))

    return result

def process_list(input_list):
    result = []
    for item in input_list:
        if isinstance(item, str):
            split_result = split_by_pattern(item)
            result.extend(split_result)
        else:
            result.append(item)
    return result


def split_by_pattern(text):
    # 패턴: 숫자로 시작하는 줄, 빈 줄, 텍스트와 괄호 안의 숫자로 끝나는 줄
    pattern = r'(\d+\s?\n\n(?:(?!\n).){1,7}?\(?\d+\)?)' # 서바이벌 정규 해설
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
    # 모든 매치 찾기
    matches = list(regex.finditer(text))
    # 결과 리스트 초기화
    result = []
    # 매치가 없으면 원본 텍스트 반환
    if not matches:
        return [text]
    # 첫 번째 매치 이전의 텍스트와 첫 번째 매치를 함께 처리
    result.append(text[:matches[0].start()])
    # 나머지 매치들 처리, 매치를 포함하려면 start()
    for i in range(1, len(matches)):
        result.append(text[matches[i - 1].end():matches[i].start()])
    result.append(text[matches[-1].end():])

    return result