from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
from scripts.utils import load_login_info, setup_driver, login

def parse_processing_info(text):
    """Extract processing date, time, and handler from the text."""
    date_match = re.search(r'\d{4}\.\d{2}\.\d{2}', text)
    date = date_match.group(0) if date_match else ''
    time_match = re.search(r'\d{2}:\d{2}:\d{2}', text)
    time = time_match.group(0) if time_match else ''
    handler_match = re.search(r'처리자\s*:\s*(\S+)', text)
    handler = handler_match.group(1) if handler_match else ''
    return f"{date} {time}", handler

def get_block_list(driver, page):
    """Retrieve block list data from the given page."""
    url = f'https://gall.dcinside.com/mgallery/management/block?id=galaxy_tab&p={page}'
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'minor_block_list'))
        )
    except Exception as e:
        print(f"Error loading block list page {page}: {e}")
        return []

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'class': 'minor_block_list'})
    if table is None:
        return []
    rows = table.find('tbody').find_all('tr')
    data_list = []
    for row in rows:
        cols = row.find_all('td')
        processed_date, handler = parse_processing_info(cols[5].text.strip())
        data = {
            'number': cols[0].text.strip(),
            'nickname_or_ip': cols[1].text.strip().replace('\n', ' '),
            'post_or_comment': cols[2].text.strip(),
            'reason': cols[3].text.strip(),
            'block_duration': cols[4].text.strip(),
            'processed_date': processed_date,
            'handler': handler,
            'block_status': 'blocking' if '차단 중' in cols[6].text.strip() else 'unblock'
        }
        data_list.append(data)
    return data_list

def scrape_block_list():
    """Main function to scrape the block list and save it to a JSON file."""
    user_id, user_password = load_login_info()
    driver = setup_driver()
    login(driver, user_id, user_password)

    block_data = []
    for page in range(1, 5):
        try:
            block_data.extend(get_block_list(driver, page))
        except Exception as e:
            print(f"Error while getting block list from page {page}: {e}")

    os.makedirs('data', exist_ok=True)
    with open('data/block_list.json', 'w', encoding='utf-8') as f:
        json.dump(block_data, f, ensure_ascii=False, indent=4)

    driver.quit()
    print("Block list scraping completed.")

if __name__ == "__main__":
    scrape_block_list()
