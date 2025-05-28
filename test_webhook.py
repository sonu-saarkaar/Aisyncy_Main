#!/usr/bin/env python3
import requests
import json
import sys
import argparse

def test_webhook_verification(base_url, verify_token="12345"):
    """Test the GET webhook verification endpoint"""
    try:
        url = f"{base_url.rstrip('/')}/webhook?hub.mode=subscribe&hub.verify_token={verify_token}&hub.challenge=CHALLENGE_ACCEPTED"
        print(f"Testing webhook verification at: {url}")
        
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 and response.text == "CHALLENGE_ACCEPTED":
            print("\n✅ Webhook verification successful!")
            return True
        else:
            print("\n❌ Webhook verification failed!")
            return False
    except Exception as e:
        print(f"\n❌ Error testing webhook verification: {str(e)}")
        return False

def test_webhook_message(base_url):
    """Test the POST webhook message handling endpoint"""
    try:
        url = f"{base_url.rstrip('/')}/webhook"
        print(f"Testing webhook message handling at: {url}")
        
        # Sample WhatsApp message payload
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "ENTRY_ID",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "PHONE_NUMBER",
                                    "phone_number_id": "PHONE_NUMBER_ID"
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "Test User"},
                                        "wa_id": "919876543210"
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "919876543210",
                                        "id": "wamid.TEST_MESSAGE_ID",
                                        "timestamp": "1639138950",
                                        "text": {
                                            "body": "This is a test message"
                                        },
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if 200 <= response.status_code < 300:
            print("\n✅ Webhook message test successful!")
            return True
        else:
            print("\n❌ Webhook message test failed!")
            return False
    except Exception as e:
        print(f"\n❌ Error testing webhook message: {str(e)}")
        return False

def test_webhook_diagnostics(base_url):
    """Test the webhook diagnostics endpoint"""
    try:
        url = f"{base_url.rstrip('/')}/webhook_test"
        print(f"Testing webhook diagnostics at: {url}")
        
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            print("\n✅ Webhook diagnostics successful!")
            return True
        else:
            print(f"Response: {response.text}")
            print("\n❌ Webhook diagnostics failed!")
            return False
    except Exception as e:
        print(f"\n❌ Error testing webhook diagnostics: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test WhatsApp webhook functionality")
    parser.add_argument('url', help='Base URL of your deployed application (e.g., https://your-app.run.app)')
    parser.add_argument('--token', default="12345", help='Webhook verification token (default: 12345)')
    
    args = parser.parse_args()
    
    print("\n===== WhatsApp Webhook Test Tool =====\n")
    
    # First check diagnostics
    print("\n----- Testing Webhook Diagnostics -----")
    test_webhook_diagnostics(args.url)
    
    # Test verification
    print("\n----- Testing Webhook Verification -----")
    test_webhook_verification(args.url, args.token)
    
    # Test message handling
    print("\n----- Testing Webhook Message Handling -----")
    test_webhook_message(args.url)

    print("\n===== Test Complete =====\n") 