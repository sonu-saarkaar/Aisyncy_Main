import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, request, Response, jsonify, render_template, session, redirect, url_for, flash
import requests
import logging
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime, timedelta
import os
try:
    from src.chatflow.ChatFlowController import RechargeController, ChatFlowController  # type: ignore 
    recharge_controller = RechargeController()  # Initialize RechargeController
    chat_controller = ChatFlowController()
except ModuleNotFoundError:
    logging.error("Module 'ChatFlowController' could not be imported. Ensure it exists in 'src/chatflow'.")
    recharge_controller = None  # Set to None to avoid runtime errors
    chat_controller = None
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
from forms import LoginForm

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
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.urandom(24)
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour

logging.basicConfig(level=LOG_LEVEL)
VERIFY_TOKEN = "12345"

csrf = CSRFProtect(app)
csrf.init_app(app)

# Initialize SocketIO with CSRF protection
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# Add CSRF token to all responses
@app.after_request
def add_csrf_token(response):
    # Get the CSRF token from the session
    token = session.get('csrf_token')
    if token:
        response.headers['X-CSRFToken'] = token
    return response

# Generate CSRF token for each session
@app.before_request
def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = os.urandom(24).hex()

# MongoDB Connection
try:
    mongo_client = MongoClient(os.getenv('MONGO_URI'))
    db = mongo_client.get_database('aisyncy')
    logging.info("Connected to MongoDB successfully!")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {str(e)}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.handle_request(request)

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
                            
                            # Store incoming message
                            db.messages.insert_one({
                                'phone_number': phone_number,
                                'message': message_body,
                                'direction': 'incoming',
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
                            socketio.emit('new_message', {
                                'phone_number': phone_number,
                                'text': message_body,
                                'direction': 'incoming',
                                'timestamp': datetime.utcnow().isoformat(),
                                'time': datetime.utcnow().strftime('%I:%M %p'),
                                'date': datetime.utcnow().strftime('%d/%m/%Y')
                            })
                            
                            # Process message and get response
                            response_message = recharge_controller.process_recharge(phone_number, message_body)
                            
                            if response_message:
                                # Store bot response
                                db.messages.insert_one({
                                    'phone_number': phone_number,
                                    'message': response_message,
                                    'direction': 'bot',
                                    'timestamp': datetime.utcnow()
                                })
                                
                                # Emit bot response
                                socketio.emit('new_message', {
                                    'phone_number': phone_number,
                                    'text': response_message,
                                    'direction': 'bot',
                                    'timestamp': datetime.utcnow().isoformat(),
                                    'time': datetime.utcnow().strftime('%I:%M %p'),
                                    'date': datetime.utcnow().strftime('%d/%m/%Y')
                                })
                                
                                # Send response via WhatsApp
                                send_whatsapp_message(phone_number, response_message)
                            
                            return "OK", 200
                            
            return "OK", 200
            
        except Exception as e:
            logging.error(f"Error in webhook: {str(e)}")
            return "OK", 200

# Add CSRF exemption after the webhook function is defined
csrf.exempt(webhook)  # Exempt webhook from CSRF

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Replace with your actual authentication logic
        if username == "admin" and password == "admin123":
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin_login.html', form=form)

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
    if not session.get('admin_logged_in'):
        return False
    emit('user_list', get_active_users())

@socketio.on('admin_message')
def handle_admin_message(data):
    if not session.get('admin_logged_in'):
        return False
    try:
        phone_number = data.get('phone_number')
        message = data.get('text')
        
        if not phone_number or not message:
            return
            
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
            socketio.emit('new_message', {
                'phone_number': phone_number,
                'text': message,
                'direction': 'outgoing',
                'timestamp': datetime.utcnow().isoformat(),
                'time': datetime.utcnow().strftime('%I:%M %p'),
                'date': datetime.utcnow().strftime('%d/%m/%Y')
            })
            
    except Exception as e:
        logging.error(f"Error handling admin message: {str(e)}")

@socketio.on('message')
def handle_message(data):
    try:
        phone_number = data.get('phone_number')
        message = data.get('message')
        direction = data.get('direction', 'incoming')
        
        if not phone_number or not message:
            return
            
        # Store message in database
        db.messages.insert_one({
            'phone_number': phone_number,
            'message': message,
            'direction': direction,
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
        socketio.emit('new_message', {
            'phone_number': phone_number,
            'text': message,
            'direction': direction,
            'timestamp': datetime.utcnow().isoformat(),
            'time': datetime.utcnow().strftime('%I:%M %p'),
            'date': datetime.utcnow().strftime('%d/%m/%Y')
        })
        
    except Exception as e:
        logging.error(f"Error handling message: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    pass

def get_active_users():
    try:
        # Get users with recent messages
        users = list(db.messages.aggregate([
            {
                '$group': {
                    '_id': '$phone_number',
                    'last_message': {'$last': '$message'},
                    'last_active': {'$last': '$timestamp'},
                    'status': {'$last': '$direction'}
                }
            },
            {
                '$project': {
                    'phone_number': '$_id',
                    'last_message': 1,
                    'last_active': 1,
                    'status': 1
                }
            }
        ]))
        
        # Format the data
        for user in users:
            user['status'] = 'online' if (datetime.utcnow() - user['last_active']).total_seconds() < 300 else 'offline'
            user['last_active'] = user['last_active'].strftime('%Y-%m-%d %H:%M:%S')
            
        return users
    except Exception as e:
        logging.error(f"Error getting active users: {str(e)}")
        return []

# Admin panel routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

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
            {'phone_number': phone_number},
            {'_id': 0, 'phone_number': 0}
        ).sort('timestamp', 1))
        
        # Format messages for WhatsApp-like display
        formatted_messages = []
        for msg in messages:
            # Determine message direction
            if msg['direction'] == 'outgoing':
                direction = 'outgoing'
            elif msg['direction'] == 'bot':
                direction = 'incoming'  # Bot messages appear as incoming
            else:
                direction = msg['direction']
            
            formatted_messages.append({
                'text': msg['message'],
                'direction': direction,
                'timestamp': msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'time': msg['timestamp'].strftime('%I:%M %p'),
                'date': msg['timestamp'].strftime('%d/%m/%Y')
            })
        
        return jsonify({'messages': formatted_messages})
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

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = chat_controller.process_message(user_message)
    return jsonify({'response': response})

@app.route('/api/users')
@admin_required
def get_users():
    try:
        users = get_active_users()
        return jsonify({'users': users})
    except Exception as e:
        logging.error(f"Error getting users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Update the main run statement to use socketio
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
