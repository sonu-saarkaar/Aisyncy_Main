#!/bin/bash
# This script deploys the WhatsApp credential fixes to your GCP Cloud Run service

# Set the service name and region
SERVICE_NAME="aisyncy-service"
REGION="asia-south1"

# Create a temporary directory for deployment
mkdir -p deploy_fix
cd deploy_fix

# Copy the necessary files
cp ../config_fix.py .
cp ../main.py .
cp ../app.yaml .

# Apply the fix to main.py
cat ../main_fix.py > temp_main.py
cat main.py >> temp_main.py
mv temp_main.py main.py

# Deploy to GCP
echo "Deploying fixes to GCP Cloud Run..."
gcloud run deploy $SERVICE_NAME --source . --region $REGION

# Clean up
cd ..
rm -rf deploy_fix

echo "✅ Deployment complete!" 