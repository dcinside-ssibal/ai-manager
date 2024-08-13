import threading
import schedule
import time
from scripts.data_preparation import prepare_data
from scripts.train_model import train_model
from scripts.predict import load_resources, predict_text
from scripts.scraper import scrape_block_list, scrape_delete_list, scrape_monitored_posts
from scripts.monitor import monitor_new_posts, load_config

def setup_schedule(discord_webhook_url):
    schedule.every().hour.do(scrape_block_list)
    schedule.every().hour.do(scrape_delete_list)
    schedule.every().hour.do(scrape_monitored_posts)
    schedule.every(1).minute.do(lambda: monitor_new_posts(discord_webhook_url))  # 매 1분마다 모니터링

def run_schedule(discord_webhook_url):
    setup_schedule(discord_webhook_url)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    # 설정 파일에서 Discord webhook URL 로드
    config = load_config('config/discord_config.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("Error: Discord webhook URL is not configured.")
        return

    # 크롤링 스크립트 실행
    print("Starting web scraping...")
    scrape_monitored_posts()
    scrape_block_list()
    scrape_delete_list()
    print("Web scraping completed.")

    # 데이터 준비 및 모델 학습
    print("Starting data preparation...")
    prepare_data()
    print("Data preparation completed.")
    
    print("Starting model training...")
    train_model()
    print("Model training completed.")
    
    # 예측 예제
    print("Starting prediction...")
    tokenizer, model = load_resources()
    if tokenizer and model:
        prediction_result = predict_text("예시 텍스트", tokenizer, model)
        print(f"Prediction result: {prediction_result}")
    else:
        print("Error: Failed to load resources for prediction.")
    print("Prediction completed.")
    
    # 크롤링 스케줄 스레드
    try:
        schedule_thread = threading.Thread(target=lambda: run_schedule(discord_webhook_url), name='ScheduleThread')
        schedule_thread.start()

        # 모든 스레드가 종료될 때까지 대기
        schedule_thread.join()
    except Exception as e:
        print(f"Error in threading setup: {e}")

if __name__ == "__main__":
    main()
