import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scripts.ml_pipeline.predict import predict, load_resources
from scripts.discord_alert import send_discord_alert
from scripts.utils import load_login_info, setup_driver, login

def load_config(file_path):
    """
    Loads configuration from a file.
    
    Args:
        file_path (str): Path to the configuration file.
    
    Returns:
        dict: A dictionary containing configuration key-value pairs.
    """
    config = {}
    try:
        with open(file_path) as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value
        print(f"Configuration loaded from {file_path}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
    return config

def monitor_new_posts(discord_webhook_url):
    """
    Monitors new posts and sends alerts if issues are detected.
    
    Args:
        discord_webhook_url (str): The URL for Discord webhook.
    """
    print("Starting to monitor new posts...")
    config = load_config('config/discord.txt')
    
    # Load the model and tokenizer
    tokenizer, model = load_resources()
    if tokenizer is None or model is None:
        print("Error: Tokenizer or model is not loaded.")
        return

    # Set up Selenium
    driver = setup_driver()
    if driver is None:
        print("Error setting up Selenium driver.")
        return
    
    user_id, user_password = load_login_info()
    if not user_id or not user_password:
        print("Error: User credentials not loaded.")
        driver.quit()
        return
    
    login(driver, user_id, user_password)

    try:
        driver.get('https://gall.dcinside.com/mgallery/board/lists?id=galaxy_tab')
        print("Selenium driver initialized and page loaded.")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        posts = soup.find_all('tr', class_='ub-content us-post')
        print(f"Found {len(posts)} posts.")
        
        for post in posts:
            title = post.find('td', class_='gall_tit').text.strip()
            link = post.find('td', class_='gall_tit').a['href']
            post_url = f'https://gall.dcinside.com{link}'
            
            try:
                if predict(title, tokenizer, model):
                    message = f"문제 있는 게시글 제목 발견: {title}\n{post_url}"
                    print(f"Predicting title: {title}")
                    send_discord_alert(message, discord_webhook_url)
            except Exception as e:
                print(f"Error predicting title '{title}': {e}")

    except Exception as e:
        print(f"Error parsing posts: {e}")
    finally:
        driver.quit()
        print("Selenium driver closed.")

def monitor():
    """
    Loads configuration and starts the monitoring process.
    """
    config = load_config('config/discord.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("Discord webhook URL not configured.")
        return

    print(f"Monitoring started with webhook URL: {discord_webhook_url}")
    monitor_new_posts(discord_webhook_url)
    print("Monitoring completed.")

if __name__ == "__main__":
    monitor()
