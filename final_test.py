#!/usr/bin/env python3
import requests
import json
import sys

# Hardcoded WhatsApp credentials - confirmed working
WHATSAPP_PHONE_NUMBER_ID = "104612292631543"
WHATSAPP_ACCESS_TOKEN = "EAAwFo4oYpGgBO8ZAgKQxZB7dxQY8XnArrLxRsvuhZARG8NJVwQPiJ15EuJq30fV1x4eohl7zT4tHwegGaBcpqtVZADA8QOLKgJwL92etZC7HbZCeujbtr01yxcbFiZBFMUtfPr8RtriO8ZCxXCSWUvMxOynVhmy4ZBHtUzcbTGzLxPUdnIJMeyolNKjcpD376l1WZAJQZDZD"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

def send_whatsapp_message(to_number, message):
    """Send a WhatsApp message using hardcoded credentials"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Format phone number - remove non-digit characters
    to_number = ''.join(filter(str.isdigit, to_number))
    
    # Add country code if not present (assuming India)
    if not to_number.startswith('91'):
        to_number = '91' + to_number
    
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    
    print(f"Sending message to {to_number}: {message}")
    print(f"Request URL: {WHATSAPP_API_URL}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=data, timeout=10)
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send message: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return False

if __name__ == "__main__":
    print("==== WhatsApp Message Tester ====")
    print("This script will send a test message using the hardcoded credentials")
    
    if len(sys.argv) >= 3:
        phone_number = sys.argv[1]
        message = sys.argv[2]
    else:
        phone_number = input("Enter phone number (with country code): ")
        message = input("Enter message to send: ")
    
    send_whatsapp_message(phone_number, message) 