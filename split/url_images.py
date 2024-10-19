import os
import re
import requests
import time


def get_list_image(idx: int, text: str) -> list[str]:
    # result = re.findall(r'!\[]\((.*)?\)', text)
    results = [url for url in re.findall(r'!\[]\((.*)?\)', text)]
    for idy, result in enumerate(results):
    # for result in results:
        success = download_image(result, idx, idy)
        if success:
            print("다운로드 작업이 성공적으로 완료되었습니다.")
        else:
            print("다운로드 작업이 실패했습니다.")

    return results


def download_image(url, idx: int, idy:int, max_retries=3, retry_delay=5):
    directory = "split/images"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.basename(url).split("?")[0]
    filename = os.path.splitext(filename)[0] + f"-{idx + 1}-{idy + 1}" + os.path.splitext(filename)[1]
    save_path = os.path.join(directory, filename)
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생

            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"이미지가 {save_path}에 저장되었습니다.")
            return True
        except requests.RequestException as e:
            print(f"시도 {attempt + 1}/{max_retries} 실패: {e}")
            if attempt < max_retries - 1:
                print(f"{retry_delay}초 후 재시도합니다...")
                time.sleep(retry_delay)
            else:
                print("최대 재시도 횟수에 도달했습니다. 다운로드에 실패했습니다.")
    return False