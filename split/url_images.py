import re
import requests


def get_list_image(text: str) -> list[str]:
    # result = []
    result = re.findall(r'!\[]\((.*)?\)', text)
    for result in result:
        save_path = re.search(r'\d{4}_.*\.jpg', result).group(0)
        download_image(result, save_path)

    return result

def download_image(url, save_path):
    save_path = 'images/' + save_path
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"이미지가 성공적으로 다운로드되어 {save_path}에 저장되었습니다.")
    else:
        print("이미지 다운로드에 실패했습니다.")