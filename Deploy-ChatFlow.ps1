# PowerShell script to deploy the updated ChatFlowController and main.py to GCP Cloud Run

# Service configuration
$ServiceName = "aisyncy-service"
$Region = "asia-south1"

Write-Host "Deploying Aisyncy Recharge with ChatFlow to GCP Cloud Run..." -ForegroundColor Yellow

# Verify MongoDB Atlas connection
Write-Host "Verifying MongoDB Atlas connection..." -ForegroundColor Yellow
$MongoConnectionString = (Get-Content -Path "app.yaml" | Select-String -Pattern "MONGO_URI:") -replace "^.*MONGO_URI:\s+""(.+?)"".*$", '$1'

if ($MongoConnectionString -match "mongodb\+srv://username:password@") {
    Write-Host "WARNING: You haven't updated the MongoDB Atlas connection string in app.yaml!" -ForegroundColor Red
    Write-Host "Please follow the instructions in MONGODB_SETUP.md to set up MongoDB Atlas." -ForegroundColor Red
    $Continue = Read-Host "Do you want to continue anyway? (y/n)"
    if ($Continue -ne "y") {
        Write-Host "Deployment canceled." -ForegroundColor Red
        exit 1
    }
}

# Test MongoDB connection
Write-Host "Testing MongoDB connection..." -ForegroundColor Yellow
try {
    python test_mongo_connection.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "MongoDB connection test failed!" -ForegroundColor Red
        $Continue = Read-Host "MongoDB connection test failed. Do you want to continue anyway? (y/n)"
        if ($Continue -ne "y") {
            Write-Host "Deployment canceled." -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "MongoDB connection test failed! Error: $_" -ForegroundColor Red
    $Continue = Read-Host "MongoDB connection test failed. Do you want to continue anyway? (y/n)"
    if ($Continue -ne "y") {
        Write-Host "Deployment canceled." -ForegroundColor Red
        exit 1
    }
}

# Check if Git is available
try {
    $gitVersion = git --version
    Write-Host "Git detected: $gitVersion"
    
    # Check if this is a git repository
    if (Test-Path -Path ".git") {
        Write-Host "Committing changes to git for tracking..." -ForegroundColor Yellow
        git add config.py main.py src/chatflow/ChatFlowController_new.py app.yaml
        git commit -m "Update WhatsApp integration with ChatFlowController and MongoDB Atlas"
    }
} catch {
    Write-Host "Git not available, skipping source control operations." -ForegroundColor Yellow
}

# Deploy to GCP App Engine
Write-Host "Deploying to App Engine..." -ForegroundColor Yellow
gcloud app deploy app.yaml --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    # Get the service URL
    $ServiceUrl = gcloud app browse --no-launch-browser
    
    Write-Host "Service URL: $ServiceUrl" -ForegroundColor Green
    Write-Host "Testing the webhook..." -ForegroundColor Yellow
    
    # Test the webhook
    try {
        $WebhookTest = Invoke-RestMethod -Uri "$ServiceUrl/webhook_test" -Method Get
        $WebhookTest | ConvertTo-Json -Depth 5
    } catch {
        Write-Host "Warning: Could not test webhook. Error: $_" -ForegroundColor Yellow
    }
    
    Write-Host "Showing logs..." -ForegroundColor Yellow
    gcloud app logs tail --limit=20
    
    Write-Host "Deployment and testing complete!" -ForegroundColor Green
    Write-Host "Important: Send a test message 'hi' to your WhatsApp Business number to verify the chatflow integration." -ForegroundColor Yellow
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
} 