import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import os

def load_login_info():
    try:
        with open('config/account.txt', 'r') as f:
            lines = f.readlines()
            return lines[0].strip(), lines[1].strip()
    except Exception as e:
        print(f"Error loading login info: {e}")
        return None, None

def get_chromedriver_path():
    try:
        result = subprocess.run(['which', 'chromedriver'], stdout=subprocess.PIPE, text=True)
        path = result.stdout.strip()
        if path:
            return path
        print("ChromeDriver not found.")
    except Exception as e:
        print(f"Error finding ChromeDriver: {e}")
    return None

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    chrome_driver_path = get_chromedriver_path()
    if not chrome_driver_path:
        return None

    try:
        service = Service(chrome_driver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

def login(driver, user_id, user_password):
    driver.get('https://sign.dcinside.com/login')
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'id')))
        driver.find_element(By.ID, 'id').send_keys(user_id)
        driver.find_element(By.ID, 'pw').send_keys(user_password)
        driver.find_element(By.CLASS_NAME, 'btn_blue').click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn_grey')))
        next_time_buttons = driver.find_elements(By.CLASS_NAME, 'btn_grey')
        if next_time_buttons:
            next_time_buttons[1].click()
    except Exception as e:
        print(f"Error during login: {e}")
        with open('debug_login_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.quit()
        exit()

def load_existing_posts():
    try:
        with open('data/normal_posts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON from normal_posts.json.")
        return []

def save_posts(posts):
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/normal_posts.json', 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving posts: {e}")
