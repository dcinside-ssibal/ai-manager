import os
import threading
import schedule
import time
from scripts import (
    load_data, preprocess_data, tokenize_and_pad, save_prepared_data,
    train_model, load_resources, predict_text,
    scrape_block_list, scrape_delete_list, scrape_normal_posts,
    monitor_new_posts, load_config
)

def setup_schedule(discord_webhook_url):
    """스케줄을 설정합니다."""
    schedule.every().day.at("00:00").do(scrape_block_list)
    schedule.every().day.at("00:30").do(scrape_delete_list)
    schedule.every().day.at("01:00").do(scrape_normal_posts)
    
    schedule.every().day.at("01:30").do(prepare_data)
    schedule.every().day.at("02:00").do(train_model)

    schedule.every(5).minutes.do(lambda: monitor_new_posts(discord_webhook_url))

def run_schedule(discord_webhook_url):
    """스케줄을 실행하는 무한 루프를 시작합니다."""
    setup_schedule(discord_webhook_url)
    while True:
        schedule.run_pending()
        time.sleep(1)

def prepare_data():
    """데이터를 준비하는 메인 함수."""
    print("데이터 준비 시작")
    block_list, delete_list, normal_posts = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(block_list, delete_list, normal_posts)
    tokenizer, X_train_pad, X_test_pad = tokenize_and_pad(X_train, X_test)
    save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test)
    print("데이터 준비 완료")

def main():
    """메인 함수: 설정 및 데이터 처리, 스케줄링을 수행합니다."""
    config = load_config('config/discord.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("Discord Webhook URL이 설정되지 않았습니다.")
        return
    
    print("스크래핑 시작")
    scrape_normal_posts()
    scrape_block_list()
    scrape_delete_list()
    print("스크래핑 완료")
    
    print("모델 준비 시작")
    
    model_path = 'models/text_classification_model.keras'
    if not os.path.exists(model_path):
        # 모델이 존재하지 않으면 데이터 준비 및 모델 학습
        prepare_data()
        train_model()
        print("모델 학습 완료")
    else:
        print("모델이 이미 존재합니다. 모델 학습을 건너뜁니다.")

    monitor_new_posts(discord_webhook_url)

    try:
        schedule_thread = threading.Thread(target=lambda: run_schedule(discord_webhook_url), name='ScheduleThread')
        schedule_thread.start()
        schedule_thread.join()
    except Exception as e:
        print(f"스케줄 스레드에서 오류 발생: {e}")

if __name__ == "__main__":
    main()
