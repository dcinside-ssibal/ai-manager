import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scripts.ml_pipeline.predict import predict, load_resources
from scripts.discord_alert import send_discord_alert
from scripts.utils import load_login_info, setup_driver, login
from datetime import datetime, timedelta
import time

def load_config(file_path):
    config = {}
    try:
        with open(file_path) as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value
    except Exception:
        pass
    return config

def get_post_time(post):
    time_str = post.find('td', class_='gall_date').text.strip()
    try:
        # 변환할 날짜와 시간 형식 (이 부분은 실제 게시글 시간 포맷에 맞게 조정해야 할 수 있음)
        return datetime.strptime(time_str, '%Y.%m.%d %H:%M')
    except ValueError:
        return None

def process_posts(posts, ten_minutes_ago, discord_webhook_url):
    for post in posts:
        post_time = get_post_time(post)
        if post_time and post_time >= ten_minutes_ago:
            title = post.find('td', class_='gall_tit').text.strip()
            link = post.find('td', class_='gall_tit').a['href']
            post_url = f'https://gall.dcinside.com{link}'
            
            try:
                if predict(title):
                    message = f"문제 있는 게시글 제목 발견: {title}\n{post_url}"
                    send_discord_alert(message, discord_webhook_url)
            except Exception as e:
                print(f"Error predicting or sending alert: {e}")

def monitor_new_posts(discord_webhook_url):
    config = load_config('config/discord.txt')
    
    tokenizer, model = load_resources()
    if tokenizer is None or model is None:
        return

    driver = setup_driver()
    if driver is None:
        return
    
    user_id, user_password = load_login_info()
    if not user_id or not user_password:
        driver.quit()
        return

    try:
        current_time = datetime.now()
        ten_minutes_ago = current_time - timedelta(minutes=10)

        page_number = 1
        while True:
            driver.get(f'https://gall.dcinside.com/mgallery/board/lists?id=galaxy&page={page_number}')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            posts = soup.find_all('tr', class_='ub-content us-post')

            if not posts:
                break

            process_posts(posts, ten_minutes_ago, discord_webhook_url)

            # 페이지 이동
            page_number += 1

            # 잠시 대기 (서버에 부담을 줄 수 있으므로)
            time.sleep(1)

    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        driver.quit()

def monitor():
    config = load_config('config/discord.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        return

    monitor_new_posts(discord_webhook_url)

if __name__ == "__main__":
    monitor()
