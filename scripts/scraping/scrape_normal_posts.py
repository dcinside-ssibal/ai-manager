from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import re
from scripts.utils import setup_driver

def get_normal_posts(driver, page):
    url = f'https://gall.dcinside.com/mgallery/board/lists?id=galaxy&page={page}'
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.ub-content.us-post')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    posts = soup.find_all('tr', class_='ub-content us-post')
    
    post_data = []
    for post in posts:
        title_td = post.find('td', class_='gall_tit')
        title_text = title_td.text.strip()
        link = title_td.a['href']
        post_url = f'https://gall.dcinside.com{link}'
        time_text = post.find('td', class_='gall_date')['title'].strip()
        post_time = datetime.strptime(time_text, '%Y-%m-%d %H:%M:%S')
        
        if post_time < datetime.now() - timedelta(hours=1):
            comment_match = re.search(r'\n\[(\d+)\]', title_text)
            post_data.append({
                'title': re.sub(r'\n\[\d+\]$', '', title_text).strip(),
                'url': post_url,
                'time': post_time.strftime('%Y-%m-%d %H:%M:%S'),
                'writer': post.find('td', class_='gall_writer').text.strip(),
                'view_count': post.find('td', class_='gall_count').text.strip(),
                'recommend_count': post.find('td', class_='gall_recommend').text.strip(),
                'comment': comment_match.group(1) if comment_match else ''
            })
    
    return post_data

def load_existing_posts():
    path = 'data/normal_posts.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def scrape_normal_posts():
    driver = setup_driver()
    existing_posts = load_existing_posts()
    existing_urls = {post['url'] for post in existing_posts}

    all_posts = []
    for page in range(1, 501):
        try:
            recent_posts = get_normal_posts(driver, page)
            new_posts = [post for post in recent_posts if post['url'] not in existing_urls]
            if not new_posts:
                break
            all_posts.extend(new_posts)
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    os.makedirs('data', exist_ok=True)
    with open('data/normal_posts.json', 'w', encoding='utf-8') as f:
        json.dump(existing_posts + all_posts, f, ensure_ascii=False, indent=4)

    driver.quit()

if __name__ == "__main__":
    scrape_normal_posts()
