from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
from scripts.utils import load_login_info, setup_driver, login
from scripts.discord_alert import send_discord_alert

def parse_processing_info(text):
    date = re.search(r'\d{4}\.\d{2}\.\d{2}', text)
    time = re.search(r'\d{2}:\d{2}:\d{2}', text)
    handler = re.search(r'처리자\s*:\s*(\S+)', text)
    return f"{date.group(0) if date else ''} {time.group(0) if time else ''}", handler.group(1) if handler else ''

def get_block_list(driver, page):
    url = f'https://gall.dcinside.com/mgallery/management/block?id=galaxy&p={page}'
    driver.get(url)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'minor_block_list'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'class': 'minor_block_list'})
    if not table:
        return []

    rows = table.find('tbody').find_all('tr')
    if not rows:
        return []  # Return empty list if no rows are found, indicating no more pages

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

def scrape_block_list():
    user_id, user_password = load_login_info()
    driver = setup_driver()
    login(driver, user_id, user_password)

    block_data = []
    page = 1
    while True:
        try:
            current_block_data = get_block_list(driver, page)
            if not current_block_data:
                break  # Stop if no data is returned, indicating no more pages
            block_data.extend(current_block_data)

            # 50페이지마다 로그를 보냄
            if page % 50 == 0:
                message = f"Processed page {page}"
                print(message)  # 콘솔에 로그를 출력
                # Uncomment the following line to send a Discord alert instead
                # send_discord_alert(message, discord_webhook_url)

            page += 1

        except Exception as e:
            print(f"Error getting block list from page {page}: {e}")
            break  # Stop the loop on error

    os.makedirs('data', exist_ok=True)
    with open('data/block_list.json', 'w', encoding='utf-8') as f:
        json.dump(block_data, f, ensure_ascii=False, indent=4)

    print("Complete Block List")
    driver.quit()

if __name__ == "__main__":
    scrape_block_list()
