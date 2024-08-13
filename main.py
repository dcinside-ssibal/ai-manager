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
    """
    Sets up the schedule for periodic tasks.
    
    Args:
        discord_webhook_url (str): The URL for Discord webhook.
    """
    schedule.every().hour.do(scrape_block_list)
    schedule.every().hour.do(scrape_delete_list)
    schedule.every().hour.do(scrape_normal_posts)
    schedule.every(1).minute.do(lambda: monitor_new_posts(discord_webhook_url))  # Monitor every minute

def run_schedule(discord_webhook_url):
    """
    Runs the schedule for periodic tasks in a loop.
    
    Args:
        discord_webhook_url (str): The URL for Discord webhook.
    """
    setup_schedule(discord_webhook_url)
    while True:
        schedule.run_pending()
        time.sleep(1)

def prepare_data():
    """
    Prepares data for model training by loading, preprocessing, and saving it.
    """
    block_list, delete_list = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(block_list, delete_list)
    tokenizer, X_train_pad, X_test_pad = tokenize_and_pad(X_train, X_test)
    save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test)

def main():
    """
    Main function to execute the entire process: scraping, data preparation, model training, and scheduling.
    """
    # Load configuration from file
    config = load_config('config/discord.txt')
    discord_webhook_url = config.get('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("Error: Discord webhook URL is not configured.")
        return

    # Run web scraping scripts
    print("Starting web scraping...")
    scrape_normal_posts()
    scrape_block_list()
    scrape_delete_list()
    print("Web scraping completed.")

    # Data preparation and model training
    print("Starting data preparation...")
    prepare_data()
    print("Data preparation completed.")
    
    print("Starting model training...")
    train_model()
    print("Model training completed.")
    
    
    # Start the scraping schedule in a separate thread
    try:
        schedule_thread = threading.Thread(target=lambda: run_schedule(discord_webhook_url), name='ScheduleThread')
        schedule_thread.start()

        # Wait for the schedule thread to finish
        schedule_thread.join()
    except Exception as e:
        print(f"Error in threading setup: {e}")

if __name__ == "__main__":
    main()
