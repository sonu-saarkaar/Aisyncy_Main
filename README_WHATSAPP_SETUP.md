# WhatsApp API Setup Guide

## Problem Identified
Your WhatsApp integration is failing because of incorrect or missing WhatsApp API credentials. The error logs show:
```
"POST /v17.0/default_phone_number_id/messages HTTP/1.1" 401 152
ERROR - Network error sending WhatsApp message: 401 Client Error: Unauthorized
```

## How to Fix

### 1. Get Your Meta WhatsApp Credentials

1. Go to [Meta Developer Portal](https://developers.facebook.com/)
2. Navigate to your WhatsApp Business app
3. Find your:
   - **Phone Number ID** - This is a unique identifier for your WhatsApp phone number
   - **Access Token** - This is used for authentication with the WhatsApp API

### 2. Update Your GCP Environment Variables

The fastest way to update your WhatsApp credentials is to use our script:

1. Edit the `update_whatsapp_creds.sh` file and replace:
   ```
   WHATSAPP_PHONE_NUMBER_ID="YOUR_WHATSAPP_PHONE_NUMBER_ID"
   WHATSAPP_ACCESS_TOKEN="YOUR_WHATSAPP_ACCESS_TOKEN"
   ```
   with your actual values from the Meta Developer Portal.

2. Run the script to update your GCP deployment:
   ```
   chmod +x update_whatsapp_creds.sh
   ./update_whatsapp_creds.sh
   ```

3. Alternatively, you can update the variables directly with this command:
   ```
   gcloud run services update aisyncy-service \
     --region=asia-south1 \
     --set-env-vars=WHATSAPP_PHONE_NUMBER_ID=YOUR_ACTUAL_ID,WHATSAPP_ACCESS_TOKEN=YOUR_ACTUAL_TOKEN
   ```

### 3. Test Your WhatsApp Webhook

After updating your credentials, use the test tool to verify your configuration:

```
python test_webhook.py https://aisyncy-service-1040441775881.asia-south1.run.app
```

### 4. Verify WhatsApp Webhook Registration

Make sure your webhook is properly registered in the Meta Developer Portal:

1. Go to your WhatsApp Business app in Meta Developer Portal
2. Navigate to Webhooks configuration
3. Ensure your callback URL is set to:
   ```
   https://aisyncy-service-1040441775881.asia-south1.run.app/webhook
   ```
4. The verify token should match the one in your app (default is "12345")
5. Make sure you're subscribed to the `messages` webhook field

## Troubleshooting

If you still have issues after updating your credentials:

1. Check the Cloud Run logs for detailed error messages
2. Use the `/webhook_test` endpoint to verify your configuration:
   ```
   https://aisyncy-service-1040441775881.asia-south1.run.app/webhook_test
   ```
3. Ensure your WhatsApp Business Account is properly set up and active

## Common Issues

1. **401 Unauthorized**: Your access token is invalid or expired
2. **Missing Phone Number ID**: The `default_phone_number_id` value means your environment variable isn't set
3. **Webhook Verification Fails**: Check that your verify token matches between GCP and Meta Developer Portal 