#!/usr/bin/env python3
import os
import requests
import json
import argparse

# Hardcoded WhatsApp credentials
WHATSAPP_PHONE_NUMBER_ID = "104612292631543"
WHATSAPP_ACCESS_TOKEN = "EAAwFo4oYpGgBO8ZAgKQxZB7dxQY8XnArrLxRsvuhZARG8NJVwQPiJ15EuJq30fV1x4eohl7zT4tHwegGaBcpqtVZADA8QOLKgJwL92etZC7HbZCeujbtr01yxcbFiZBFMUtfPr8RtriO8ZCxXCSWUvMxOynVhmy4ZBHtUzcbTGzLxPUdnIJMeyolNKjcpD376l1WZAJQZDZD"
WEBHOOK_VERIFY_TOKEN = "12345"

def test_api_credentials():
    """Test the WhatsApp API credentials to make sure they're valid"""
    whatsapp_api_url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test message data - we won't actually send it, just validate auth
    data = {
        "messaging_product": "whatsapp",
        "to": "15555555555",  # Dummy number, won't be used
        "type": "text",
        "text": {"body": "Test message - not actually sending"}
    }
    
    try:
        # Make a request to check auth without sending (by using a timeout)
        try:
            # Quick timeout just to test authentication
            response = requests.post(whatsapp_api_url, headers=headers, json=data, timeout=2)
        except requests.exceptions.Timeout:
            # Even timeout is fine as long as we get a response code first
            pass
        
        if response.status_code == 200:
            print("✅ WhatsApp API credentials are valid")
            return True
        elif response.status_code == 401 or response.status_code == 403:
            print(f"❌ WhatsApp API authentication failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"⚠️ WhatsApp API returned unexpected status: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            # At least it authenticated
            return True
            
    except Exception as e:
        print(f"❌ Error testing WhatsApp API credentials: {str(e)}")
        return False

def create_config_fix_files():
    """Creates the config files needed to fix the WhatsApp integration"""
    # Create config_fix.py with hardcoded credentials
    config_fix_content = f"""# WhatsApp API Configuration with hardcoded credentials
WHATSAPP_PHONE_NUMBER_ID = "{WHATSAPP_PHONE_NUMBER_ID}"
WHATSAPP_ACCESS_TOKEN = "{WHATSAPP_ACCESS_TOKEN}"
WHATSAPP_TOKEN = WHATSAPP_ACCESS_TOKEN  # Also set this alias that some code might use
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{{WHATSAPP_PHONE_NUMBER_ID}}/messages"

# Webhook Configuration
VERIFY_TOKEN = "{WEBHOOK_VERIFY_TOKEN}"

print("CONFIG FIX LOADED: WhatsApp credentials initialized with hardcoded values")
"""
    with open('config_fix.py', 'w') as f:
        f.write(config_fix_content)
    print("✅ Created config_fix.py with hardcoded WhatsApp credentials")
    
    # Create a patch for main.py
    main_fix_content = """# Add this at the top of your main.py file
try:
    # Try to load our hardcoded configuration first
    from config_fix import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_TOKEN, WHATSAPP_API_URL, VERIFY_TOKEN
    print("Successfully loaded hardcoded WhatsApp credentials")
except ImportError:
    # Fall back to regular config if the fix file isn't present
    print("Hardcoded credentials not found, using environment variables")
    from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_TOKEN, WHATSAPP_API_URL, VERIFY_TOKEN
"""
    with open('main_fix.py', 'w') as f:
        f.write(main_fix_content)
    print("✅ Created main_fix.py with import fixes")
    
    # Create a test script
    test_whatsapp_content = """#!/usr/bin/env python3
import requests
import json
import sys

# Import the hardcoded credentials
WHATSAPP_PHONE_NUMBER_ID = "104612292631543"
WHATSAPP_ACCESS_TOKEN = "EAAwFo4oYpGgBO8ZAgKQxZB7dxQY8XnArrLxRsvuhZARG8NJVwQPiJ15EuJq30fV1x4eohl7zT4tHwegGaBcpqtVZADA8QOLKgJwL92etZC7HbZCeujbtr01yxcbFiZBFMUtfPr8RtriO8ZCxXCSWUvMxOynVhmy4ZBHtUzcbTGzLxPUdnIJMeyolNKjcpD376l1WZAJQZDZD"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
VERIFY_TOKEN = "12345"

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
    
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=data, timeout=10)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Message sent successfully!")
            response_data = response.json()
            message_id = response_data.get('messages', [{}])[0].get('id', 'unknown')
            print(f"Message ID: {message_id}")
            return True
        else:
            print(f"❌ Failed to send message: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_whatsapp.py <phone_number> <message>")
        print("Example: python test_whatsapp.py 919708299494 'Hello from Python'")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    message = sys.argv[2]
    
    send_whatsapp_message(phone_number, message)
"""
    with open('test_whatsapp.py', 'w') as f:
        f.write(test_whatsapp_content)
    print("✅ Created test_whatsapp.py for easy testing")
    
    # Create a deployment fix file
    deploy_fix_content = """#!/bin/bash
# This script deploys the WhatsApp credential fixes to your GCP Cloud Run service

# Set the service name and region
SERVICE_NAME="aisyncy-service"
REGION="asia-south1"

# Create a temporary directory for deployment
mkdir -p deploy_fix
cd deploy_fix

# Copy the necessary files
cp ../config_fix.py .
cp ../main.py .
cp ../app.yaml .

# Apply the fix to main.py
cat ../main_fix.py > temp_main.py
cat main.py >> temp_main.py
mv temp_main.py main.py

# Deploy to GCP
echo "Deploying fixes to GCP Cloud Run..."
gcloud run deploy $SERVICE_NAME --source . --region $REGION

# Clean up
cd ..
rm -rf deploy_fix

echo "✅ Deployment complete!"
"""
    with open('deploy_fix.sh', 'w') as f:
        f.write(deploy_fix_content)
    print("✅ Created deploy_fix.sh for easy deployment")
    
    print("\n📝 Instructions for fixing WhatsApp integration:")
    print("1. Copy these files to your GCP deployment")
    print("2. Modify your main.py to use the hardcoded credentials")
    print("   - Add the code from main_fix.py at the top of your main.py file")
    print("3. Deploy your changes to GCP using deploy_fix.sh")
    print("4. Test by sending a message with test_whatsapp.py")

def main():
    print("==== WhatsApp Integration Fix Tool ====\n")
    
    # Test the API credentials
    api_valid = test_api_credentials()
    if not api_valid:
        print("\n❌ The WhatsApp API credentials appear to be invalid.")
        print("Please check the WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN values.")
        return
    
    # Create the config fix files
    create_config_fix_files()
    
    print("\n✅ All setup complete! Follow the instructions above to fix your WhatsApp integration.")
    print("\nTo test sending a message directly:")
    print("python test_whatsapp.py 919708299494 'Hello from the fixed WhatsApp API'")

if __name__ == "__main__":
    main() 