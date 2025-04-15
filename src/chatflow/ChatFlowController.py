import time

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

    def handle_initial_state(self, message, phone_number):
        # Check for greeting words
        greeting_words = ['hi', 'hello', 'hye', 'recharge', 'recharge now', 'namaste', 'hey']
        if message.lower().strip() in greeting_words:
            # Move to welcome state
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

    def send_explore_aisyncy_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "🌟 Explore Aisyncy Features:\n\nDiscover our services and features. What would you like to know more about?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "services", "title": "Our Services"}},
                        {"type": "reply", "reply": {"id": "auto_payment", "title": "Auto Payment"}},
                        {"type": "reply", "reply": {"id": "rise_issue", "title": "Rise Issue"}}
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
                        {"type": "reply", "reply": {"id": "confirm_operator", "title": "Confirm"}},
                        {"type": "reply", "reply": {"id": "other_operator", "title": "Other Operator"}}
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
                    "id": f"select_{op}",
                    "title": op.upper()
                }
            })
        
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
        
        # First show the common features with View Plans button
        initial_message = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "• All plans include unlimited calls\n• Free SMS per day\n• Data as per plan"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "view_plans", "title": "View Plans"}},
                        {"type": "reply", "reply": {"id": "back_operator", "title": "Back"}}
                    ]
                }
            }
        }

        # When user clicks View Plans, show the list view
        if self.user_states[phone_number].get('show_plans_list'):
            # Create the list view message
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "View Plans"
                },
                "body": {
                    "text": f"Select a {operator.upper()} recharge plan"
                },
                "action": {
                    "button": "Select Plan",
                    "sections": [
                        {
                            "title": "📱 POPULAR",
                            "rows": [
                                {
                                    "id": f"plan_{i}",
                                    "title": f"₹{plan['amount']} - {plan['days']} Days",
                                    "description": f"📱 {plan['data']} • Unlimited Calls"
                                } for i, plan in enumerate(plans) if plan['days'] <= 30
                            ]
                        },
                        {
                            "title": "♾️ UNLIMITED",
                            "rows": [
                                {
                                    "id": f"plan_{i}",
                                    "title": f"₹{plan['amount']} - {plan['days']} Days",
                                    "description": f"📱 {plan['data']} • Unlimited Calls"
                                } for i, plan in enumerate(plans) if 30 < plan['days'] <= 84
                            ]
                        },
                        {
                            "title": "📊 DATA",
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
        
        return initial_message

    def send_recharge_summary(self, phone_number):
        number = self.user_states[phone_number]['current_number']
        operator = self.user_states[phone_number]['operator']
        plan = self.user_states[phone_number]['selected_plan']
        masked_number = number[:5] + 'XXXXX'
        
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
                        {"type": "reply", "reply": {"id": "proceed_payment", "title": "Proceed"}},
                        {"type": "reply", "reply": {"id": "change_plan", "title": "Change Plan"}},
                        {"type": "reply", "reply": {"id": "cancel_recharge", "title": "Cancel Recharge"}}
                    ]
                }
            }
        }

    def send_payment_options(self, phone_number):
        plan = self.user_states[phone_number]['selected_plan']
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Please select your payment mode for ₹{plan['amount']}:"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "upi_payment", "title": "UPI Payment"}},
                        {"type": "reply", "reply": {"id": "card_payment", "title": "Card Payment"}},
                        {"type": "reply", "reply": {"id": "netbanking", "title": "Netbanking"}}
                    ]
                }
            }
        }

    def send_upi_payment_options(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Please select your UPI app:"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "whatsapp_pay", "title": "WhatsApp Pay"}},
                        {"type": "reply", "reply": {"id": "paytm", "title": "Paytm"}},
                        {"type": "reply", "reply": {"id": "phonepe", "title": "PhonePe"}},
                        {"type": "reply", "reply": {"id": "gpay", "title": "GPay"}}
                    ]
                }
            }
        }

    def send_success_message(self, phone_number):
        number = self.user_states[phone_number]['current_number']
        operator = self.user_states[phone_number]['operator']
        plan = self.user_states[phone_number]['selected_plan']
        transaction_id = f"#{int(time.time())}"
        masked_number = number[:5] + 'XXXXX'
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Transaction ID: {transaction_id}\nRecharge of ₹{plan['amount']} for {masked_number} was successful.\n\nThank you for using Aisyncy Recharge!\nWhat would you like to do next?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "auto_recharge", "title": "Auto Recharge Setup"}},
                        {"type": "reply", "reply": {"id": "raise_issue", "title": "Raise an Issue"}},
                        {"type": "reply", "reply": {"id": "give_feedback", "title": "Give Feedback"}}
                    ]
                }
            }
        }

    def send_auto_recharge_info(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Auto Recharge means:\nRecharge will auto-deduct & auto-apply every 28 days."
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "setup_auto_recharge", "title": "Set Auto Recharge"}},
                        {"type": "reply", "reply": {"id": "back_to_main", "title": "Back"}}
                    ]
                }
            }
        }

    def send_feedback_prompt(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "How was your experience with Aisyncy Recharge?"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "rating_awesome", "title": "Awesome"}},
                        {"type": "reply", "reply": {"id": "rating_good", "title": "Good"}},
                        {"type": "reply", "reply": {"id": "rating_average", "title": "Average"}}
                    ]
                }
            }
        }

    def send_payment_confirmation(self, phone_number):
        plan = self.user_states[phone_number]['selected_plan']
        number = self.user_states[phone_number]['current_number']
        masked_number = number[:5] + 'XXXXX'
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"📱 Payment Confirmation\n\nNumber: {masked_number}\nAmount: ₹{plan['amount']}\n\nBy proceeding, you agree to make the payment for the recharge."
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "confirm_payment", "title": "Confirm & Pay"}},
                        {"type": "reply", "reply": {"id": "back_to_plans", "title": "Back"}},
                        {"type": "reply", "reply": {"id": "cancel_payment", "title": "Cancel"}}
                    ]
                }
            }
        }

    def process_recharge(self, phone_number, message):
        # Handle exit/cancel commands globally
        if message.lower() in ['exit', 'cancel', 'cancel recharge']:
            if phone_number in self.user_states:
                del self.user_states[phone_number]
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": "Session cancelled. Thank you for using Aisyncy Recharge! Type 'hi' to start again."
                }
            }

        # Check for greeting words to restart flow
        greeting_words = ['hi', 'hello', 'hye', 'recharge', 'recharge now', 'namaste', 'hey']
        if message.lower().strip() in greeting_words:
            self.user_states[phone_number] = {
                'state': 'welcome',
                'current_number': phone_number
            }
            return self.send_welcome_message(phone_number)

        if phone_number not in self.user_states:
            return self.send_welcome_message(phone_number)
        
        current_state = self.user_states[phone_number]['state']
        
        if current_state == 'welcome':
            if message == "recharge_now":
                self.user_states[phone_number]['state'] = 'number_selection'
                return self.send_number_confirmation(phone_number, phone_number)
            elif message == "explore_aisyncy":
                self.user_states[phone_number]['state'] = 'explore'
                return self.send_explore_aisyncy_message(phone_number)
            else:
                return self.send_welcome_message(phone_number)

        elif current_state == 'explore':
            if message == "services":
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": "📱 Our Services:\n\n• Mobile Recharge\n• DTH Recharge\n• Bill Payments\n• Electricity Bill\n• Gas Bill\n• Water Bill\n\nWhat would you like to do?"
                        },
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "recharge_now", "title": "Recharge Now"}},
                                {"type": "reply", "reply": {"id": "back_explore", "title": "Back"}},
                                {"type": "reply", "reply": {"id": "main_menu", "title": "Main Menu"}}
                            ]
                        }
                    }
                }
            elif message == "auto_payment":
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": "💳 Auto Payment System:\n\n• Set up automatic recharges\n• Never miss a recharge\n• Choose payment frequency\n• Easy cancellation anytime\n• Get reminders before deduction"
                        },
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "setup_auto", "title": "Setup Auto-Pay"}},
                                {"type": "reply", "reply": {"id": "back_explore", "title": "Back"}},
                                {"type": "reply", "reply": {"id": "main_menu", "title": "Main Menu"}}
                            ]
                        }
                    }
                }
            elif message == "support":
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": "🎯 Support Options:\n\n• 24/7 Customer Support\n• File a Complaint\n• Track Status\n• Request Callback\n• Visit Website"
                        },
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "request_callback", "title": "Request Callback"}},
                                {"type": "reply", "reply": {"id": "file_complaint", "title": "File Complaint"}},
                                {"type": "reply", "reply": {"id": "back_explore", "title": "Back"}}
                            ]
                        }
                    }
                }
            elif message in ["back_explore", "back_to_explore"]:
                return self.send_explore_aisyncy_message(phone_number)
            elif message == "main_menu":
                self.user_states[phone_number]['state'] = 'welcome'
                return self.send_welcome_message(phone_number)
            else:
                return self.send_explore_aisyncy_message(phone_number)

        elif current_state == 'number_selection':
            if message == "confirm_number":
                return self.send_operator_confirmation_message(phone_number, self.user_states[phone_number]['current_number'])
            elif message == "other_number":
                return self.send_enter_number_message(phone_number)
            else:
                number = ''.join(filter(str.isdigit, message))
                if len(number) == 10:
                    self.user_states[phone_number]['current_number'] = number
                    return self.send_operator_confirmation_message(phone_number, number)
                else:
                    return self.send_number_confirmation(phone_number, phone_number)
                    
        elif current_state == 'operator_selection':
            if message in ["confirm_operator", "Yes, Confirm"]:  # Handle both button text and ID
                self.user_states[phone_number]['state'] = 'plan_selection'
                return self.send_plan_selection_message(phone_number)
            elif message in ["other_operator", "No, Change Operator"]:  # Handle both button text and ID
                return self.send_operator_selection_message(phone_number)
            elif message.startswith("select_"):
                operator = message.split("_")[1]
                self.user_states[phone_number]['operator'] = operator
                self.user_states[phone_number]['state'] = 'plan_selection'
                return self.send_plan_selection_message(phone_number)
            else:
                return self.send_operator_selection_message(phone_number)
                
        elif current_state == 'plan_selection':
            if message == "view_plans":
                self.user_states[phone_number]['show_plans_list'] = True
                return self.send_plan_selection_message(phone_number)
            elif message.startswith("plan_"):
                try:
                    plan_index = int(message.split('_')[1])
                    operator = self.user_states[phone_number]['operator']
                    plans = self.recharge_plans[operator]
                    
                    if plan_index < len(plans):
                        selected_plan = plans[plan_index]
                        self.user_states[phone_number]['selected_plan'] = selected_plan
                        self.user_states[phone_number]['state'] = 'recharge_summary'
                        return self.send_recharge_summary(phone_number)
                    else:
                        return self.send_plan_selection_message(phone_number)
                except (ValueError, IndexError):
                    return self.send_plan_selection_message(phone_number)
            else:
                return self.send_plan_selection_message(phone_number)
                
        elif current_state == 'recharge_summary':
            if message == "proceed_payment":
                self.user_states[phone_number]['state'] = 'payment_confirmation'
                return self.send_payment_confirmation(phone_number)
            elif message == "change_plan":
                self.user_states[phone_number]['state'] = 'plan_selection'
                return self.send_plan_selection_message(phone_number)
            elif message == "cancel_recharge":
                if phone_number in self.user_states:
                    del self.user_states[phone_number]
                return self.send_cancellation_message(phone_number)
            else:
                return self.send_recharge_summary(phone_number)

        elif current_state == 'payment_confirmation':
            if message == "confirm_payment":
                # Simulate successful payment
                time.sleep(2)  # Add a small delay to simulate processing
                transaction_id = f"TR{int(time.time())}"
                plan = self.user_states[phone_number]['selected_plan']
                number = self.user_states[phone_number]['current_number']
                masked_number = number[:5] + 'XXXXX'
                
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": f"✅ Payment Successful!\n\n📱 Number: {masked_number}\n💰 Amount: ₹{plan['amount']}\n🔖 Transaction ID: {transaction_id}\n⏱️ Validity: {plan['days']} days\n\nYour recharge will be processed within 2 minutes.\nThank you for using Aisyncy Recharge!"
                        },
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "auto_recharge", "title": "Set Auto-Recharge"}},
                                {"type": "reply", "reply": {"id": "rise_issue", "title": "Rise Issue"}},
                                {"type": "reply", "reply": {"id": "feedback", "title": "feedback"}}
                            ]
                        }
                    }
                }
            elif message == "back_to_plans":
                self.user_states[phone_number]['state'] = 'recharge_summary'
                return self.send_recharge_summary(phone_number)
            elif message == "cancel_payment":
                if phone_number in self.user_states:
                    del self.user_states[phone_number]
                return {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "Payment cancelled. Type 'hi' to start a new recharge."
                    }
                }
            else:
                return self.send_payment_confirmation(phone_number)

        return self.send_welcome_message(phone_number)

    def send_invalid_input_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Please select a valid option from the buttons provided."
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

    def send_enter_number_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Please enter the 10-digit mobile number you want to recharge:"
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

    def send_raise_issue_message(self, phone_number):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Please describe your issue (Example format shown):\n\nIssue Type: [Recharge/Payment/Other]\nDescription: [Brief description of the issue]\nTransaction ID: [If applicable]"
            }
        }

    def process_payment(self, phone_number, payment_method):
        # Simulate payment processing
        time.sleep(2)  # Simulate payment processing time
        
        # Update user state to post_recharge
        self.user_states[phone_number]['state'] = 'post_recharge'
        
        # Generate transaction details
        transaction_id = f"#{int(time.time())}"
        plan = self.user_states[phone_number]['selected_plan']
        
        # Send success message
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"🎉 Payment Successful!\n\nTransaction ID: {transaction_id}\nAmount: ₹{plan['amount']}\nPayment Mode: {payment_method.upper()}\n\nYour recharge will be processed within 2 minutes.\nThank you for using Aisyncy Recharge!"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "auto_recharge", "title": "Set Auto-Recharge"}},
                        {"type": "reply", "reply": {"id": "new_recharge", "title": "New Recharge"}},
                        {"type": "reply", "reply": {"id": "get_support", "title": "Get Support"}}
                    ]
                }
            }
        }

    def send_card_payment_options(self, phone_number):
        plan = self.user_states[phone_number]['selected_plan']
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Select card type for payment of ₹{plan['amount']}:"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "credit_card", "title": "Credit Card"}},
                        {"type": "reply", "reply": {"id": "debit_card", "title": "Debit Card"}},
                        {"type": "reply", "reply": {"id": "back_payment", "title": "Back"}}
                    ]
                }
            }
        }

    def send_netbanking_options(self, phone_number):
        plan = self.user_states[phone_number]['selected_plan']
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"Select your bank for payment of ₹{plan['amount']}:"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "sbi_bank", "title": "SBI"}},
                        {"type": "reply", "reply": {"id": "hdfc_bank", "title": "HDFC"}},
                        {"type": "reply", "reply": {"id": "icici_bank", "title": "ICICI"}}
                    ]
                }
            }
        }

