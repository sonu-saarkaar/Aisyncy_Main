import os
import logging
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("dotenv not found, using environment variables directly")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WhatsApp API Configuration - Hardcoded for reliability
WHATSAPP_PHONE_NUMBER_ID = "104612292631543"
WHATSAPP_ACCESS_TOKEN = "EAAwFo4oYpGgBO8ZAgKQxZB7dxQY8XnArrLxRsvuhZARG8NJVwQPiJ15EuJq30fV1x4eohl7zT4tHwegGaBcpqtVZADA8QOLKgJwL92etZC7HbZCeujbtr01yxcbFiZBFMUtfPr8RtriO8ZCxXCSWUvMxOynVhmy4ZBHtUzcbTGzLxPUdnIJMeyolNKjcpD376l1WZAJQZDZD"
WHATSAPP_TOKEN = WHATSAPP_ACCESS_TOKEN  # For compatibility with existing code
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# Webhook verification token
VERIFY_TOKEN = "12345"

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    logger.warning("No MONGO_URI found in environment, using localhost for development only")
    MONGO_URI = 'mongodb://localhost:27017/aisyncy_recharge'
MONGO_DB = os.environ.get('MONGO_DB', 'aisyncy_recharge')

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
USE_OPENAI = OPENAI_API_KEY is not None and len(OPENAI_API_KEY) > 0
if USE_OPENAI:
    logger.info("OpenAI integration enabled")
else:
    logger.warning("OpenAI API key not configured - AI enhancement features will be disabled")

# Recharge API Configuration
RECHARGE_API_KEY = os.getenv('RECHARGE_API_KEY')

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Admin Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')

# App Secret Key
SECRET_KEY = os.environ.get('SECRET_KEY', '483e9d3234249efb49ab9383b786a2a7')

# Log the configuration on loading
logger.info("Config loaded with the following settings:")
logger.info(f"WhatsApp Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")
logger.info(f"WhatsApp API URL: {WHATSAPP_API_URL}")
logger.info(f"MongoDB URI: {'[REDACTED]' if MONGO_URI else 'Not configured'}")
logger.info(f"MongoDB Database: {MONGO_DB}")
logger.info(f"Admin Username: {ADMIN_USERNAME}")

# API URL is defined only if PHONE_NUMBER_ID is actually set
if WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_PHONE_NUMBER_ID != 'default_phone_number_id':
    WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
else:
    # Log warning but don't crash
    print("WARNING: WHATSAPP_PHONE_NUMBER_ID not properly configured")
    WHATSAPP_API_URL = None 