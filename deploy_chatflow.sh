#!/bin/bash
# This script deploys the updated ChatFlowController and main.py to GCP Cloud Run

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set service name and region
SERVICE_NAME="aisyncy-service"
REGION="asia-south1"

echo -e "${YELLOW}Deploying Aisyncy Recharge with ChatFlow to GCP Cloud Run...${NC}"

# Check if git is available and the directory is a git repository
if command -v git &> /dev/null && [ -d .git ]; then
    echo "Committing changes to git for tracking..."
    git add config.py main.py src/chatflow/ChatFlowController_new.py
    git commit -m "Update WhatsApp integration with ChatFlowController"
fi

# Deploy to GCP Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME --source . --region $REGION --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Deployment successful!${NC}"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
    
    echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
    echo -e "${YELLOW}Testing the webhook...${NC}"
    
    # Test the webhook
    curl -s "$SERVICE_URL/webhook_test" | jq .
    
    echo -e "${GREEN}Deployment and testing complete!${NC}"
    echo -e "${YELLOW}Important: Send a test message to your WhatsApp Business number to verify the chatflow integration.${NC}"
else
    echo -e "${RED}Deployment failed!${NC}"
fi 