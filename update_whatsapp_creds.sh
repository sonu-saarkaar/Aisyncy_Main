#!/bin/bash

# This script updates the WhatsApp API credentials for your Cloud Run service

# Replace these values with your actual WhatsApp API credentials
WHATSAPP_PHONE_NUMBER_ID="YOUR_WHATSAPP_PHONE_NUMBER_ID"  # Replace with your actual Phone Number ID
WHATSAPP_ACCESS_TOKEN="YOUR_WHATSAPP_ACCESS_TOKEN"        # Replace with your actual WhatsApp API Token
SERVICE_NAME="aisyncy-service"                           # Your Cloud Run service name
REGION="asia-south1"                                     # Your service region

# Print warning
echo "Make sure to replace the placeholder values in this script with your actual WhatsApp API credentials!"
echo "WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN must be valid values from Meta Developer Portal"
echo ""

# Confirm before proceeding
read -p "Have you replaced the credentials with actual values? (y/n): " CONFIRM
if [[ $CONFIRM != "y" && $CONFIRM != "Y" ]]; then
  echo "Aborting. Please edit this script with your actual credentials first."
  exit 1
fi

# Update the service
echo "Updating WhatsApp credentials for $SERVICE_NAME in $REGION..."
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --set-env-vars=WHATSAPP_PHONE_NUMBER_ID=$WHATSAPP_PHONE_NUMBER_ID,WHATSAPP_ACCESS_TOKEN=$WHATSAPP_ACCESS_TOKEN,WHATSAPP_TOKEN=$WHATSAPP_ACCESS_TOKEN

# Check if update was successful
if [ $? -eq 0 ]; then
  echo "WhatsApp credentials updated successfully!"
  echo "Your service will restart with the new credentials. It might take a minute to take effect."
  echo "After the service restarts, verify your webhook is working at: https://$SERVICE_NAME-XXXX-$REGION.run.app/webhook_test"
else
  echo "Failed to update WhatsApp credentials. Please check your gcloud configuration and try again."
fi 