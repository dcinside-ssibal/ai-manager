import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scripts.ml_pipeline.predict import predict, load_resources
from scripts.discord_alert import send_discord_alert
from scripts.utils import setup_driver
from datetime import datetime, timedelta
import time

def load_config(file_path):
    """Load configuration from a file."""
    config = {}
    try:
        with open(file_path) as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value
        print(f"Config loaded from {file_path}")
    except Exception as e:
        print(f"Error loading config from {file_path}: {e}")
    return config


def get_post_time(post):
    """Extract and parse the post time from the HTML."""
    try:
        time_str = post.find('td', class_='gall_date')['title'].strip()
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error parsing time from post: {e}")
        return None


def get_post_author(post):
    """Extract the post author from the HTML."""
    try:
        author_element = post.find('td', class_='gall_writer')
        if author_element:
            return author_element.get_text(strip=True)
        return "Unknown"
    except Exception as e:
        print(f"Error extracting post author: {e}")
        return "Unknown"


def filter_post_title(subject):
    """Filter out posts based on their subject."""
    excluded_subjects = ['설문', '공지', '광고']
    is_filtered = any(excluded_subject in subject for excluded_subject in excluded_subjects)
    if is_filtered:
        print(f"Post subject '{subject}' is filtered out.")
    return is_filtered

def process_posts(posts, five_minutes_ago, discord_webhook_url):
    """Process each post and send alerts if needed."""
    for post in posts:
        try:
            subject_element = post.find('td', class_='gall_subject')
            if subject_element is None:
                print("No subject element found. Skipping post.")
                continue
            
            subject = subject_element.text.strip()
            if filter_post_title(subject):
                continue  # Skip posts with filtered subjects

            title_element = post.find('td', class_='gall_tit')
            if title_element is None:
                print("No title element found. Skipping post.")
                continue
            
            title_link_element = title_element.find('a')
            if title_link_element is None:
                print("No title link element found. Skipping post.")
                continue
            
            title = title_link_element.text.strip()
            link = title_link_element.get('href')
            post_url = f'https://gall.dcinside.com{link}'
            
            post_time = get_post_time(post)
            if post_time is None:
                print("Error parsing post time. Skipping post.")
                continue

            author = get_post_author(post)

            if post_time >= five_minutes_ago:
                print(f"Processing post: {title} with URL: {post_url}")
                try:
                    if predict(title):
                        message = (
                            f"\n---\n"
                            f"⚠️ **이 게시글은 AI 모델에 의해 의심스러운 내용으로 분류되었습니다.**\n\n"
                            f"**제목:** [{title}]({post_url})\n"
                            f"**작성자:** {author}\n"
                            f"**작성 시간:** {post_time.strftime('%H:%M')}\n"
                        )
                        send_discord_alert(message, discord_webhook_url)
                        print(f"Alert sent for post: {title}")
                except Exception as e:
                    print(f"Error predicting or sending alert for post '{title}': {e}")

        except Exception as e:
            print(f"Error processing post: {e}")


def monitor_new_posts(discord_webhook_url):
    """Monitor new posts and send alerts if needed."""
    config = load_config('config/discord.txt')
    
    tokenizer, model = load_resources()
    if tokenizer is None or model is None:
        print("Error loading resources.")
        return

    driver = setup_driver()
    if driver is None:
        print("Error setting up driver.")
        return

    try:
        current_time = datetime.now()
        five_minutes_ago = current_time - timedelta(minutes=5)
        print(f"Monitoring posts from: {five_minutes_ago}")

        page_number = 1
        while True:
            print(f"Fetching page number: {page_number}")
            driver.get(f'https://gall.dcinside.com/mgallery/board/lists?id=galaxy&page={page_number}')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            posts = soup.find_all('tr', class_='ub-content')

            if not posts:
                print("No more posts found. Exiting.")
                break

            found_recent_post = False
            for post in posts:
                post_time = get_post_time(post)
                if post_time and post_time >= five_minutes_ago:
                    found_recent_post = True
                    break

            if not found_recent_post:
                print("No recent posts found. Exiting.")
                break

            print(f"Processing {len(posts)} posts.")
            process_posts(posts, five_minutes_ago, discord_webhook_url)

            page_number += 1
            time.sleep(2)

    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        driver.quit()
        print("Monitoring completed.")

def monitor():
    """Main function to start monitoring."""
    config = load_config('config/discord.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("No Discord webhook URL found in config.")
        return

    monitor_new_posts(discord_webhook_url)

if __name__ == "__main__":
    monitor()
