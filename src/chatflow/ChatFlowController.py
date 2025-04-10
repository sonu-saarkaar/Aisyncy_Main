import time

class RechargeController:
    def __init__(self):
        self.user_states = {}
        self.recharge_plans = {
            'jio': [
                {'amount': 199, 'days': 28, 'data': '1.5GB/day'},
                {'amount': 399, 'days': 56, 'data': '1.5GB/day'},
                {'amount': 599, 'days': 84, 'data': '1.5GB/day'},
                {'amount': 999, 'days': 84, 'data': '2GB/day'}
            ],
            'airtel': [
                {'amount': 199, 'days': 28, 'data': '1.5GB/day'},
                {'amount': 399, 'days': 56, 'data': '1.5GB/day'},
                {'amount': 599, 'days': 84, 'data': '1.5GB/day'},
                {'amount': 999, 'days': 84, 'data': '2GB/day'}
            ],
            'vi': [
                {'amount': 199, 'days': 28, 'data': '1.5GB/day'},
                {'amount': 399, 'days': 56, 'data': '1.5GB/day'},
                {'amount': 599, 'days': 84, 'data': '1.5GB/day'},
                {'amount': 999, 'days': 84, 'data': '2GB/day'}
            ],
            'bsnl': [
                {'amount': 199, 'days': 28, 'data': '1GB/day'},
                {'amount': 399, 'days': 56, 'data': '1GB/day'},
                {'amount': 599, 'days': 84, 'data': '1GB/day'},
                {'amount': 999, 'days': 84, 'data': '1.5GB/day'}
            ]
        }

    def handle_initial_state(self, message, phone_number):
        # Check for greeting words
        greeting_words = ['hi', 'hello', 'hye', 'recharge', 'recharge now', 'namaste']
        if message.lower().strip() in greeting_words:
            # Move to number selection state
            self.user_states[phone_number] = {
                'state': 'number_selection',
                'current_number': phone_number
            }
            return self.send_welcome_message(phone_number)
        else:
            return self.send_invalid_input_message(phone_number)

    def send_welcome_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Welcome to Aisyncy Recharge!"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "recharge_now", "title": "Recharge Now"}},
                        {"type": "reply", "reply": {"id": "explore_aisyncy", "title": "Explore Aisyncy"}}
                    ]
                }
            }
        }

    def send_explore_aisyncy_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Discover more about Aisyncy below!"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "about", "title": "About"}},
                        {"type": "reply", "reply": {"id": "subscription", "title": "Subscription Model"}},
                        {"type": "reply", "reply": {"id": "complaint", "title": "Register Complaint"}}
                    ]
                }
            }
        }

    def send_invalid_input_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Please send 'Hi' or 'Hello' to proceed."
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "recharge_now", "title": "Recharge Now"}},
                        {"type": "reply", "reply": {"id": "explore_aisyncy", "title": "Explore Aisyncy"}}
                    ]
                }
            }
        }

    def handle_number_selection(self, phone_number, message):
        if message == "recharge_now":
            # Extract the last 10 digits from the phone number
            number = ''.join(filter(str.isdigit, phone_number))[-10:]
            self.user_states[phone_number]['current_number'] = number
            return self.send_number_confirmation(phone_number, number)
        elif message == "explore_aisyncy":
            return self.send_explore_aisyncy_message(phone_number)
        else:
            # Check if the message is a 10-digit number
            number = ''.join(filter(str.isdigit, message))
            if len(number) == 10:
                self.user_states[phone_number]['current_number'] = number
                return self.send_operator_confirmation_message(phone_number, number)
            else:
                return self.send_invalid_number_message(phone_number)

    def send_number_confirmation(self, phone_number, number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Would you like to recharge this number: {number}?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "confirm_number", "title": "Confirm Number"}},
                        {"type": "reply", "reply": {"id": "other_number", "title": "Other Number"}}
                    ]
                }
            }
        }

    def send_invalid_number_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Please enter a valid 10-digit mobile number."
            }
        }

    def send_operator_confirmation_message(self, phone_number, number):
        # Detect operator based on number prefix
        operator = self.detect_operator(number)
        self.user_states[phone_number]['operator'] = operator
        self.user_states[phone_number]['state'] = 'operator_selection'
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Detected Operator: {operator.title()}"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "confirm_operator", "title": "Confirm Operator"}},
                        {"type": "reply", "reply": {"id": "other_operator", "title": "Other Operator"}}
                    ]
                }
            }
        }

    def detect_operator(self, number):
        # Simple operator detection based on number prefix
        prefix = number[:3]
        if prefix in ['700', '701', '702', '703', '704', '705', '706', '707', '708', '709']:
            return 'airtel'
        elif prefix in ['600', '601', '602', '603', '604', '605', '606', '607', '608', '609']:
            return 'jio'
        elif prefix in ['800', '801', '802', '803', '804', '805', '806', '807', '808', '809']:
            return 'vi'
        else:
            return 'bsnl'

    def send_operator_selection_message(self, phone_number):
        operators = ['airtel', 'jio', 'vi', 'bsnl']
        current_operator = self.user_states[phone_number]['operator']
        operators.remove(current_operator)
        
        buttons = [
            {"type": "reply", "reply": {"id": f"select_{op}", "title": op.title()}} 
            for op in operators
        ]
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Kindly select your SIM Operator:"
                },
                "action": {
                    "buttons": buttons
                }
            }
        }

    def handle_operator_selection(self, phone_number, message):
        if message == "confirm_operator":
            return self.send_plan_selection_message(phone_number)
        elif message == "other_operator":
            return self.send_operator_selection_message(phone_number)
        elif message.startswith("select_"):
            operator = message.split("_")[1]
            self.user_states[phone_number]['operator'] = operator
            return self.send_plan_selection_message(phone_number)
        else:
            return self.send_invalid_input_message(phone_number)

    def send_plan_selection_message(self, phone_number):
        operator = self.user_states[phone_number]['operator']
        plans = self.recharge_plans[operator]
        self.user_states[phone_number]['state'] = 'plan_selection'
        
        buttons = [
            {"type": "reply", "reply": {"id": f"plan_{i+1}", "title": f"Plan {i+1}: ₹{plan['amount']} - {plan['days']} Days"}}
            for i, plan in enumerate(plans)
        ]
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Available Recharge Plans for {operator.title()}:"
                },
                "action": {
                    "buttons": buttons
                }
            }
        }

    def handle_plan_selection(self, phone_number, message):
        if message.startswith("plan_"):
            plan_index = int(message.split("_")[1]) - 1
            operator = self.user_states[phone_number]['operator']
            plan = self.recharge_plans[operator][plan_index]
            self.user_states[phone_number]['selected_plan'] = plan
            return self.send_recharge_summary(phone_number)
        else:
            return self.send_invalid_input_message(phone_number)

    def send_recharge_summary(self, phone_number):
        number = self.user_states[phone_number]['current_number']
        operator = self.user_states[phone_number]['operator']
        plan = self.user_states[phone_number]['selected_plan']
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Recharge Summary:\n\nMobile Number: {number}\nOperator: {operator.title()}\nPlan: ₹{plan['amount']} - {plan['days']} Days"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "proceed_payment", "title": "Proceed Payment"}},
                        {"type": "reply", "reply": {"id": "change_plan", "title": "Change Plan"}},
                        {"type": "reply", "reply": {"id": "cancel_recharge", "title": "Cancel Recharge"}}
                    ]
                }
            }
        }

    def send_payment_options(self, phone_number):
        self.user_states[phone_number]['state'] = 'payment'
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Choose your payment method:"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "whatsapp_pay", "title": "WhatsApp Pay"}},
                        {"type": "reply", "reply": {"id": "phonepe", "title": "PhonePe"}},
                        {"type": "reply", "reply": {"id": "paytm", "title": "Paytm"}}
                    ]
                }
            }
        }

    def handle_payment(self, phone_number, message):
        if message == "proceed_payment":
            return self.send_payment_options(phone_number)
        elif message in ["whatsapp_pay", "phonepe", "paytm"]:
            return self.process_payment(phone_number, message)
        elif message == "change_plan":
            return self.send_plan_selection_message(phone_number)
        elif message == "cancel_recharge":
            return self.send_cancellation_message(phone_number)
        else:
            return self.send_invalid_input_message(phone_number)

    def process_payment(self, phone_number, payment_method):
        # Simulate payment processing
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Recharge Processing..."
            }
        }

    def send_success_message(self, phone_number):
        number = self.user_states[phone_number]['current_number']
        operator = self.user_states[phone_number]['operator']
        plan = self.user_states[phone_number]['selected_plan']
        transaction_id = f"TXN{int(time.time())}"
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Recharge Successful!\n\nTransaction ID: {transaction_id}\nMobile Number: {number}\nOperator: {operator.title()}\nPlan: ₹{plan['amount']} - {plan['days']} Days\n\nHow was your experience?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "rating_1", "title": "⭐"}},
                        {"type": "reply", "reply": {"id": "rating_2", "title": "⭐⭐"}},
                        {"type": "reply", "reply": {"id": "rating_3", "title": "⭐⭐⭐"}},
                        {"type": "reply", "reply": {"id": "rating_4", "title": "⭐⭐⭐⭐"}},
                        {"type": "reply", "reply": {"id": "rating_5", "title": "⭐⭐⭐⭐⭐"}}
                    ]
                }
            }
        }

    def send_cancellation_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Recharge cancelled. Thank you for using Aisyncy Recharge!"
            }
        }

    def process_recharge(self, phone_number, message):
        if phone_number not in self.user_states:
            return self.handle_initial_state(message, phone_number)
        
        current_state = self.user_states[phone_number]['state']
        
        if current_state == 'number_selection':
            return self.handle_number_selection(phone_number, message)
        elif current_state == 'operator_selection':
            return self.handle_operator_selection(phone_number, message)
        elif current_state == 'plan_selection':
            return self.handle_plan_selection(phone_number, message)
        elif current_state == 'payment':
            return self.handle_payment(phone_number, message)
        
        return self.send_invalid_input_message(phone_number) 