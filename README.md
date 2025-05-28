# Aisyncy Recharge Chatbot

An intelligent chatbot system that handles recharge-related queries and general conversations.

## Features

- General conversation handling using ChatterBot
- Recharge flow processing
- Natural language understanding for recharge requests
- Multi-platform support
- Easy-to-extend architecture

## Prerequisites

- Python 3.7 or higher
- pip package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aisyncy-recharge.git
cd aisyncy-recharge
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install chatterbot chatterbot-corpus
```

## Setup

1. Configure the chatbot settings (optional):
   - Edit chatbot/core.py to customize bot behavior
   - Modify recharge keywords in is_recharge_message()

2. Run the chatbot:
```bash
python chatbot.py
```

## Usage Examples

### General Conversation
```
You: Hello
Bot: Hi there! How can I help you today?

You: What can you do?
Bot: I can help you with recharge-related queries and general conversation.
```

### Recharge Flow
```
You: I want to recharge my phone
Bot: Sure! Please enter your phone number:
You: 1234567890
Bot: Enter recharge amount:
You: 100
Bot: Confirming recharge of Rs.100 for 1234567890...
```

## Project Structure

```
Aisyncy Recharge/
├── chatbot/
│   ├── __init__.py
│   └── core.py       # Core chatbot functionality
├── chatbot.py        # Main entry point
└── README.md         # Documentation
```

## Development

### Adding New Features
1. Extend the AisyncyChatBot class in core.py
2. Add new message handlers in handle_message()
3. Create new utility functions as needed

### Testing
Run the chatbot and test different conversation flows:
- General queries
- Recharge requests
- Error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use and modify as needed.

## Support

For issues and questions, please create an issue in the repository.
# Aisyncy_Main
# Aisyncy_Main
