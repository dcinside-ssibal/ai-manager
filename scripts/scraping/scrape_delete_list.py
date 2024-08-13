from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import os
from scripts.utils import load_login_info, setup_driver, login

def get_delete_list(driver, page):
    url = f'https://gall.dcinside.com/mgallery/management/delete?id=galaxy&p={page}'
    driver.get(url)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'minor_block_list'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'class': 'minor_block_list del'})
    if not table:
        return []

    rows = table.find('tbody').find_all('tr')
    if not rows:
        return []  # Return empty list if no rows are found, indicating no more pages

    data_list = []
    for row in rows:
        cols = row.find_all('td')
        processed_datetime = re.sub(r'(\d{4}\.\d{2}\.\d{2})(\d{2}:\d{2}:\d{2})', r'\1 \2', cols[3].text.strip())
        data_list.append({
            'number': cols[0].text.strip(),
            'nickname_or_ip': cols[1].text.strip().replace('\n', ' '),
            'post_or_comment': cols[2].text.strip(),
            'processed_datetime': processed_datetime,
            'handler': cols[4].text.strip()
        })
    return data_list

def scrape_delete_list():
    user_id, user_password = load_login_info()
    driver = setup_driver()
    login(driver, user_id, user_password)

    delete_data = []
    page = 1
    while True:
        try:
            current_delete_data = get_delete_list(driver, page)
            if not current_delete_data:
                break  # Stop if no data is returned, indicating no more pages
            delete_data.extend(current_delete_data)
            page += 1
            
            if page % 50 == 0:
                message = f"Processed page {page}"
                print(message)  # 콘솔에 로그를 출력
        except Exception as e:
            print(f"Error getting delete list from page {page}: {e}")
            break  # Stop the loop on error

    os.makedirs('data', exist_ok=True)
    with open('data/delete_list.json', 'w', encoding='utf-8') as f:
        json.dump(delete_data, f, ensure_ascii=False, indent=4)

    print("Complete Delete List")
    driver.quit()

if __name__ == "__main__":
    scrape_delete_list()
