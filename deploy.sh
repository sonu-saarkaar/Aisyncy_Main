#!/bin/bash
# Shell script to deploy the updated ChatFlowController and main.py to GCP App Engine

echo -e "\033[33mDeploying Aisyncy Recharge with ChatFlow to GCP App Engine...\033[0m"

# Verify MongoDB Atlas connection
echo -e "\033[33mVerifying MongoDB Atlas connection...\033[0m"
MONGO_CONNECTION_STRING=$(grep "MONGO_URI:" app.yaml | sed -E 's/^.*MONGO_URI:\s+"(.+?)".*$/\1/')

if [[ $MONGO_CONNECTION_STRING == *"mongodb+srv://username:password@"* ]]; then
    echo -e "\033[31mWARNING: You haven't updated the MongoDB Atlas connection string in app.yaml!\033[0m"
    echo -e "\033[31mPlease follow the instructions in MONGODB_SETUP.md to set up MongoDB Atlas.\033[0m"
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo -e "\033[31mDeployment canceled.\033[0m"
        exit 1
    fi
fi

# Test MongoDB connection
echo -e "\033[33mTesting MongoDB connection...\033[0m"
python test_mongo_connection.py
if [ $? -ne 0 ]; then
    echo -e "\033[31mMongoDB connection test failed!\033[0m"
    read -p "MongoDB connection test failed. Do you want to continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo -e "\033[31mDeployment canceled.\033[0m"
        exit 1
    fi
fi

# Check if Git is available
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "Git detected: $GIT_VERSION"
    
    # Check if this is a git repository
    if [ -d ".git" ]; then
        echo -e "\033[33mCommitting changes to git for tracking...\033[0m"
        git add config.py main.py src/chatflow/ChatFlowController_new.py app.yaml
        git commit -m "Update WhatsApp integration with ChatFlowController and MongoDB Atlas"
    fi
else
    echo -e "\033[33mGit not available, skipping source control operations.\033[0m"
fi

# Deploy to GCP App Engine
echo -e "\033[33mDeploying to App Engine...\033[0m"
gcloud app deploy app.yaml --quiet

if [ $? -eq 0 ]; then
    echo -e "\033[32mDeployment successful!\033[0m"
    
    # Get the service URL
    SERVICE_URL=$(gcloud app browse --no-launch-browser)
    
    echo -e "\033[32mService URL: $SERVICE_URL\033[0m"
    echo -e "\033[33mTesting the webhook...\033[0m"
    
    # Test the webhook
    curl -s "$SERVICE_URL/webhook_test" | python -m json.tool || echo -e "\033[33mWarning: Could not test webhook.\033[0m"
    
    echo -e "\033[33mShowing logs...\033[0m"
    gcloud app logs tail --limit=20
    
    echo -e "\033[32mDeployment and testing complete!\033[0m"
    echo -e "\033[33mImportant: Send a test message 'hi' to your WhatsApp Business number to verify the chatflow integration.\033[0m"
else
    echo -e "\033[31mDeployment failed!\033[0m"
fi 