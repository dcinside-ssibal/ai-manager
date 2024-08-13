import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scripts.ml_pipeline.predict import predict, load_resources
from scripts.discord_alert import send_discord_alert
from scripts.utils import load_login_info, setup_driver, login

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
    
    login(driver, user_id, user_password)

    try:
        driver.get('https://gall.dcinside.com/mgallery/board/lists?id=galaxy_tab')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        posts = soup.find_all('tr', class_='ub-content us-post')
        
        for post in posts:
            title = post.find('td', class_='gall_tit').text.strip()
            link = post.find('td', class_='gall_tit').a['href']
            post_url = f'https://gall.dcinside.com{link}'
            
            try:
                if predict(title):
                    message = f"문제 있는 게시글 제목 발견: {title}\n{post_url}"
                    send_discord_alert(message, discord_webhook_url)
            except Exception:
                pass

    except Exception:
        pass
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
