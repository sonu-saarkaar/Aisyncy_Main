# PowerShell script to test the WhatsApp API connection

# WhatsApp API credentials
$WhatsAppPhoneNumberId = "104612292631543"
$WhatsAppAccessToken = "EAAwFo4oYpGgBO8ZAgKQxZB7dxQY8XnArrLxRsvuhZARG8NJVwQPiJ15EuJq30fV1x4eohl7zT4tHwegGaBcpqtVZADA8QOLKgJwL92etZC7HbZCeujbtr01yxcbFiZBFMUtfPr8RtriO8ZCxXCSWUvMxOynVhmy4ZBHtUzcbTGzLxPUdnIJMeyolNKjcpD376l1WZAJQZDZD"
$WhatsAppApiUrl = "https://graph.facebook.com/v17.0/$WhatsAppPhoneNumberId/messages"

# Get the recipient number
$phoneNumber = Read-Host -Prompt "Enter the phone number to send a test message to (with country code, e.g., 919708299494)"

# Format phone number - remove non-digit characters
$phoneNumber = $phoneNumber -replace '\D', ''

# Add country code if not present (assuming India)
if (-not $phoneNumber.StartsWith('91')) {
    $phoneNumber = "91$phoneNumber"
}

# Create the message payload
$messagePayload = @{
    messaging_product = "whatsapp"
    recipient_type = "individual"
    to = $phoneNumber
    type = "text"
    text = @{
        body = "This is a test message from the Aisyncy Recharge chatflow integration test script. The time is $(Get-Date)."
    }
} | ConvertTo-Json

# Create the headers
$headers = @{
    "Authorization" = "Bearer $WhatsAppAccessToken"
    "Content-Type" = "application/json"
}

Write-Host "Sending test message to $phoneNumber..." -ForegroundColor Yellow
Write-Host "API URL: $WhatsAppApiUrl" -ForegroundColor Yellow
Write-Host "Request payload:" -ForegroundColor Yellow
$messagePayload

try {
    # Send the request
    $response = Invoke-RestMethod -Uri $WhatsAppApiUrl -Method Post -Headers $headers -Body $messagePayload
    
    Write-Host "✅ Message sent successfully!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
    
    # Get the message ID if available
    if ($response.messages -and $response.messages.Count -gt 0) {
        $messageId = $response.messages[0].id
        Write-Host "Message ID: $messageId" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to send message!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    
    # Get more details about the error
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status code: $statusCode" -ForegroundColor Red
        
        try {
            $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "Error details:" -ForegroundColor Red
            $errorDetails | ConvertTo-Json -Depth 5
        } catch {
            Write-Host "Could not parse error details: $_" -ForegroundColor Red
        }
    }
}

Write-Host "`nTest complete. If the message was sent successfully, you should receive it on your WhatsApp within a few seconds." -ForegroundColor Yellow
Write-Host "Note: To verify that the chatflow is working, send a message like 'hi' to your WhatsApp Business number." -ForegroundColor Yellow 