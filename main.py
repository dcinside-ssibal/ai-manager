import os
import threading
import schedule
import time
from scripts import (
    scrape_block_list, scrape_delete_list, scrape_normal_posts,
    prepare_data, train_model, monitor_new_posts, load_config
)

def setup_schedule(discord_webhook_url):
    schedule.every().day.at("00:00").do(scrape_block_list)
    schedule.every().day.at("00:15").do(scrape_delete_list)
    schedule.every().day.at("00:30").do(scrape_normal_posts)
    schedule.every().day.at("01:00").do(prepare_data_and_train_model)
    schedule.every(5).minutes.do(lambda: monitor_new_posts(discord_webhook_url))

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def prepare_data_and_train_model():
    model_path = 'models/text_classification_model.keras'
    if not os.path.exists(model_path):
        prepare_data()
        train_model()

def main():
    config = load_config('config/discord.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("Discord webhook URL not found in config.")
        return

    scrape_normal_posts()
    scrape_block_list()
    scrape_delete_list()
    
    prepare_data_and_train_model()

    monitor_new_posts(discord_webhook_url)

    try:
        setup_schedule(discord_webhook_url)
        schedule_thread = threading.Thread(target=run_schedule, name='ScheduleThread')
        schedule_thread.start()
        schedule_thread.join()
    except Exception as e:
        print(f"Error in schedule thread: {e}")

if __name__ == "__main__":
    main()
