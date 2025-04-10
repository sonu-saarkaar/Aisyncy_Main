import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, request, Response, jsonify, render_template, session, redirect, url_for
import requests
import logging
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime, timedelta
import os
try:
    from src.chatflow.ChatFlowController import RechargeController  # type: ignore
    recharge_controller = RechargeController()  # Initialize RechargeController
except ModuleNotFoundError:
    logging.error("Module 'ChatFlowController' could not be imported. Ensure it exists in 'src/chatflow'.")
    recharge_controller = None  # Set to None to avoid runtime errors
try:
    from src.error_handler import register_error_handlers  # Adjusted import for error_handler
except ImportError:
    logging.warning("Module 'src.error_handler' could not be imported. Ensure it exists.")

try:
    from src.config import (
        SECRET_KEY, MONGO_URI, ADMIN_USERNAME, ADMIN_PASSWORD,
        WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, LOG_LEVEL
    )  # Adjusted import for config
except ImportError:
    logging.warning("Module 'src.config' could not be imported. Ensure it exists.")
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_socketio import SocketIO, emit

# Load environment variables
load_dotenv()
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')  # Added missing variable
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')        # Added missing variable
logging.info(f"Admin username configured: {ADMIN_USERNAME is not None}")
logging.info(f"Admin password configured: {ADMIN_PASSWORD is not None}")
logging.info(f"WhatsApp Phone Number ID configured: {WHATSAPP_PHONE_NUMBER_ID is not None}")
logging.info(f"WhatsApp Access Token configured: {WHATSAPP_ACCESS_TOKEN is not None}")

app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(level=LOG_LEVEL)
VERIFY_TOKEN = "12345"

csrf = CSRFProtect(app)

# MongoDB Connection
try:
    mongo_client = MongoClient(os.getenv('MONGO_URI'))
    db = mongo_client.get_database('aisyncy')
    logging.info("Connected to MongoDB successfully!")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {str(e)}")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def home():
    return "Server is running!"

def send_whatsapp_message(phone_number, message):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if isinstance(message, dict):
        data = message
        data['to'] = phone_number
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        return False

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                return challenge
            return "Forbidden", 403
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'object' not in data:
                return "Invalid request", 400
                
            if data['object'] == 'whatsapp_business_account':
                for entry in data['entry']:
                    for change in entry['changes']:
                        if change['value'].get('messages'):
                            message = change['value']['messages'][0]
                            phone_number = message.get('from')
                            
                            if 'text' in message:
                                message_body = message['text'].get('body', '')
                            elif 'interactive' in message:
                                message_body = message['interactive'].get('button_reply', {}).get('id', '')
                            else:
                                message_body = ''
                            
                            response_message = recharge_controller.process_recharge(phone_number, message_body)
                            
                            if response_message:
                                send_whatsapp_message(phone_number, response_message)
                            
                            return "OK", 200
                            
            return "OK", 200
            
        except Exception as e:
            logging.error(f"Error in webhook: {str(e)}")
            return "OK", 200

# Add CSRF exemption after the webhook function is defined
csrf.exempt(webhook)  # Exempt webhook from CSRF

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
            
        return render_template('admin_login.html', error="Invalid credentials")
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Add authentication middleware
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    if not session.get('admin_logged_in'):
        return False
    emit('user_list', get_active_users())

@socketio.on('get_user_list')
def handle_get_user_list():
    emit('user_list', get_active_users())

@socketio.on('disconnect')
def handle_disconnect():
    pass

def get_active_users():
    try:
        # Get users who have interacted in the last 24 hours
        recent_users = db.messages.find({
            'timestamp': {'$gte': datetime.utcnow() - timedelta(days=1)}
        }).distinct('phone_number')
        
        users = []
        for phone in recent_users:
            user = db.users.find_one({'phone_number': phone})
            if user:
                users.append({
                    'phone_number': phone,
                    'last_active': user.get('last_active', '').strftime('%Y-%m-%d %H:%M'),
                    'status': 'active' if user.get('last_active') > datetime.utcnow() - timedelta(hours=1) else 'inactive'
                })
        return users
    except Exception as e:
        logging.error(f"Error getting active users: {str(e)}")
        return []

# Admin panel routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('dashboard.html')

@app.route('/admin/user/<phone_number>')
@admin_required
def user_details(phone_number):
    try:
        # Get user details
        user = db.users.find_one({'phone_number': phone_number})
        if not user:
            return "User not found", 404
            
        # Get recharge history
        recharge_history = list(db.recharges.find(
            {'phone_number': phone_number}
        ).sort('date', -1))
        
        # Get payment history
        payments = list(db.payments.find(
            {'phone_number': phone_number}
        ).sort('date', -1))
        
        # Get current plan
        current_plan = db.recharges.find_one({
            'phone_number': phone_number,
            'status': 'success',
            'valid_until': {'$gt': datetime.utcnow()}
        })
        
        return render_template('user_details.html',
                             user=user,
                             history=recharge_history,
                             payments=payments,
                             current_plan=current_plan)
                             
    except Exception as e:
        logging.error(f"Error in user_details: {str(e)}")
        return "Internal server error", 500

