# ChatFlow Integration Guide

## Overview

This guide will help you deploy and test the integration of ChatFlowController with your WhatsApp webhook handler in Aisyncy Recharge.

## Changes Made

1. **Updated WhatsApp Credentials** - Hardcoded the credentials to ensure reliable operation
2. **Integrated ChatFlowController** - Connected your custom ChatFlowController to the webhook handler
3. **Enhanced Message Handling** - Added support for interactive messages (buttons, lists)
4. **Improved Error Handling** - Better logging and error reporting

## Deployment Instructions

### Option 1: Using PowerShell (Windows)

1. Open PowerShell in your project directory
2. Run the deployment script:
   ```powershell
   .\Deploy-ChatFlow.ps1
   ```

### Option 2: Manual Deployment

1. Ensure all files are saved
2. Deploy to GCP Cloud Run using:
   ```bash
   gcloud run deploy aisyncy-service --source . --region=asia-south1 --allow-unauthenticated
   ```

## Testing the Integration

1. **Send a Test Message**:
   - Send a simple message like "hi" or "recharge" to your WhatsApp Business number
   - The system should respond with the welcome message and buttons defined in your ChatFlowController

2. **Test Button Interactions**:
   - Click on the buttons in the response to see if the chatflow navigates correctly
   - Try "Recharge Now" to see if it starts the recharge flow

3. **Test List Interactions**:
   - When plan selection or other list views appear, test selecting options
   - Verify that the flow proceeds correctly after each selection

## Common Issues and Solutions

1. **No Response to Messages**:
   - Check the GCP Cloud Run logs for errors
   - Verify WhatsApp Business API webhooks are configured correctly
   - Make sure your WhatsApp API credentials are valid

2. **Responses Not Following ChatFlow**:
   - Check for errors in the logs related to the ChatFlowController
   - Verify that the webhook handler is correctly passing messages to the controller

3. **Interactive Messages Not Working**:
   - Check the response format in the logs
   - Ensure WhatsApp Business API supports the interactive message types you're using

## Debugging

To view logs and debug issues:

1. **Check Cloud Run Logs**:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=aisyncy-service" --limit=50
   ```

2. **Test Webhook Endpoint**:
   - Visit `https://YOUR-SERVICE-URL/webhook_test` in a browser
   - This will return the current configuration and webhook status

## Next Steps

If you want to extend the chatflow:

1. Modify `ChatFlowController_new.py` to add new conversation flows
2. Update the webhook handler in `main.py` if you need to handle new message types
3. Re-deploy using the provided deployment script

## Support

If you encounter any issues, please refer to the logs first, then contact technical support with the specific error messages and timestamps. 