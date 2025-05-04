import time
from datetime import datetime
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the credentials from the root config, but with fallback to hardcoded values
try:
    from config import MONGO_URI, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_API_URL
    logger.info("Loaded WhatsApp credentials from config")
except ImportError:
    logger.warning("Could not import credentials from config, using hardcoded values")
    # Hardcoded for safety
    MONGO_URI = "mongodb://localhost:27017/aisyncy_recharge"
    WHATSAPP_PHONE_NUMBER_ID = "104612292631543"
    WHATSAPP_ACCESS_TOKEN = "EAAwFo4oYpGgBO8ZAgKQxZB7dxQY8XnArrLxRsvuhZARG8NJVwQPiJ15EuJq30fV1x4eohl7zT4tHwegGaBcpqtVZADA8QOLKgJwL92etZC7HbZCeujbtr01yxcbFiZBFMUtfPr8RtriO8ZCxXCSWUvMxOynVhmy4ZBHtUzcbTGzLxPUdnIJMeyolNKjcpD376l1WZAJQZDZD"
    WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

class RechargeController:
    def __init__(self):
        self.user_states = {}
        self.recharge_plans = {
            'jio': [
                {'amount': 199, 'days': 28, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 349, 'days': 28, 'data': '2GB/day', 'description': 'Unlimited calls + 2GB daily data + 5G Unlimited'},
                {'amount': 399, 'days': 56, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 599, 'days': 84, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 999, 'days': 84, 'data': '2GB/day', 'description': 'Unlimited calls + 2GB daily data + 5G Unlimited'}
            ],
            'airtel': [
                {'amount': 199, 'days': 28, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 349, 'days': 28, 'data': '2GB/day', 'description': 'Unlimited calls + 2GB daily data + 5G Unlimited'},
                {'amount': 399, 'days': 56, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 599, 'days': 84, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 999, 'days': 84, 'data': '2GB/day', 'description': 'Unlimited calls + 2GB daily data + 5G Unlimited'}
            ],
            'vi': [
                {'amount': 199, 'days': 28, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 349, 'days': 28, 'data': '2GB/day', 'description': 'Unlimited calls + 2GB daily data + 5G Unlimited'},
                {'amount': 399, 'days': 56, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 599, 'days': 84, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data + 5G Unlimited'},
                {'amount': 999, 'days': 84, 'data': '2GB/day', 'description': 'Unlimited calls + 2GB daily data + 5G Unlimited'}
            ],
            'bsnl': [
                {'amount': 199, 'days': 28, 'data': '1GB/day', 'description': 'Unlimited calls + 1GB daily data'},
                {'amount': 349, 'days': 28, 'data': '2GB/day', 'description': 'Unlimited calls + 2GB daily data'},
                {'amount': 399, 'days': 56, 'data': '1GB/day', 'description': 'Unlimited calls + 1GB daily data'},
                {'amount': 599, 'days': 84, 'data': '1GB/day', 'description': 'Unlimited calls + 1GB daily data'},
                {'amount': 999, 'days': 84, 'data': '1.5GB/day', 'description': 'Unlimited calls + 1.5GB daily data'}
            ]
        }
        self.recharge_requests = {}  # Store recharge requests by phone number
        
        try:
            # Initialize MongoDB connection
            client = MongoClient(MONGO_URI)
            self.db = client.get_default_database()
            logger.info("Successfully connected to MongoDB in RechargeController")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.db = None

        # WhatsApp API credentials - updated to use the imported or hardcoded values
        self.WHATSAPP_API_URL = WHATSAPP_API_URL
        self.WHATSAPP_TOKEN = WHATSAPP_ACCESS_TOKEN
        
        logger.info(f"RechargeController initialized with WhatsApp Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")

    def start_recharge_session(self, phone_number):
        """Initialize a new recharge request when session starts"""
        request_data = {
            'phone_number': phone_number,
            'created_at': time.time(),
            'status': 'initiated',
            'operator': None,
            'plan_details': None,
            'payment_details': None
        }
        
        # Save to MongoDB
        result = self.db.recharge_requests.insert_one(request_data)
        request_data['_id'] = result.inserted_id
        
        # Store in memory
        self.recharge_requests[phone_number] = request_data
        return request_data

    def update_recharge_request(self, phone_number, **kwargs):
        """Update recharge request details"""
        if phone_number in self.recharge_requests:
            # Update in memory
            self.recharge_requests[phone_number].update(kwargs)
            self.recharge_requests[phone_number]['updated_at'] = time.time()
            
            # Update in MongoDB
            self.db.recharge_requests.update_one(
                {'phone_number': phone_number},
                {'$set': kwargs}
            )
            return True
        return False

    def handle_initial_state(self, message, phone_number):
        # Check for greeting words
        greeting_words = ['hi', 'hello', 'hye', 'recharge', 'recharge now', 'namaste', 'hey']
        if message.lower().strip() in greeting_words:
            # Start new recharge session
            self.start_recharge_session(phone_number)
            self.user_states[phone_number] = {
                'state': 'welcome',
                'current_number': phone_number
            }
            return self.send_welcome_message(phone_number)
        else:
            return self.send_invalid_input_message(phone_number)

    def send_welcome_message(self, phone_number):
        # Reset user state when showing welcome message
        self.user_states[phone_number] = {
            'state': 'welcome',
            'current_number': phone_number
        }
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Welcome to Aisyncy Recharge!\n\nWe provide easy and fast recharge services through WhatsApp. How can I help you today?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "recharge_now", "title": "Recharge Now"}},
                        {"type": "reply", "reply": {"id": "explore_aisyncy", "title": "Explore Aisyncy"}}
                    ]
                }
            }
        }

    def send_number_confirmation(self, phone_number, number):
        # Extract last 10 digits if number is longer
        number = ''.join(filter(str.isdigit, number))[-10:]
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Would you like to recharge this number?\n\n{number}"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "confirm_number", "title": "Confirm Number"}},
                        {"type": "reply", "reply": {"id": "other_number", "title": "Other Number"}}
                    ]
                }
            }
        }

    def send_number_input_prompt(self, phone_number):
        self.user_states[phone_number]['state'] = 'waiting_for_number'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Please enter the 10-digit Mobile Number you would like to Recharge:"
            }
        }

    def detect_operator(self, number):
        # Enhanced operator detection based on number prefix
        prefix = number[:3]
        
        # Jio prefixes
        jio_prefixes = ['600', '601', '602', '603', '604', '605', '606', '607', '608', '609', '700', '701', '702', '703', '704', '705', '706', '707', '708', '709']
        
        # Airtel prefixes
        airtel_prefixes = ['700', '701', '702', '703', '704', '705', '706', '707', '708', '709', '800', '801', '802', '803', '804', '805', '806', '807', '808', '809']
        
        # Vi prefixes
        vi_prefixes = ['800', '801', '802', '803', '804', '805', '806', '807', '808', '809', '900', '901', '902', '903', '904', '905', '906', '907', '908', '909']
        
        if prefix in jio_prefixes:
            return 'jio'
        elif prefix in airtel_prefixes:
            return 'airtel'
        elif prefix in vi_prefixes:
            return 'vi'
        else:
            return 'bsnl'

    def send_operator_confirmation_message(self, phone_number, number):
        operator = self.detect_operator(number)
        self.user_states[phone_number]['operator'] = operator
        self.user_states[phone_number]['state'] = 'operator_selection'
        
        print(f"DEBUG - Sending operator confirmation for {operator} to {phone_number}")
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Aisyncy Recharge detected that your number belongs to {operator.upper()} network. Is this correct?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "Yes, Confirm",
                                "title": "Yes, Confirm"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "No, Change Operator",
                                "title": "No, Change Operator"
                            }
                        }
                    ]
                }
            }
        }

    def send_operator_selection_message(self, phone_number):
        operators = ['jio', 'airtel', 'vi', 'bsnl']
        current_operator = self.user_states[phone_number].get('operator')
        
        if current_operator in operators:
            operators.remove(current_operator)
        
        # Create buttons for remaining operators (max 3)
        buttons = []
        for op in operators[:3]:  # WhatsApp limit of 3 buttons
            buttons.append({
                "type": "reply",
                "reply": {
                    "id": op.upper(),
                    "title": op.upper()
                }
            })
        
        print(f"DEBUG - Sending operator selection with buttons: {[b['reply']['id'] for b in buttons]}")
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Please select your correct operator:"
                },
                "action": {
                    "buttons": buttons
                }
            }
        }

    def send_plan_selection_message(self, phone_number):
        operator = self.user_states[phone_number]['operator']
        plans = self.recharge_plans[operator]
        self.user_states[phone_number]['state'] = 'plan_selection'
        
        # Create the list view message with all plans
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Select Recharge Plan"
                },
                "body": {
                    "text": f"Choose your {operator.upper()} recharge plan:"
                },
                "footer": {
                    "text": "All plans include unlimited calls"
                },
                "action": {
                    "button": "View Plans",
                    "sections": [
                        {
                            "title": "📱 POPULAR PLANS",
                            "rows": [
                                {
                                    "id": f"plan_{i}",
                                    "title": f"₹{plan['amount']} - {plan['days']} Days",
                                    "description": f"📱 {plan['data']} • Unlimited Calls"
                                } for i, plan in enumerate(plans) if plan['days'] <= 30
                            ]
                        },
                        {
                            "title": "♾️ UNLIMITED PLANS",
                            "rows": [
                                {
                                    "id": f"plan_{i}",
                                    "title": f"₹{plan['amount']} - {plan['days']} Days",
                                    "description": f"📱 {plan['data']} • Unlimited Calls"
                                } for i, plan in enumerate(plans) if 30 < plan['days'] <= 84
                            ]
                        },
                        {
                            "title": "📊 DATA PLANS",
                            "rows": [
                                {
                                    "id": f"plan_{i}",
                                    "title": f"₹{plan['amount']} - {plan['days']} Days",
                                    "description": f"📱 {plan['data']} • Unlimited Calls"
                                } for i, plan in enumerate(plans) if plan['days'] > 84 or float(plan['data'].split('GB')[0]) >= 2
                            ]
                        }
                    ]
                }
            }
        }

    def send_recharge_summary(self, phone_number):
        number = self.user_states[phone_number]['current_number']
        operator = self.user_states[phone_number]['operator']
        plan = self.user_states[phone_number]['selected_plan']
        masked_number = number[:10] 
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Your Recharge Details:\n\nNumber: {masked_number}\nOperator: {operator.upper()}\nAmount: ₹{plan['amount']}\nValidity: {plan['days']} days\nData: {plan['data']}\nCalling: Unlimited"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "proceed_payment", "title": "Pay Now"}},
                        {"type": "reply", "reply": {"id": "change_plan", "title": "Change Plan"}},
                        {"type": "reply", "reply": {"id": "cancel_recharge", "title": "Cancel Recharge"}}
                    ]
                }
            }
        }

    def send_payment_options_message(self, phone_number):
        self.user_states[phone_number]['state'] = 'payment_mode'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Please select your preferred payment method:"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "pay_upi", "title": "Pay with UPI"}},
                        {"type": "reply", "reply": {"id": "pay_qr", "title": "Scan QR Code"}},
                        {"type": "reply", "reply": {"id": "pay_other", "title": "Other Payment"}}
                    ]
                }
            }
        }

    def send_upi_payment_details(self, phone_number):
        """Send UPI payment details including UPI ID"""
        plan = self.user_states[phone_number]['selected_plan']
        amount = plan['amount']
        upi_id = "aisyncy.recharge@upi"  # Demo UPI ID
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Please pay ₹{amount} using UPI\n\nUPI ID: {upi_id}\n\nClick 'Pay Now' to proceed with payment"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "confirm_upi_payment", "title": "Pay Now"}},
                        {"type": "reply", "reply": {"id": "cancel_payment", "title": "Cancel"}}
                    ]
                }
            }
        }

    def send_qr_payment_details(self, phone_number):
        """Send QR code for payment"""
        plan = self.user_states[phone_number]['selected_plan']
        amount = plan['amount']
        
        # Demo QR code URL (replace with actual QR code generation)
        qr_code_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=upi://pay?pa=aisyncy.recharge@upi&pn=Aisyncy%20Recharge&am=" + str(amount)
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Please scan the QR code to pay ₹{amount}\n\nUPI ID: aisyncy.recharge@upi"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "confirm_qr_payment", "title": "I've Paid"}},
                        {"type": "reply", "reply": {"id": "cancel_payment", "title": "Cancel"}}
                    ]
                }
            }
        }

    def send_other_payment_options(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Select your payment method:"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "pay_card", "title": "Credit/debit Card"}},
                        {"type": "reply", "reply": {"id": "pay_qr", "title": "QR & Link"}},
                        {"type": "reply", "reply": {"id": "pay_emi", "title": "Emi/Loan"}}
                    ]
                }
            }
        }

    def send_payment_success_message(self, phone_number):
        self.user_states[phone_number]['state'] = 'payment_success'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": "Thank you for completing payment! Your transaction id : R852489620 is successful.\n\nPlease wait a second..."}
        }

    def send_recharge_success_message(self, phone_number):
        plan = self.user_states[phone_number]['selected_plan']
        operator = self.user_states[phone_number]['operator']
        number = self.user_states[phone_number]['current_number']
        self.user_states[phone_number]['state'] = 'recharge_done'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": f"Aisyncy Recharge will do your recharge\n₹ {plan['amount']} for {operator.title()} Number {number} is successful"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "auto_recharge", "title": "Auto Recharge"}},
                        {"type": "reply", "reply": {"id": "rise_issue", "title": "Rise Issue"}},
                        {"type": "reply", "reply": {"id": "feedback", "title": "Feedback"}}
                    ]
                }
            }
        }

    def send_feedback_message(self, phone_number):
        self.user_states[phone_number]['state'] = 'feedback'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Thank you for using Aisyncy Recharge! Kindly rate us."},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "rate_good", "title": "Good"}},
                        {"type": "reply", "reply": {"id": "rate_average", "title": "Average"}},
                        {"type": "reply", "reply": {"id": "rate_awesome", "title": "Awesome"}}
                    ]
                }
            }
        }

    def send_recent_transactions(self, phone_number):
        self.user_states[phone_number]['state'] = 'recent_transactions'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Recent Transactions"
                },
                "body": {
                    "text": "Here are your recent transactions:"
                },
                "action": {
                    "button": "View Transactions",
                    "sections": [
                        {
                            "title": "📱 MOBILE RECHARGES",
                            "rows": [
                                {
                                    "id": "trans_1",
                                    "title": "₹399 - Jio Recharge",
                                    "description": "✅ Success • Yesterday"
                                },
                                {
                                    "id": "trans_2",
                                    "title": "₹599 - Airtel Recharge",
                                    "description": "✅ Success • Last Week"
                                }
                            ]
                        },
                        {
                            "title": "💡 UTILITY PAYMENTS",
                            "rows": [
                                {
                                    "id": "trans_3",
                                    "title": "₹1500 - Electricity Bill",
                                    "description": "✅ Success • 2 weeks ago"
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def send_utility_bill_payment(self, phone_number):
        self.user_states[phone_number]['state'] = 'utility_bill'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Utility Bill Payments"
                },
                "body": {
                    "text": "Select the type of bill you want to pay:"
                },
                "action": {
                    "button": "View Options",
                    "sections": [
                        {
                            "title": "UTILITY BILLS",
                            "rows": [
                                {
                                    "id": "electricity",
                                    "title": "Electricity Bill",
                                    "description": "Pay your electricity bill"
                                },
                                {
                                    "id": "water",
                                    "title": "Water Bill",
                                    "description": "Pay your water bill"
                                },
                                {
                                    "id": "gas",
                                    "title": "Gas Bill",
                                    "description": "Pay your gas bill"
                                }
                            ]
                        },
                        {
                            "title": "OTHER PAYMENTS",
                            "rows": [
                                {
                                    "id": "lic",
                                    "title": "LIC Premium",
                                    "description": "Pay your LIC premium"
                                },
                                {
                                    "id": "credit_card",
                                    "title": "Credit Card Bill",
                                    "description": "Pay your credit card bill"
                                },
                                {
                                    "id": "loan",
                                    "title": "Loan EMI",
                                    "description": "Pay your loan EMI"
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def send_auto_recharge_options(self, phone_number):
        self.user_states[phone_number]['state'] = 'auto_recharge_options'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Auto Recharge Setup"
                },
                "body": {
                    "text": "Choose how you want to set up auto recharge:"
                },
                "action": {
                    "button": "View Options",
                    "sections": [
                        {
                            "title": "AUTO RECHARGE OPTIONS",
                            "rows": [
                                {
                                    "id": "monthly",
                                    "title": "Monthly Auto Recharge",
                                    "description": "Recharge automatically every month"
                                },
                                {
                                    "id": "Data",
                                    "title": "Data based recharge",
                                    "description": "90% data used then recharge data pack"
                                },
                                {
                                    "id": "custom",
                                    "title": "Custom Schedule",
                                    "description": "Set your own recharge schedule"
                                }
                            ]
                        },
                        {
                            "title": "PAYMENT METHODS",
                            "rows": [
                                {
                                    "id": "upi_mandate",
                                    "title": "UPI Auto-Debit",
                                    "description": "Set up UPI mandate for auto-debit"
                                },
                                {
                                    "id": "card_mandate",
                                    "title": "Card Auto-Debit",
                                    "description": "Set up card for auto-debit"
                                }
                            ]
                        },
                        {
                            "title": "PAY LATER OPTIONS",
                            "rows": [
                                {
                                    "id": "pay_next_month",
                                    "title": "Pay Next Month",
                                    "description": "Pay your recharge amount next month"
                                },
                                {
                                    "id": "pay_15_days",
                                    "title": "Pay in 15 Days",
                                    "description": "Pay your recharge amount in 15 days"
                                },
                                {
                                    "id": "emi",
                                    "title": "Convert to EMI",
                                    "description": "Convert recharge amount to easy EMIs"
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def send_use_now_pay_later(self, phone_number):
        self.user_states[phone_number]['state'] = 'use_now_pay_later'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Use Now, Pay Later"
                },
                "body": {
                    "text": "Get instant recharge and pay later! Choose your preferred option:"
                },
                "action": {
                    "button": "View Options",
                    "sections": [
                        {
                            "title": "PAY LATER OPTIONS",
                            "rows": [
                                {
                                    "id": "pay_next_month",
                                    "title": "Pay Next Month",
                                    "description": "Pay your recharge amount next month"
                                },
                                {
                                    "id": "pay_15_days",
                                    "title": "Pay in 15 Days",
                                    "description": "Pay your recharge amount in 15 days"
                                },
                                {
                                    "id": "emi",
                                    "title": "Convert to EMI",
                                    "description": "Convert recharge amount to easy EMIs"
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def send_mandate_setup(self, phone_number, mandate_type):
        self.user_states[phone_number]['state'] = 'mandate_setup'
        self.user_states[phone_number]['mandate_type'] = mandate_type
        
        message = "Set up UPI Auto-Debit" if mandate_type == "upi" else "Set up Card Auto-Debit"
        description = "Link your UPI ID for auto-debit" if mandate_type == "upi" else "Link your card for auto-debit"
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"{message}\n\n{description}\n\nBy proceeding, you agree to allow Aisyncy Recharge to automatically debit your account for scheduled recharges."
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "setup_mandate", "title": "Set Up Now"}},
                        {"type": "reply", "reply": {"id": "cancel_mandate", "title": "Cancel"}}
                    ]
                }
            }
        }

    def process_recharge(self, phone_number, message):
        # Handle exit/cancel commands globally
        if message.lower() in ['exit', 'cancel', 'cancel recharge']:
            if phone_number in self.user_states:
                del self.user_states[phone_number]
            if phone_number in self.recharge_requests:
                self.update_recharge_request(phone_number, status='cancelled')
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": "Session cancelled. Thank you for using Aisyncy Recharge! Type 'hi' to start again."
                }
            }

        # Get current state or initialize if new user
        if phone_number not in self.user_states:
            return self.handle_initial_state(message, phone_number)

        current_state = self.user_states[phone_number].get('state', 'welcome')
        print(f"Current state: {current_state}, Message: {message}")  # Debug log

        # Handle different states
        if current_state == 'welcome':
            if message.lower() in ['recharge_now', 'recharge now']:
                self.user_states[phone_number]['state'] = 'number_confirmation'
                self.update_recharge_request(phone_number, status='number_confirmation')
                return self.send_number_confirmation(phone_number, phone_number)
            elif message.lower() in ['explore_aisyncy', 'explore aisyncy']:
                return self.send_explore_aisyncy_welcome(phone_number)
            else:
                return self.send_welcome_message(phone_number)

        elif current_state == 'number_confirmation':
            if message.lower() in ['confirm_number', 'confirm number']:  # Handle both button ID and text
                number = self.user_states[phone_number]['current_number']
                self.user_states[phone_number]['state'] = 'operator_selection'
                return self.send_operator_confirmation_message(phone_number, number)
            elif message.lower() in ['other_number', 'other number']:  # Handle both button ID and text
                return self.send_number_input_prompt(phone_number)
            else:
                # If user sends a number directly
                if message.isdigit() and len(message) >= 10:
                    self.user_states[phone_number]['state'] = 'operator_selection'
                    return self.send_operator_confirmation_message(phone_number, message)
                else:
                    return self.send_number_confirmation(phone_number, phone_number)

        elif current_state == 'waiting_for_number':
            # Validate the entered number
            if message.isdigit() and len(message) == 10:
                self.user_states[phone_number]['current_number'] = message
                self.user_states[phone_number]['state'] = 'operator_selection'
                return self.send_operator_confirmation_message(phone_number, message)
            else:
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "Please enter a valid 10-digit mobile number:"
                    }
                }

        elif current_state == 'operator_selection':
            if message.lower() in ['yes, confirm', 'yes']:
                self.user_states[phone_number]['state'] = 'plan_selection'
                return self.send_plan_selection_message(phone_number)
            elif message.lower() in ['no, change operator', 'no']:
                return self.send_operator_selection_message(phone_number)
            elif message.lower() in ['jio', 'airtel', 'vi', 'bsnl']:
                self.user_states[phone_number]['operator'] = message.lower()
                self.update_recharge_request(phone_number, 
                    operator=message.lower(),
                    status='operator_selected'
                )
                self.user_states[phone_number]['state'] = 'plan_selection'
                return self.send_plan_selection_message(phone_number)

        elif current_state == 'plan_selection':
            if message.startswith('plan_'):
                plan_index = int(message.split('_')[1])
                operator = self.user_states[phone_number]['operator']
                selected_plan = self.recharge_plans[operator][plan_index]
                self.user_states[phone_number]['selected_plan'] = selected_plan
                self.update_recharge_request(phone_number,
                    plan_details=selected_plan,
                    status='plan_selected'
                )
                self.user_states[phone_number]['state'] = 'recharge_summary'
                return self.send_recharge_summary(phone_number)

        elif current_state == 'recharge_summary':
            if message.lower() in ['proceed_payment', 'pay now']:
                self.user_states[phone_number]['state'] = 'payment_mode'
                return self.send_payment_options_message(phone_number)
            elif message.lower() in ['change_plan', 'change plan']:
                self.user_states[phone_number]['state'] = 'plan_selection'
                return self.send_plan_selection_message(phone_number)
            elif message.lower() in ['cancel_recharge', 'cancel recharge']:
                del self.user_states[phone_number]
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "Recharge cancelled. Type 'hi' to start again."
                    }
                }

        elif current_state == 'payment_mode':
            if message.lower() in ['pay_upi']:
                self.user_states[phone_number]['state'] = 'upi_payment'
                return self.send_upi_payment_details(phone_number)
            elif message.lower() in ['pay_qr']:
                self.user_states[phone_number]['state'] = 'qr_payment'
                return self.send_qr_payment_details(phone_number)
            elif message.lower() in ['pay_other']:
                return self.send_other_payment_options(phone_number)

        elif current_state == 'upi_payment':
            if message.lower() in ['confirm_upi_payment']:
                self.update_recharge_request(phone_number,
                    payment_details={
                        'mode': 'upi',
                        'status': 'initiated',
                        'upi_id': 'aisyncy.recharge@upi'
                    },
                    status='payment_initiated'
                )
                self.user_states[phone_number]['state'] = 'payment_success'
                return self.send_payment_success_message(phone_number)
            elif message.lower() in ['cancel_payment']:
                return self.send_payment_options_message(phone_number)

        elif current_state == 'qr_payment':
            if message.lower() in ['confirm_qr_payment']:
                self.update_recharge_request(phone_number,
                    payment_details={
                        'mode': 'qr',
                        'status': 'initiated',
                        'upi_id': 'aisyncy.recharge@upi'
                    },
                    status='payment_initiated'
                )
                self.user_states[phone_number]['state'] = 'payment_success'
                return self.send_payment_success_message(phone_number)
            elif message.lower() in ['cancel_payment']:
                return self.send_payment_options_message(phone_number)

        elif current_state == 'payment_success':
            # Generate transaction ID and update payment status
            transaction_id = f"R{int(time.time())}"
            
            # Get the complete recharge request data
            request_data = self.recharge_requests.get(phone_number, {})
            
            # Update with payment completion details
            request_data.update({
                'payment_details': {
                    'status': 'completed',
                    'transaction_id': transaction_id,
                    'completed_at': datetime.utcnow().isoformat()
                },
                'status': 'payment_completed',
                'updated_at': time.time()
            })
            
            # Update in MongoDB
            self.db.recharge_requests.update_one(
                {'phone_number': phone_number},
                {'$set': request_data},
                upsert=True
            )
            
            # Update in memory
            self.recharge_requests[phone_number] = request_data
            
            # Update state
            self.user_states[phone_number]['state'] = 'recharge_done'
            
            return self.send_recharge_success_message(phone_number)

        elif current_state == 'recharge_done':
            if message.lower() in ['auto_recharge', 'auto recharge']:
                return self.send_explore_auto(phone_number)
            elif message.lower() in ['rise_issue', 'rise issue']:
                return self.send_explore_complaint(phone_number)
            elif message.lower() in ['feedback']:
                return self.send_feedback_message(phone_number)

        # Handle explore states
        elif current_state == 'explore_main':
            if message.lower() in ['contact_us']:
                return self.send_contact_mode(phone_number)
            elif message.lower() in ['services_transaction']:
                return self.send_services_menu(phone_number)
            elif message.lower() in ['auto_payment_setup']:
                return self.send_auto_payment_setup(phone_number)

        elif current_state == 'contact_mode':
            if message.lower() == 'call_back':
                return self.send_call_back(phone_number)
            elif message.lower() == 'rise_complaint':
                return self.send_complaint_format(phone_number)
            elif message.lower() == 'open_website':
                return self.send_website_redirect(phone_number)

        elif current_state == 'call_back':
            if message.lower() == 'request_call':
                return self.send_request_call_input(phone_number)
            elif message.lower() == 'chat_agent':
                return self.send_call_back(phone_number)

        elif current_state == 'waiting_call_number':
            if message.isdigit() and len(message) == 10:
                return self.send_call_confirmation(phone_number)
            else:
                return self.send_request_call_input(phone_number)

        elif current_state == 'services':
            if message.lower() == 'utility':
                return self.send_utility_bill_payment(phone_number)
            elif message.lower() == 'recharge_plans':
                return self.send_website_redirect(phone_number)
            elif message.lower() == 'recent_transaction':
                return self.send_recent_transactions(phone_number)

        elif current_state == 'auto_payment':
            if message.lower() == 'set_auto_recharge':
                return self.send_auto_recharge_options(phone_number)
            elif message.lower() == 'use_pay_next':
                return self.send_use_now_pay_later(phone_number)

        elif current_state == 'utility_bill':
            if message.lower() in ['electricity', 'water', 'gas', 'lic', 'credit_card', 'loan']:
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "This feature is coming soon! We're working on integrating utility bill payments. Please check back later."
                    }
                }

        elif current_state == 'auto_recharge_options':
            if message.lower() in ['monthly', 'low_balance', 'custom']:
                return self.send_auto_payment_setup(phone_number)
            elif message.lower() in ['upi_mandate', 'card_mandate']:
                return self.send_explore_set_auto(phone_number)

        elif current_state == 'use_now_pay_later':
            if message.lower() in ['pay_next_month', 'pay_15_days', 'emi']:
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "This feature is coming soon! We're working on integrating pay later options. Please check back later."
                    }
                }

        elif current_state == 'mandate_setup':
            if message.lower() == 'setup_mandate':
                mandate_type = self.user_states[phone_number].get('mandate_type', 'upi')
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": f"You will receive a link to set up {mandate_type.upper()} mandate shortly. Please complete the setup process to enable auto-recharge."
                    }
                }
            elif message.lower() == 'cancel_mandate':
                return self.send_auto_payment_setup(phone_number)

        elif current_state == 'complaint_type':
            valid_complaints = ['failed_recharge', 'wrong_plan', 'pending_recharge', 
                              'payment_issue', 'refund_status', 'other_issue']
            if message.lower() in valid_complaints:
                return self.send_complaint_confirmation(phone_number, message)

        elif current_state == 'complaint_submitted':
            if message.lower() == 'track_complaint':
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "You can track your complaint status at:\nhttps://aisyncyrecharge.vercel.app/track-complaint"
                    }
                }
            elif message.lower() == 'talk_to_agent':
                return self.send_call_back(phone_number)

        # Default response for unrecognized messages
        return self.send_welcome_message(phone_number)

    def send_explore_aisyncy_welcome(self, phone_number):
        self.user_states[phone_number] = {'state': 'explore_main'}
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Welcome to Aisyncy Recharge!\n\nWe provide:\n• 24*7 Support\n• Fast & Secure Services\n• Auto Recharge\n• WhatsApp Bot Support\n• Rewards & Discounts"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "contact_us", "title": "Contact Us"}},
                        {"type": "reply", "reply": {"id": "services_transaction", "title": "Services"}},
                        {"type": "reply", "reply": {"id": "auto_payment_setup", "title": "Auto Payment"}}
                    ]
                }
            }
        }

    def send_contact_mode(self, phone_number):
        self.user_states[phone_number]['state'] = 'contact_mode'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "How would you like to contact us?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "call_back", "title": "Call Back"}},
                        {"type": "reply", "reply": {"id": "rise_complaint", "title": "Raise Complaint"}},
                        {"type": "reply", "reply": {"id": "open_website", "title": "Visit Website"}}
                    ]
                }
            }
        }

    def send_call_back(self, phone_number):
        self.user_states[phone_number]['state'] = 'call_back'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Aisyncy Recharge Provide 24*7 Support\nSo you call me 9708299494 at any tym\nwe will helpfull for us ....."
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "request_call", "title": "Request Call"}},
                        {"type": "reply", "reply": {"id": "chat_agent", "title": "Chat With Agent"}}
                    ]
                }
            }
        }

    def send_request_call_input(self, phone_number):
        self.user_states[phone_number]['state'] = 'waiting_call_number'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Enter You Number That's you Want to\nRecive You Call :)"
            }
        }

    def send_call_confirmation(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Wait Aisyncy Staff Will You Call Shotlyy"
            }
        }

    def send_complaint_format(self, phone_number):
        self.user_states[phone_number]['state'] = 'complaint'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "add All Issue reagdig You to face the\nuser in list View msg formate with\nproper responsive chart flow.."
            }
        }

    def send_website_redirect(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "https://aisyncyrechge.vercel.app"
            }
        }

    def send_services_menu(self, phone_number):
        self.user_states[phone_number]['state'] = 'services'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "What would you like to do?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "utility", "title": "Utility Bills"}},
                        {"type": "reply", "reply": {"id": "recharge_plans", "title": "Recharge Plans"}},
                        {"type": "reply", "reply": {"id": "recent_transaction", "title": "Transactions"}}
                    ]
                }
            }
        }

    def send_auto_payment_setup(self, phone_number):
        self.user_states[phone_number]['state'] = 'auto_payment'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Choose your auto payment option:"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "set_auto_recharge", "title": "Auto Recharge"}},
                        {"type": "reply", "reply": {"id": "use_pay_next", "title": "Pay Later"}}
                    ]
                }
            }
        }

    def send_explore_complaint(self, phone_number):
        self.user_states[phone_number]['state'] = 'explore_complaint'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Raise Complaint"},
                "body": {"text": "Please list your issue in the complaint format. \nWe will respond with a proper solution via chat."},
                "action": {
                    "list": "View Complaint in List Format",
                    "sections": [
                        {"title": "Complaint Format", "rows": [
                            {"id": "explore_complaint_list", "title": "View Complaint in List Format", "description": ""}
                        ]}
                    ]
                }
            }
        }

    def send_explore_auto(self, phone_number):
        self.user_states[phone_number]['state'] = 'explore_auto'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Auto Payment Features:\n\nChoose how you want to set up your automatic recharge:"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "explore_set_auto", "title": "Set Auto Recharge"}},
                        {"type": "reply", "reply": {"id": "explore_use_next_month", "title": "Use This Month, Pay Next Month"}}
                    ]
                }
            }
        }

    def send_explore_set_auto(self, phone_number):
        self.user_states[phone_number]['state'] = 'explore_set_auto'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Auto Recharge means Aisyncy will automatically recharge your number \nand deduct the money after recharge, without manual intervention."},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "explore_upi_mandate", "title": "UPI Mandate"}},
                        {"type": "reply", "reply": {"id": "explore_card_mandate", "title": "Credit/Debit Mandate"}}
                    ]
                }
            }
        }

    def send_explore_use_next_month(self, phone_number):
        self.user_states[phone_number]['state'] = 'explore_use_next_month'
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "✅ Use Today, Pay Tomorrow!\nRecharge first, pay later with Aisyncy Recharge."},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "explore_back", "title": "Back"}}
                    ]
                }
            }
        } 