@app.route('/api/chat/<phone_number>')
@admin_required
def get_chat_history(phone_number):
    try:
        messages = list(db.messages.find(
            {'phone_number': phone_number}
        ).sort('timestamp', 1))
        
        return jsonify({
            'messages': [{
                'text': msg['message'],
                'direction': msg['direction'],
                'timestamp': msg['timestamp'].strftime('%Y-%m-%d %H:%M')
            } for msg in messages]
        })
    except Exception as e:
        logging.error(f"Error getting chat history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/send-reply', methods=['POST'])
@admin_required
def send_reply():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Format phone number if needed (remove any spaces or special characters)
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Send message via WhatsApp
        success = send_whatsapp_message(phone_number, message)
        
        if success:
            # Store message in database
            db.messages.insert_one({
                'phone_number': phone_number,
                'message': message,
                'direction': 'outgoing',
                'timestamp': datetime.utcnow()
            })
            
            # Update user's last active time
            db.users.update_one(
                {'phone_number': phone_number},
                {
                    '$set': {'last_active': datetime.utcnow()},
                    '$setOnInsert': {'phone_number': phone_number}
                },
                upsert=True
            )
            
            # Emit to WebSocket
            socketio.emit('message', {
                'phone_number': phone_number,
                'message': message,
                'direction': 'outgoing'
            })
            
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to send message'}), 500
            
    except Exception as e:
        logging.error(f"Error sending reply: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/manual-recharge', methods=['POST'])
@admin_required
def trigger_manual_recharge():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        days = data.get('days')
        payment_method = data.get('payment_method')
        
        if not all([phone_number, amount, days, payment_method]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Create recharge record
        recharge_id = db.recharges.insert_one({
            'phone_number': phone_number,
            'amount': amount,
            'days': days,
            'status': 'pending',
            'payment_method': payment_method,
            'created_at': datetime.utcnow()
        }).inserted_id
        
        # Here you would integrate with your payment gateway
        # For now, we'll simulate a successful payment
        db.recharges.update_one(
            {'_id': recharge_id},
            {
                '$set': {
                    'status': 'success',
                    'transaction_id': f"TXN_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    'valid_until': datetime.utcnow() + timedelta(days=days)
                }
            }
        )
        
        # Send success message to user
        success_message = f"✅ Recharge Successful!\nAmount: ₹{amount}\nValidity: {days} Days"
        send_whatsapp_message(phone_number, success_message)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Error in manual recharge: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.get_json()
        # Process message here
        return jsonify({"status": "success", "message": "Message received"})
    else:
        # Return recent messages
        messages = [] # Replace with actual message fetching logic
        return jsonify(messages)

@app.errorhandler(404)
def not_found_error(e):  # Defined missing function
    return jsonify({
        "error": "Not Found",
        "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
    }), 404

def send_message(to, text):
    url = "https://graph.facebook.com/v13.0/me/messages"
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not access_token:
        logging.error("WhatsApp access token not found in environment variables")
        return False

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"Message sent successfully to {to}")
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error sending message to {to}: {str(e)}")
        if response.status_code == 401:
            logging.error("Authentication failed. Please check WhatsApp access token.")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send message to {to}: {str(e)}")
        return False

def send_button(to, text, button_text):
    url = "https://graph.facebook.com/v13.0/me/messages"
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not access_token:
        logging.error("WhatsApp access token not found in environment variables")
        return False

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "recharge_now", "title": button_text}}
                ]
            }
        }
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"Button message sent successfully to {to}")
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error sending button message to {to}: {str(e)}")
        if response.status_code == 401:
            logging.error("Authentication failed. Please check WhatsApp access token.")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send button message to {to}: {str(e)}")
        return False

# Register the custom error handler
app.register_error_handler(404, not_found_error)

# Register error handlers
if 'register_error_handlers' in locals():
    register_error_handlers(app)

@app.route('/api/send-manual-message', methods=['POST'])
@admin_required
def send_manual_message():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        data = request.get_json()
        if not data or 'phone_number' not in data or 'message' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        phone_number = data['phone_number']
        message = data['message']

        success = send_whatsapp_message(phone_number, message)
        
        if not success:
            return jsonify({'error': 'Failed to send message'}), 500

        return jsonify({'status': 'success'})

    except Exception as e:
        logging.error(f"Error sending manual message: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Update the main run statement to use socketio
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
