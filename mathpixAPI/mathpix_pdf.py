import os
import zipfile
import requests
import json
import time
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 엔드포인트 및 인증 정보 설정
API_ENDPOINT = "https://api.mathpix.com/v3/pdf"
APP_ID = os.getenv("MATHPIX_APP_ID")
APP_KEY = os.getenv("MATHPIX_APP_KEY")

# 헤더 설정
headers = {
    "app_id": APP_ID,
    "app_key": APP_KEY
}

# PDF 파일 업로드 및 처리
def process_pdf(file) -> str | None:
    files = {"file": file}
    data = {"options_json": json.dumps({
        "math_inline_delimiters": ["\\(", "\\)"], # default
        "math_display_delimiters": ["\\[", "\\]"], # default
        "rm_spaces": True, # default
        "idiomatic_eqn_arrays": True, # default=false
        "include_equation_tags": True, # default=false
    })}
    response = requests.post(API_ENDPOINT, headers=headers, files=files, data=data)

    if response.status_code == 200:
        pdf_id = response.json()["pdf_id"]
        print(f"PDF 업로드 완료. PDF ID: {pdf_id}")
        # 로그 파일에 정보 기록
        pdf_id_info(file.name, pdf_id)
        # PDF 처리 시도
        max_attempts = 30
        for attempt in range(max_attempts):
            status = check_processing_status(pdf_id)
            if status == "completed":
                print("PDF 처리 완료")

                # 결과 다운로드 및 저장
                # MMD 파일 저장
                mmd_content = download_result(pdf_id, "mmd")
                mmd_filepath = save_file(mmd_content, f"{pdf_id}.mmd")
                print(f"MMD 파일이 {mmd_filepath}에 저장되었습니다.")

                # TEX.ZIP 파일 저장 및 압축 해제
                tex_content = download_result(pdf_id, "tex.zip")
                tex_zip_filepath = save_file(tex_content, f"{pdf_id}.tex.zip")
                print(f"TEX.ZIP 파일이 {tex_zip_filepath}에 저장되었습니다.")
                extracted_path = extract_zip(tex_zip_filepath)
                print(f"ZIP 파일의 내용이 {extracted_path}에 압축 해제되었습니다.")

                break
            elif status == "error":
                print("PDF 처리 중 오류 발생")
                break
            else:
                print(f"처리 중... ({attempt + 1}/{max_attempts})")
                time.sleep(10)
        else:
            print("최대 대기 시간 초과")
        return pdf_id
    else:
        raise Exception(f"PDF 업로드 실패: {response.text}")


# 로그 파일 정보 기록
def pdf_id_info(filename:str, pdf_id=str):
    with open(f"mathpixAPI/pdf_id.txt", "a", encoding='utf-8') as pdf_id_file:
        pdf_id_file.write(f"{filename}, {pdf_id}\n")


# 처리 상태 확인
def check_processing_status(pdf_id: str) -> str:
    url = f"{API_ENDPOINT}/{pdf_id}"
    response = requests.get(url, headers=headers)
    return response.json()["status"] # "completed", "error"


# 결과 다운로드
def download_result(pdf_id: str, output_format: str) -> bytes | None:
    url = f"{API_ENDPOINT}/{pdf_id}.{output_format}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"{output_format.upper()} 파일 다운로드 실패: {response.text}")

# 결과 파일 저장
def save_file(content, filename: str, directory="mathpixAPI/files") -> str:
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath


# ZIP 파일 압축 해제
def extract_zip(zip_path):
    extract_to = f"{zip_path}_extracted"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to