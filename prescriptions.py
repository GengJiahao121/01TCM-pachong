import requests
import json
from bs4 import BeautifulSoup

website = 'https://www.dayi.org.cn'
prescriptions_path = "prescriptions.json"

prescriptions_count = 0


def append_to_json(data, file_path):
    try:
        # Load the existing data from the JSON file
        with open(file_path, "r") as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        # If the file doesn't exist or is empty, start with an empty list
        existing_data = []

    # Append the new dictionary to the existing data
    existing_data.append(data)

    # Write the updated data back to the JSON file
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

def main():
    category = '7'
    max_page = 1645
    for page_index in range(1, max_page+1):
        page_href = website + '/list' + '/' + category + '/' + str(page_index)
        resp = requests.get(page_href)
        soup = BeautifulSoup(resp.content, features="html.parser")
        elements = soup.find_all(class_ = "title-left")
        href_contents = [element.find('a')['href'] for element in elements]
        for pres_addr in href_contents:
            # 存储单个处方
            pres_dict = {}    

            # 获得处方html页面并封装成BeautifulSoup类型的对象
            pres_href = website + pres_addr
            pres_resp = requests.get(pres_href)
            pres_soup = BeautifulSoup(pres_resp.content, features="html.parser")

            global prescriptions_count
            pres_dict['index'] = prescriptions_count + 1

            # 获取处方名
            pres_titles = pres_soup.select('html > body > div:nth-of-type(1) > div > div > div:nth-of-type(2) > div:nth-of-type(3) > div:nth-of-type(1) > div > article > div:nth-of-type(1) > div > div > div:nth-of-type(1) > span')
            pres_dict['方名'] = pres_titles[0].get_text()

            # 获取处方介绍
            pres_intros = pres_soup.find_all(class_="intro")
            pres_dict['介绍'] = pres_intros[0].get_text()

            # 获取剩余所有的属性（包括：歌诀、组成、用法用量......）
            one_titles = pres_soup.find_all(class_="one-title")
            one_contents = pres_soup.find_all(class_="field-content")

            # Extract text from the "one-title" elements and corresponding "field-content" elements
            for one_title, one_content in zip(one_titles, one_contents):
                title_text = one_title.get_text().strip()
                content_text = one_content.get_text().strip()
                pres_dict[title_text] = content_text
            

            # 将单个处方pres_dict追加存储到prescripions.json文件中
            append_to_json(pres_dict, prescriptions_path)

            
            prescriptions_count += 1
            print('page_index=', page_index, pres_addr,  prescriptions_count, "   ok")
            

if __name__ == "__main__":
    main()








