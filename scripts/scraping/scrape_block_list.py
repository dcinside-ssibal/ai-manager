from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import os
from scripts.utils import load_login_info, setup_driver, login

def parse_processing_info(text):
    date = re.search(r'\d{4}\.\d{2}\.\d{2}', text)
    time = re.search(r'\d{2}:\d{2}:\d{2}', text)
    handler = re.search(r'처리자\s*:\s*(\S+)', text)
    return f"{date.group(0) if date else ''} {time.group(0) if time else ''}", handler.group(1) if handler else ''

def get_block_list(driver, page):
    url = f'https://gall.dcinside.com/mgallery/management/block?id=galaxy&p={page}'
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'minor_block_list')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'class': 'minor_block_list'})
    if not table:
        return []
    rows = table.find('tbody').find_all('tr')
    data_list = []
    for row in rows:
        cols = row.find_all('td')
        processed_date, handler = parse_processing_info(cols[5].text.strip())
        data_list.append({
            'number': cols[0].text.strip(),
            'nickname_or_ip': cols[1].text.strip().replace('\n', ' '),
            'post_or_comment': cols[2].text.strip(),
            'reason': cols[3].text.strip(),
            'block_duration': cols[4].text.strip(),
            'processed_date': processed_date,
            'handler': handler,
            'block_status': 'blocking' if '차단 중' in cols[6].text.strip() else 'unblock'
        })
    return data_list

def load_existing_data():
    if os.path.exists('data/block_list.json'):
        with open('data/block_list.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def scrape_block_list():
    user_id, user_password = load_login_info()
    driver = setup_driver()
    login(driver, user_id, user_password)

    existing_data = load_existing_data()
    existing_numbers = {item['number'] for item in existing_data}
    
    block_data = []
    page = 1
    while True:
        current_block_data = get_block_list(driver, page)
        if not current_block_data:
            break
        new_data = [item for item in current_block_data if item['number'] not in existing_numbers]
        if not new_data:
            break
        block_data.extend(new_data)
        page += 1

    if block_data:
        os.makedirs('data', exist_ok=True)
        with open('data/block_list.json', 'w', encoding='utf-8') as f:
            json.dump(existing_data + block_data, f, ensure_ascii=False, indent=4)

    driver.quit()

if __name__ == "__main__":
    scrape_block_list()
