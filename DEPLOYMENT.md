# Aisyncy Recharge GCP Deployment Guide

## MongoDB Configuration

### Issue: MongoDB Connection Refused 

The application was previously configured to use a local MongoDB instance (`mongodb://localhost:27017/`). When deployed to Google Cloud Platform, the application cannot connect to a MongoDB instance on localhost because:

1. App Engine instances don't have MongoDB installed locally
2. The localhost reference only works on your development machine

### Solution: Use MongoDB Atlas

Follow these steps to set up MongoDB Atlas and configure your application to use it:

1. **Create a MongoDB Atlas account** at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

2. **Create a new cluster** (you can use the free tier for testing)

3. **Configure network access**:
   - Go to Network Access in the Atlas dashboard
   - Add a new IP address: `0.0.0.0/0` to allow access from anywhere (you can restrict this later)

4. **Create a database user**:
   - Go to Database Access
   - Add a new user with read/write permissions

5. **Get your connection string**:
   - Go to Clusters → Connect → Connect your application
   - Copy the connection string which looks like: `mongodb+srv://username:password@cluster.mongodb.net/myFirstDatabase`
   - Replace `username` and `password` with your database user credentials
   - Replace `myFirstDatabase` with `aisyncy_recharge`

6. **Update app.yaml**:
   ```yaml
   env_variables:
     MONGO_URI: "mongodb+srv://username:password@cluster.mongodb.net/aisyncy_recharge"
     # other variables remain the same
   ```

7. **Deploy to GCP**:
   ```
   gcloud app deploy
   ```

## Troubleshooting MongoDB Connections

If you're still experiencing MongoDB connection issues:

1. **Check your logs**: 
   ```
   gcloud app logs tail
   ```

2. **Verify network settings** in MongoDB Atlas:
   - Ensure that your App Engine IP is allowed or use 0.0.0.0/0 temporarily

3. **Check credentials** in the Atlas dashboard

4. **Test locally** with the Atlas connection string to verify it works before deploying

## Other Deployment Considerations

1. **WhatsApp API credentials** are already correctly configured in your app.yaml

2. **Scale your MongoDB** as needed based on your user load

3. **Consider setting up a backup strategy** for your MongoDB data 