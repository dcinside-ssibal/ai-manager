from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import os

# 외부 파일에서 로그인 정보 읽기
def load_login_info():
    with open('config/account.txt', 'r') as f:
        lines = f.readlines()
        user_id = lines[0].strip()
        user_password = lines[1].strip()
    return user_id, user_password

# Chrome 드라이버 설정
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 드라이버 자동 업데이트 및 관리
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# 로그인 처리
def login(driver, user_id, user_password):
    driver.get('https://sign.dcinside.com/login')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'id')))
    
    try:
        username = driver.find_element(By.ID, 'id')
        password = driver.find_element(By.ID, 'pw')
        
        username.send_keys(user_id)
        password.send_keys(user_password)
        
        login_button = driver.find_element(By.CLASS_NAME, 'btn_blue')
        login_button.click()

        # 비밀번호 변경 캠페인 페이지 처리
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'btn_grey'))
        )
        next_time_buttons = driver.find_elements(By.CLASS_NAME, 'btn_grey')
        if next_time_buttons:
            next_time_button = next_time_buttons[1]
            next_time_button.click()
    except Exception as e:
        print("비밀번호 변경 캠페인 페이지 대기 중 오류 발생:", e)
        page_source = driver.page_source
        with open('debug_login_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        driver.quit()
        exit()
    print("Login process completed.")

# 기존 게시물 로드
def load_existing_posts():
    try:
        with open('data/normal_posts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# 게시물 저장
def save_posts(posts):
    os.makedirs('data', exist_ok=True)
    with open('data/normal_posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)
