from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime, timedelta
from .utils import load_login_info, setup_driver, login, load_existing_posts, save_posts

def parse_processing_info(text):
    date_match = re.search(r'\d{4}\.\d{2}\.\d{2}', text)
    date = date_match.group(0) if date_match else ''
    time_match = re.search(r'\d{2}:\d{2}:\d{2}', text)
    time = time_match.group(0) if time_match else ''
    handler_match = re.search(r'처리자\s*:\s*(\S+)', text)
    handler = handler_match.group(1) if handler_match else ''
    return f"{date} {time}", handler

def get_recent_posts(driver, page):
    url = f'https://gall.dcinside.com/mgallery/board/lists?id=galaxy_tab&page={page}'
    print(f"Loading URL: {url}")
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.ub-content.us-post'))
        )
    except Exception as e:
        print(f"Error loading post list page {page}: {e}")
        print(f"Stacktrace: {e}")
        page_source = driver.page_source
        with open(f'debug_page_source_{page}.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        return []

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    posts = soup.find_all('tr', class_='ub-content us-post')
    
    post_data = []
    for post in posts:
        title = post.find('td', class_='gall_tit').text.strip()
        link = post.find('td', class_='gall_tit').a['href']
        post_url = f'https://gall.dcinside.com{link}'
        time_text = post.find('td', class_='gall_date')['title'].strip()
        post_time = datetime.strptime(time_text, '%Y-%m-%d %H:%M:%S')
        writer = post.find('td', class_='gall_writer').text.strip()
        view_count = post.find('td', class_='gall_count').text.strip()
        recommend_count = post.find('td', class_='gall_recommend').text.strip()

        # 1시간 이상 지난 게시글만 선택
        if post_time < datetime.now() - timedelta(hours=1):
            post_data.append({
                'title': title,
                'url': post_url,
                'time': post_time.strftime('%Y-%m-%d %H:%M:%S'),
                'writer': writer,
                'view_count': view_count,
                'recommend_count': recommend_count
            })
    
    return post_data

def scrape_monitored_posts():
    user_id, user_password = load_login_info()
    driver = setup_driver()
    login(driver, user_id, user_password)

    monitored_posts = load_existing_posts()
    new_posts = []
    existing_urls = [post['url'] for post in monitored_posts]

    for page in range(1, 5):
        try:
            recent_posts = get_recent_posts(driver, page)
            for post in recent_posts:
                if post['url'] not in existing_urls:
                    new_posts.append(post)
        except Exception as e:
            print(f"Error while getting posts from page {page}: {e}")

    monitored_posts.extend(new_posts)
    save_posts(monitored_posts)

    driver.quit()
    print("Monitoring and saving new posts completed.")

# 기존 함수들
def get_block_list(driver, page):
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

def get_delete_list(driver, page):
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

def scrape_block_list():
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

def scrape_delete_list():
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
    scrape_monitored_posts()
    scrape_block_list()
    scrape_delete_list()
