# Add this at the top of your main.py file
try:
    # Try to load our hardcoded configuration first
    from config_fix import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_TOKEN, WHATSAPP_API_URL, VERIFY_TOKEN
    print("Successfully loaded hardcoded WhatsApp credentials")
except ImportError:
    # Fall back to regular config if the fix file isn't present
    print("Hardcoded credentials not found, using environment variables")
    from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_TOKEN, WHATSAPP_API_URL, VERIFY_TOKEN 