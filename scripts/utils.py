from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import os

def load_login_info():
    """
    Load login credentials from a configuration file.
    
    Returns:
        tuple: A tuple containing user ID and password.
    """
    try:
        with open('config/account.txt', 'r') as f:
            lines = f.readlines()
            user_id = lines[0].strip()
            user_password = lines[1].strip()
        return user_id, user_password
    except Exception as e:
        print(f"Error loading login info: {e}")
        return None, None

def setup_driver():
    """
    Set up the Selenium WebDriver with Chrome options.
    
    Returns:
        webdriver.Chrome: Configured WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

def login(driver, user_id, user_password):
    """
    Perform login using provided credentials.
    
    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        user_id (str): User ID for login.
        user_password (str): User password for login.
    """
    driver.get('https://sign.dcinside.com/login')
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'id')))
        username = driver.find_element(By.ID, 'id')
        password = driver.find_element(By.ID, 'pw')
        
        username.send_keys(user_id)
        password.send_keys(user_password)
        
        login_button = driver.find_element(By.CLASS_NAME, 'btn_blue')
        login_button.click()

        # Handle the password change campaign page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'btn_grey'))
        )
        next_time_buttons = driver.find_elements(By.CLASS_NAME, 'btn_grey')
        if next_time_buttons:
            next_time_button = next_time_buttons[1]
            next_time_button.click()
        print("Login process completed.")
    except Exception as e:
        print(f"Error during login process: {e}")
        page_source = driver.page_source
        with open('debug_login_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        driver.quit()
        exit()

def load_existing_posts():
    """
    Load existing posts from the JSON file.
    
    Returns:
        list: A list of existing posts.
    """
    try:
        with open('data/normal_posts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON from normal_posts.json.")
        return []

def save_posts(posts):
    """
    Save the list of posts to the JSON file.
    
    Args:
        posts (list): List of posts to be saved.
    """
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/normal_posts.json', 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving posts: {e}")
