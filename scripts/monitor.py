import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from .predict import predict, load_resources

def load_config(file_path):
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

def send_discord_alert(message, webhook_url):
    print(f"Attempting to send Discord alert: {message}")
    if not webhook_url:
        print("Discord webhook URL not set")
        return

    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            raise Exception(f"Failed to send alert: {response.status_code} - {response.text}")
        print("Discord alert sent successfully.")
    except Exception as e:
        print(f"Error sending Discord alert: {e}")

def monitor_new_posts(discord_webhook_url):
    print("Starting to monitor new posts...")
    config = load_config('config/discord_config.txt')
    
    # 모델과 토크나이저 로드
    tokenizer, model = load_resources()
    if tokenizer is None or model is None:
        print("Error: Tokenizer or model is not loaded.")
        return

    # Selenium 설정
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://gall.dcinside.com/mgallery/board/lists?id=galaxy_tab')
        print("Selenium driver initialized and page loaded.")
    except Exception as e:
        print(f"Error setting up Selenium: {e}")
        return

    try:
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
    config = load_config('config/discord_config.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("Discord webhook URL not configured.")
        return

    print(f"Monitoring started with webhook URL: {discord_webhook_url}")
    monitor_new_posts(discord_webhook_url)
    print("Monitoring completed.")

def load_resources():
    import pickle
    from tensorflow.keras.models import load_model
    
    try:
        with open('artifacts/tokenizer.pkl', 'rb') as f:
            tokenizer = pickle.load(f)
        model = load_model('models/text_classification_model.h5')
        print("Resources loaded successfully.")
        return tokenizer, model
    except Exception as e:
        print(f"Error loading resources: {e}")
        return None, None