class ChatFlowController:
    def __init__(self):
        self.recharge_controller = RechargeController()
        self.user_states = {}
        self.current_operator = None

    def process_message(self, message):
        if not message:
            return "Please enter a valid message."

        message = message.lower().strip()

        # Store current operator for plan selection
        if message in ['jio', 'airtel', 'vi', 'bsnl']:
            self.current_operator = message

        # Check for greeting words
        greeting_words = ['hi', 'hello', 'hye', 'recharge', 'recharge now', 'namaste', 'hey']
        if message in greeting_words:
            return self.get_welcome_message()

        # Check for number input
        if message.isdigit():
            if len(message) == 10:
                return self.handle_number_input(message)
            elif len(message) <= 2:  # For plan selection by number
                return self.handle_plan_selection(message)

        # Check for operator selection
        operators = ['jio', 'airtel', 'vi', 'bsnl']
        if message in operators:
            return self.handle_operator_selection(message)

        # Check for plan selection
        if message.startswith('plan_'):
            return self.handle_plan_selection(message)

        # Check for confirmation
        if message == 'confirm':
            return "Great! Please select your payment method:\n1. UPI\n2. Card\n3. Netbanking"

        # Check for back command
        if message == 'back' and self.current_operator:
            return self.handle_operator_selection(self.current_operator)

        # Default response
        return "I'm not sure I understand. Please try again or type 'hi' to start over."

    def get_welcome_message(self):
        return "Welcome to Aisyncy Recharge!\n\nI can help you recharge your mobile number. Please enter your 10-digit mobile number to get started."

    def handle_number_input(self, number):
        operator = self.recharge_controller.detect_operator(number)
        return f"I detected that your number belongs to {operator.upper()} network. Please confirm your operator:\n\n" + \
               "\n".join([f"• {op.upper()}" for op in ['jio', 'airtel', 'vi', 'bsnl']])

    def handle_operator_selection(self, operator):
        if operator not in self.recharge_controller.recharge_plans:
            return "Invalid operator. Please select from: JIO, AIRTEL, VI, BSNL"

        plans = self.recharge_controller.recharge_plans[operator]
        
        # First show common features
        initial_text = "• All plans include unlimited calls\n• Free SMS per day\n• Data as per plan\n\n"
        initial_text += "📱 View Plans\n"
        initial_text += "-----------------\n\n"
        
        # Categorize plans
        popular_plans = []
        unlimited_plans = []
        data_plans = []
        
        for i, plan in enumerate(plans):
            plan_text = (
                f"{i+1}. ₹{plan['amount']} - {plan['days']} Days\n"
                f"   📱 {plan['data']} • Unlimited Calls\n"
            )
            
            # Categorize based on criteria
            if plan['days'] <= 30:
                popular_plans.append(plan_text)
            elif 30 < plan['days'] <= 84:
                unlimited_plans.append(plan_text)
            elif float(plan['data'].split('GB')[0]) >= 2 or plan['days'] > 84:
                data_plans.append(plan_text)
        
        # Build the complete message with sections
        message = initial_text
        
        if popular_plans:
            message += "📱 POPULAR\n"
            message += "".join(popular_plans)
            message += "\n"
        
        if unlimited_plans:
            message += "♾️ UNLIMITED\n"
            message += "".join(unlimited_plans)
            message += "\n"
        
        if data_plans:
            message += "📊 DATA\n"
            message += "".join(data_plans)
            message += "\n"
        
        message += "\nTap to select an item (e.g., '1' for first plan)"
        
        return message

    def handle_plan_selection(self, selection):
        try:
            # Handle both 'plan_1' format and direct number input
            if selection.startswith('plan_'):
                plan_index = int(selection.split('_')[1]) - 1
            else:
                plan_index = int(selection) - 1

            # Get the selected plan
            if not self.current_operator:
                return "Please select an operator first."

            plans = self.recharge_controller.recharge_plans[self.current_operator]
            
            if 0 <= plan_index < len(plans):
                selected_plan = plans[plan_index]
                return (
                    f"Selected Plan Details:\n\n"
                    f"Amount: ₹{selected_plan['amount']}\n"
                    f"Validity: {selected_plan['days']} Days\n"
                    f"Data: {selected_plan['data']}\n"
                    f"Benefits: {selected_plan['description']}\n\n"
                    f"Type 'confirm' to proceed with recharge or 'back' to view plans again"
                )
            else:
                return "Invalid plan selection. Please select a valid plan number."
        except (ValueError, IndexError):
            return "Invalid selection. Please enter a valid plan number." 