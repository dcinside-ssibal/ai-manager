from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
from scripts.utils import load_login_info, setup_driver, login

def get_delete_list(driver, page):
    """Retrieve delete list data from the given page."""
    url = f'https://gall.dcinside.com/mgallery/management/delete?id=galaxy_tab&p={page}'
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'minor_block_list'))
        )
    except Exception as e:
        print(f"Error loading delete list page {page}: {e}")
        return []

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'class': 'minor_block_list del'})
    if table is None:
        return []
    rows = table.find('tbody').find_all('tr')
    data_list = []
    for row in rows:
        cols = row.find_all('td')
        processed_datetime = cols[3].text.strip()
        processed_datetime = re.sub(r'(\d{4}\.\d{2}\.\d{2})(\d{2}:\d{2}:\d{2})', r'\1 \2', processed_datetime)
        data = {
            'number': cols[0].text.strip(),
            'nickname_or_ip': cols[1].text.strip().replace('\n', ' '),
            'post_or_comment': cols[2].text.strip(),
            'processed_datetime': processed_datetime,
            'handler': cols[4].text.strip()
        }
        data_list.append(data)
    return data_list

def scrape_delete_list():
    """Main function to scrape the delete list and save it to a JSON file."""
    user_id, user_password = load_login_info()
    driver = setup_driver()
    login(driver, user_id, user_password)

    delete_data = []
    for page in range(1, 5):
        try:
            delete_data.extend(get_delete_list(driver, page))
        except Exception as e:
            print(f"Error while getting delete list from page {page}: {e}")

    os.makedirs('data', exist_ok=True)
    with open('data/delete_list.json', 'w', encoding='utf-8') as f:
        json.dump(delete_data, f, ensure_ascii=False, indent=4)

    driver.quit()
    print("Delete list scraping completed.")

if __name__ == "__main__":
    scrape_delete_list()
