from app import app
import os
from flask import request

# This is required for Vercel serverless functions
def handler(event, context):
    with app.request_context(event):
        return app.full_dispatch_request()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000))) 