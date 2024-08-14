import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_login_info():
    try:
        with open('config/account.txt', 'r') as f:
            return f.readline().strip(), f.readline().strip()
    except Exception as e:
        print(f"Error loading login info: {e}")
        return None, None

def get_chromedriver_path():
    try:
        result = subprocess.run(['which', 'chromedriver'], stdout=subprocess.PIPE, text=True)
        return result.stdout.strip() or None
    except Exception as e:
        print(f"Error finding ChromeDriver: {e}")
        return None

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    path = get_chromedriver_path()
    if not path:
        print("ChromeDriver not found.")
        return None

    try:
        return webdriver.Chrome(service=Service(path), options=options)
    except Exception as e:
        print(f"Error setting up ChromeDriver: {e}")
        return None

def login(driver, user_id, user_password):
    driver.get('https://sign.dcinside.com/login')
    
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'id')))
        driver.find_element(By.ID, 'id').send_keys(user_id)
        driver.find_element(By.ID, 'pw').send_keys(user_password)
        driver.find_element(By.CLASS_NAME, 'btn_blue').click()

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn_grey')))
        buttons = driver.find_elements(By.CLASS_NAME, 'btn_grey')
        if buttons:
            buttons[1].click()
    except Exception as e:
        print(f"Error during login: {e}")
        with open('debug_login_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.quit()
        exit()
