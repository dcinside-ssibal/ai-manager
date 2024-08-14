import requests
from bs4 import BeautifulSoup
from scripts.ml_pipeline.predict import predict, load_resources
from scripts.discord_alert import send_discord_alert
from scripts.utils import setup_driver
from datetime import datetime, timedelta
import time

def load_config(file_path):
    try:
        with open(file_path) as f:
            return dict(line.strip().split('=') for line in f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def get_post_time(post):
    try:
        time_str = post.find('td', class_='gall_date')['title'].strip()
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return None

def get_post_author(post):
    try:
        author_element = post.find('td', class_='gall_writer')
        return author_element.get_text(strip=True) if author_element else "Unknown"
    except Exception:
        return "Unknown"

def filter_post_title(subject):
    return any(excluded in subject for excluded in ['설문', '공지', '광고'])

def process_posts(posts, five_minutes_ago, discord_webhook_url):
    for post in posts:
        try:
            subject_element = post.find('td', class_='gall_subject')
            if not subject_element:
                continue
            
            subject = subject_element.text.strip()
            if filter_post_title(subject):
                continue

            title_element = post.find('td', class_='gall_tit')
            if not title_element:
                continue
            
            title_link_element = title_element.find('a')
            if not title_link_element:
                continue
            
            title = title_link_element.text.strip()
            link = title_link_element.get('href')
            post_url = f'https://gall.dcinside.com{link}'
            post_time = get_post_time(post)
            if not post_time:
                continue

            author = get_post_author(post)
            if post_time >= five_minutes_ago and predict(title):
                message = (
                    f"\n---\n"
                    f"⚠️ **이 게시글은 AI 모델에 의해 의심스러운 내용으로 분류되었습니다.**\n\n"
                    f"**제목:** [{title}]({post_url})\n"
                    f"**작성자:** {author}\n"
                    f"**작성 시간:** {post_time.strftime('%H:%M')}\n"
                )
                send_discord_alert(message, discord_webhook_url)
        except Exception as e:
            print(f"Error processing post: {e}")

def monitor_new_posts(discord_webhook_url):
    config = load_config('config/discord.txt')
    tokenizer, model = load_resources()
    if not tokenizer or not model:
        return

    driver = setup_driver()
    if not driver:
        return

    try:
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        page_number = 1
        while True:
            driver.get(f'https://gall.dcinside.com/mgallery/board/lists?id=galaxy&page={page_number}')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            posts = soup.find_all('tr', class_='ub-content')
            if not posts:
                break

            if any(get_post_time(post) and get_post_time(post) >= five_minutes_ago for post in posts):
                process_posts(posts, five_minutes_ago, discord_webhook_url)
                page_number += 1
                time.sleep(2)
            else:
                break
    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        driver.quit()

def monitor():
    config = load_config('config/discord.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if discord_webhook_url:
        monitor_new_posts(discord_webhook_url)

if __name__ == "__main__":
    monitor()
