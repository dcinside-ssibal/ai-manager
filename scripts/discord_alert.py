import requests

def send_discord_alert(message, webhook_url):
    if not webhook_url:
        return

    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending Discord alert: {e}")
