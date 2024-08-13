import requests

def send_discord_alert(message, webhook_url):
    """
    Sends a message to a Discord channel via a webhook URL.
    
    Args:
        message (str): The message content to be sent.
        webhook_url (str): The Discord webhook URL.
    """
    if not webhook_url:
        print("Discord webhook URL not set.")
        return

    data = {"content": message}
    
    try:
        print(f"Attempting to send Discord alert: {message}")
        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 204:
            print("Discord alert sent successfully.")
        else:
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    
    except requests.RequestException as e:
        print(f"Error sending Discord alert: {e}")
        # Optional: Log more detailed error information or notify someone.
