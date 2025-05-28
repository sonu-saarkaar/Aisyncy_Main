# GCP Deployment Guide

This guide will help you deploy the Aisyncy Recharge application to Google Cloud Platform (GCP).

## Prerequisites

1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Create a GCP project and enable billing
3. Install Docker
4. Set up the following environment variables:
   - MONGO_URI
   - ADMIN_USERNAME
   - ADMIN_PASSWORD
   - WHATSAPP_PHONE_NUMBER_ID
   - WHATSAPP_ACCESS_TOKEN
   - SECRET_KEY

## Deployment Steps

1. **Initialize GCP**
   ```bash
   gcloud init
   gcloud auth login
   ```

2. **Set your project ID**
   Edit the `deploy.sh` file and replace `your-project-id` with your actual GCP project ID.

3. **Make the deployment script executable**
   ```bash
   chmod +x deploy.sh
   ```

4. **Run the deployment script**
   ```bash
   ./deploy.sh
   ```

## Environment Variables

Create a `.env` file with the following variables:
```
MONGO_URI=your_mongodb_uri
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
SECRET_KEY=your_secret_key
```

## Post-Deployment

1. The application will be available at: `https://aisyncy-recharge-asia-south1.run.app`
2. Monitor the deployment in the GCP Console
3. Set up any necessary domain mapping if required

## Troubleshooting

1. Check Cloud Run logs in GCP Console
2. Verify environment variables are set correctly
3. Ensure all required services are enabled in your GCP project:
   - Cloud Run
   - Cloud Build
   - Container Registry

## Maintenance

To update the deployment:
1. Make your code changes
2. Run the deployment script again:
   ```bash
   ./deploy.sh
   ```

## Additional Resources

- [Google App Engine Documentation](https://cloud.google.com/appengine/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp/api/webhooks) 