from app import app
import os

# This is required for Vercel serverless functions
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000))) 