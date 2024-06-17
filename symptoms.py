import requests
import json
from bs4 import BeautifulSoup

website = 'https://www.dayi.org.cn'
symptoms_path = "symptoms.json"

symptoms_count = 0


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
    category = '1'
    max_page = 343
    for page_index in range(1, max_page+1):
        page_href = website + '/list' + '/' + category + '/' + str(page_index)
        resp = requests.get(page_href)
        soup = BeautifulSoup(resp.content, features="html.parser")
        elements = soup.find_all(class_ = "title-left")

        href_contents = []
        for element in elements:
            span_element = element.find('span')
            if '症状' in span_element.get_text().strip():
                href_contents.append(element.find('a')['href'])

        for symptom_addr in href_contents:
            # 存储单个症状
            symptom_dict = {}    

            # 获得症状html页面并封装成BeautifulSoup类型的对象
            symptom_href = website + symptom_addr
            symptom_resp = requests.get(symptom_href)
            symptom_soup = BeautifulSoup(symptom_resp.content, features="html.parser")

            global symptoms_count
            symptom_dict['index'] = symptoms_count + 1

            # 获取症状名
            symptom_titles = symptom_soup.select('html > body > div:nth-child(1) > div > div > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div > article > div:nth-child(1) > div > div > div:nth-child(1) > span')
            symptom_dict['症状名'] = symptom_titles[0].get_text()

            # 获取症状介绍
            symptom_intros = symptom_soup.find_all(class_="intro")
            symptom_dict['介绍'] = symptom_intros[0].get_text()

            # 获取剩余所有的属性
            # 查找所有并列section元素
            one_section_elements = symptom_soup.find_all('section', class_='long-item')

            # 遍历section元素
            for one_section in one_section_elements:
                # 找出class="one-title"元素
                one_title_elements = one_section.find(class_="one-title")
                # 从one-title元素中获得文本
                one_title_text = one_title_elements.get_text().strip()  # 获取一级标题文本

                # 查找相对应的二级标题和内容元素
                two_title_elements = one_section.find_all(class_='two-title')
                if len(two_title_elements) == 0:
                    symptom_dict[one_title_text] = one_section.find_all(class_="field-content")[0].get_text().strip()
                else:
                    # 创建词典，以一级标题为key，value为嵌套词典，存储二级标题和内容
                    symptom_dict[one_title_text] = {}  # 创建一个嵌套字典用于存储二级标题和内容
                    all_two_field_elements = one_section.find_all(class_="field-content")
                    for two_title, two_content in zip(two_title_elements, all_two_field_elements):
                        two_title_text = two_title.get_text().strip()
                        content_text = two_content.get_text().strip()
                        symptom_dict[one_title_text][two_title_text] = content_text

            
            # 将单个处方pres_dict追加存储到prescripions.json文件中
            append_to_json(symptom_dict, symptoms_path)

            
            symptoms_count += 1
            print('page_index=', page_index, symptom_addr,  symptoms_count, "   ok")
      

            

if __name__ == "__main__":
    main()








