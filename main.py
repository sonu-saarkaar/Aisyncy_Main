import os
import json
import logging
import requests
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import (
    WHATSAPP_API_URL,
    WHATSAPP_TOKEN,
    VERIFY_TOKEN,
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    WHATSAPP_PHONE_NUMBER_ID
)

# Add this at the top to fix WhatsApp credentials
# Hardcoded WhatsApp API credentials
WHATSAPP_PHONE_NUMBER_ID = "104612292631543"
WHATSAPP_ACCESS_TOKEN = "EAAwFo4oYpGgBO8ZAgKQxZB7dxQY8XnArrLxRsvuhZARG8NJVwQPiJ15EuJq30fV1x4eohl7zT4tHwegGaBcpqtVZADA8QOLKgJwL92etZC7HbZCeujbtr01yxcbFiZBFMUtfPr8RtriO8ZCxXCSWUvMxOynVhmy4ZBHtUzcbTGzLxPUdnIJMeyolNKjcpD376l1WZAJQZDZD"  
WHATSAPP_TOKEN = WHATSAPP_ACCESS_TOKEN
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
VERIFY_TOKEN = "12345"

print("HARDCODED CREDENTIALS LOADED IN MAIN.PY")

# Import ChatFlowController for the recharge flow
from src.chatflow.ChatFlowController_new import RechargeController

# Initialize RechargeController for handling conversational flows
recharge_controller = RechargeController()

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# MongoDB configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB = os.environ.get('MONGO_DB', 'aisyncy_recharge')

try:
    # Connect to MongoDB
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
    db = None

