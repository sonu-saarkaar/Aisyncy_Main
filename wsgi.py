from app import app
import os
from flask import request, jsonify

# This is required for Vercel serverless functions
def handler(event, context):
    try:
        # Convert Vercel event to Flask request
        headers = event.get('headers', {})
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body', '')
        
        # Create request context
        with app.request_context({
            'path': path,
            'method': method,
            'headers': headers,
            'data': body
        }):
            return app.full_dispatch_request()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': jsonify({'error': str(e)}).get_data(as_text=True)
        }

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000))) 