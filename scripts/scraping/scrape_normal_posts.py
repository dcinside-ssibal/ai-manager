from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from scripts.utils import load_login_info, setup_driver, load_existing_posts, save_posts
import re

def get_normal_posts(driver, page):
    url = f'https://gall.dcinside.com/mgallery/board/lists?id=galaxy&page={page}'
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.ub-content.us-post'))
        )
    except Exception as e:
        print(f"Error loading page {page}: {e}")
        with open(f'debug_page_source_{page}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        return []

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
        writer = post.find('td', class_='gall_writer').text.strip()
        view_count = post.find('td', class_='gall_count').text.strip()
        recommend_count = post.find('td', class_='gall_recommend').text.strip()

        # Extract and remove comment count from title
        comment_match = re.search(r'\n\[(\d+)\]', title_text)
        comment_count = comment_match.group(1) if comment_match else ''
        title_cleaned = re.sub(r'\n\[\d+\]$', '', title_text).strip()

        if post_time < datetime.now() - timedelta(hours=1):
            post_data.append({
                'title': title_cleaned,
                'url': post_url,
                'time': post_time.strftime('%Y-%m-%d %H:%M:%S'),
                'writer': writer,
                'view_count': view_count,
                'recommend_count': recommend_count,
                'comment': comment_count
            })
    
    return post_data

def scrape_normal_posts():
    driver = setup_driver()

    normal_posts = load_existing_posts()
    new_posts = []
    existing_urls = {post['url'] for post in normal_posts}

    for page in range(1, 501):
        try:
            recent_posts = get_normal_posts(driver, page)
            new_posts.extend(post for post in recent_posts if post['url'] not in existing_urls)
            if page % 50 == 0:
                message = f"Processed page {page}"
                print(message)  # 콘솔에 로그를 출력
        except Exception as e:
            print(f"Error getting posts from page {page}: {e}")

    normal_posts.extend(new_posts)
    save_posts(normal_posts)
    driver.quit()

if __name__ == "__main__":
    scrape_normal_posts()