# Add file handler for persistent logging
if not app.debug:
    file_handler = logging.FileHandler('webhook.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    ))
    logger.addHandler(file_handler)

def send_whatsapp_message(to_number, message_or_data):
    """
    Send a WhatsApp message or interactive message
    
    to_number: recipient's phone number
    message_or_data: Either a string for text messages or a complete WhatsApp API payload
    """
    try:
        # Check for the placeholder value in the WHATSAPP_PHONE_NUMBER_ID
        if not WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_PHONE_NUMBER_ID == 'default_phone_number_id':
            logger.error("❌ WhatsApp Phone Number ID not properly configured - found: default_phone_number_id")
            logger.error("Please set the correct WHATSAPP_PHONE_NUMBER_ID in your environment variables")
            return {"error": "WhatsApp Phone Number ID not properly configured", "status": "failed"}
            
        if not WHATSAPP_TOKEN:
            logger.error("❌ WhatsApp token not configured - check environment variables")
            return {"error": "WhatsApp token not configured", "status": "failed"}
            
        if not WHATSAPP_API_URL:
            logger.error("❌ WhatsApp API URL not configured - check environment variables")
            return {"error": "WhatsApp API URL not configured", "status": "failed"}
        
        # Debug information about the configuration    
        logger.debug(f"Using WhatsApp Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")
        logger.debug(f"Using WhatsApp API URL: {WHATSAPP_API_URL}")
            
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # If message_or_data is a string, create a text message payload
        if isinstance(message_or_data, str):
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
                "text": {"body": message_or_data}
            }
            
            logger.info(f"📤 Sending text message to {to_number}: {message_or_data}")
        else:
            # If it's already a complete payload (e.g., for interactive messages)
            data = message_or_data
            logger.info(f"📤 Sending complex message to {data.get('to')}")
        
        logger.debug(f"Request URL: {WHATSAPP_API_URL}")
        logger.debug(f"Request headers: {json.dumps({k: '**REDACTED**' if k == 'Authorization' else v for k, v in headers.items()})}")
        logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(WHATSAPP_API_URL, headers=headers, json=data, timeout=10)
            logger.info(f"WhatsApp API Response Status: {response.status_code}")
            logger.debug(f"WhatsApp API Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"✅ Message sent successfully, Message ID: {response_data.get('messages', [{}])[0].get('id', 'unknown')}")
                return response_data
            elif response.status_code == 401:
                logger.error("❌ WhatsApp API Authentication Error (401 Unauthorized)")
                logger.error("Your WhatsApp access token is invalid or expired")
                logger.error("Please update your WHATSAPP_ACCESS_TOKEN environment variable")
                return {"error": "WhatsApp API Authentication Error", "status": "failed"}
            else:
                logger.error(f"❌ WhatsApp API error: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {json.dumps(error_data)}")
                    return {"error": f"WhatsApp API error: {error_data.get('error', {}).get('message', 'Unknown error')}", "status": "failed"}
                except:
                    return {"error": f"WhatsApp API error: HTTP {response.status_code}", "status": "failed"}
                
        except requests.exceptions.Timeout:
            logger.error("❌ WhatsApp API request timed out")
            return {"error": "Request timed out", "status": "failed"}
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error sending WhatsApp message: {str(e)}")
            return {"error": f"Network error: {str(e)}", "status": "failed"}
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {str(e)}", exc_info=True)
        return {"error": str(e), "status": "failed"}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def hello():
    return "Hello from Aisyncy!"

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error="Invalid credentials")
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        # Initialize default values
        context = {
            'total_customers': 0,
            'total_recharges': 0,
            'total_revenue': 0,
            'recent_transactions': [],
            'active_users': 0,
            'pending_recharges': 0,
            'failed_recharges': 0,
            'success_rate': 0
        }
        
        # Add error handling for database operations
        try:
            # Get total customers
            total_customers = db.users.count_documents({})
            context['total_customers'] = total_customers

            # Get total recharges
            total_recharges = db.recharges.count_documents({})
            context['total_recharges'] = total_recharges

            # Calculate total revenue
            pipeline = [
                {"$match": {"status": "success"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            result = list(db.recharges.aggregate(pipeline))
            if result:
                context['total_revenue'] = result[0]['total']

            # Get recent transactions
            recent_transactions = list(db.recharges.find().sort('timestamp', -1).limit(10))
            context['recent_transactions'] = recent_transactions

            # Calculate success rate
            successful_recharges = db.recharges.count_documents({"status": "success"})
            if total_recharges > 0:
                context['success_rate'] = (successful_recharges / total_recharges) * 100

            # Get active users (users who made a recharge in the last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_users = db.recharges.distinct('user_id', {
                'timestamp': {'$gte': thirty_days_ago}
            })
            context['active_users'] = len(active_users)

            # Get pending recharges
            context['pending_recharges'] = db.recharges.count_documents({"status": "pending"})

            # Get failed recharges
            context['failed_recharges'] = db.recharges.count_documents({"status": "failed"})

        except Exception as db_error:
            logger.error(f"Database error in admin dashboard: {str(db_error)}", exc_info=True)
            # Keep the default values in case of database error
        
        return render_template('admin/home.html', **context)
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}", exc_info=True)
        return render_template('admin/error.html', error=str(e))

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    try:
        logger.debug(f"Received {request.method} request to webhook")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"URL: {request.url}")
        logger.debug(f"Args: {request.args}")
        
        if request.method == 'GET':
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            logger.info(f"Webhook verification - Mode: {mode}, Token: {token}, Challenge: {challenge}")
            
            if mode and token:
                if mode == 'subscribe' and token == VERIFY_TOKEN:
                    logger.info("✅ Webhook verified successfully!")
                    return challenge
                logger.warning("❌ Invalid verification token")
                return "Invalid verification token", 403
            
            logger.warning("❌ Missing verification parameters")
            return "Missing verification parameters", 400

        elif request.method == 'POST':
            logger.debug("📥 Received webhook POST request")
            logger.debug(f"Content-Type: {request.content_type}")
            
            body = request.get_data()
            logger.debug(f"Raw body: {body.decode()}")

            if not request.is_json:
                logger.warning("❌ Request is not JSON")
                return jsonify({"error": "Content type must be application/json"}), 400

            data = request.get_json()
            logger.info(f"📝 Webhook data: {json.dumps(data, indent=2)}")
            
            try:
                if data.get('object') == 'whatsapp_business_account':
                    logger.info("✉️ Processing WhatsApp message")
                    
                    for entry in data.get('entry', []):
                        for change in entry.get('changes', []):
                            if change.get('value', {}).get('messages'):
                                for message in change['value']['messages']:
                                    from_number = message.get('from')
                                    message_id = message.get('id', '')
                                    
                                    # Handle different message types
                                    if 'text' in message:
                                        message_body = message.get('text', {}).get('body', '')
                                        logger.info(f"📱 Text message - From: {from_number}, Body: {message_body}, ID: {message_id}")
                                        
                                        # Use the RechargeController to process the message
                                        response_payload = recharge_controller.process_recharge(from_number, message_body)
                                        
                                        # Send the response from the chatflow
                                        send_result = send_whatsapp_message(from_number, response_payload)
                                        logger.info(f"📤 Response sent using chatflow")
                                        logger.debug(f"Response payload: {json.dumps(response_payload)}")
                                        
                                    elif 'interactive' in message:
                                        interactive = message.get('interactive', {})
                                        logger.info(f"📱 Interactive message - From: {from_number}, Type: {interactive.get('type')}")
                                        
                                        # Handle button responses
                                        if interactive.get('type') == 'button_reply':
                                            button_id = interactive.get('button_reply', {}).get('id', '')
                                            logger.info(f"Button clicked: {button_id}")
                                            
                                            # Process the button click through the chatflow
                                            response_payload = recharge_controller.process_recharge(from_number, button_id)
                                            send_result = send_whatsapp_message(from_number, response_payload)
                                            logger.info(f"📤 Response sent for button click: {button_id}")
                                        
                                        # Handle list responses
                                        elif interactive.get('type') == 'list_reply':
                                            list_id = interactive.get('list_reply', {}).get('id', '')
                                            logger.info(f"List item selected: {list_id}")
                                            
                                            # Process the list selection through the chatflow
                                            response_payload = recharge_controller.process_recharge(from_number, list_id)
                                            send_result = send_whatsapp_message(from_number, response_payload)
                                            logger.info(f"📤 Response sent for list selection: {list_id}")
                                    
                                    # Add other message types as needed (location, image, etc.)
                                    else:
                                        logger.info(f"📱 Unsupported message type from: {from_number}, ID: {message_id}")
                                        
                                        # Send a default response for unsupported message types
                                        send_whatsapp_message(from_number, "Sorry, I can only process text messages and interactions at this time.")
                                    
                                    return jsonify({
                                        "status": "success",
                                        "message": "Message processed successfully"
                                    })
                
                logger.info("ℹ️ No messages to process")
                return jsonify({"status": "success", "message": "No messages to process"})
            
            except Exception as e:
                logger.error(f"❌ Error processing webhook data: {str(e)}", exc_info=True)
                return jsonify({"error": f"Error processing message: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/webhook_test', methods=['GET'])
def webhook_test():
    """Test endpoint to verify webhook functionality"""
    try:
        # Check if WhatsApp credentials are configured
        credentials_status = {
            "whatsapp_phone_number_id": bool(WHATSAPP_PHONE_NUMBER_ID),
            "whatsapp_access_token": bool(WHATSAPP_ACCESS_TOKEN),
            "webhook_url": f"{request.url_root}webhook"
        }
        
        # Log diagnostic information
        logger.info(f"WhatsApp webhook test - Credentials status: {json.dumps(credentials_status)}")
        
        return jsonify({
            "status": "success",
            "message": "Webhook test endpoint is working",
            "credentials_status": credentials_status,
            "environment": {
                "WHATSAPP_PHONE_NUMBER_ID": WHATSAPP_PHONE_NUMBER_ID,
                "WHATSAPP_API_URL": WHATSAPP_API_URL,
                "VERIFY_TOKEN": VERIFY_TOKEN
            }
        })
    except Exception as e:
        logger.error(f"Error in webhook test: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test_webhook', methods=['GET'])
def test_webhook():
    # Simulate a WhatsApp message for testing
    test_data = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "text": {"body": "Test message"}
                    }]
                }
            }]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            f"https://{request.host}/webhook",
            json=test_data,
            headers=headers
        )
        return jsonify({
            "status": "success",
            "test_response": response.json(),
            "status_code": response.status_code
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.path}")
    if request.path.startswith('/admin/'):
        return render_template('admin/error.html', error="Page not found"), 404
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 error: {str(error)}")
    if request.path.startswith('/admin/'):
        return render_template('admin/error.html', error="Internal server error"), 500
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port) 