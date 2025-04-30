from dotenv import load_dotenv
import os
import requests

# Load from the local directory (.env next to manage.py)
load_dotenv()

def send_sms(to_number, message_body):
    api_key = os.getenv('SEMAPHORE_API_KEY')
    sender_name = os.getenv('SENDER_NAME')

    if not api_key or not sender_name:
        print("Environment variables missing!")
        return None

    payload = {
        'apikey': api_key,
        'number': to_number,
        'message': message_body,
        'sendername': sender_name
    }

    response = requests.post('https://api.semaphore.co/api/v4/messages', data=payload)

    print("Payload:", payload)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    try:
        return response.json()
    except Exception as e:
        print("Error parsing JSON:", e)
        return None
