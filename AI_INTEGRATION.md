# ChatGPT Integration for Aisyncy Recharge

This document explains how the ChatGPT API has been integrated into the Aisyncy Recharge WhatsApp bot to enhance user interactions.

## Features

The ChatGPT integration provides the following enhanced capabilities:

1. **Natural Language Understanding**: Improved interpretation of user messages
2. **Intent Classification**: Automatically classify user messages to route to appropriate handlers
3. **Enhanced Responses**: Make standard responses more personalized and helpful
4. **Customer Support**: Advanced handling of customer issues and complaints
5. **General Queries**: Direct answers to questions not covered by standard flows
6. **Chat with Aisyncy**: Dedicated AI chat mode for open-ended conversations about recharge services

## Setup

### 1. Get an API Key

1. Sign up for an account at [OpenAI](https://platform.openai.com/)
2. Navigate to API Keys section
3. Create a new API key with appropriate permissions
4. Copy the key for configuration

### 2. Configure the API Key

Update your `app.yaml` file with the OpenAI API key:

```yaml
env_variables:
  # Other environment variables
  OPENAI_API_KEY: "your-openai-api-key-here"
  OPENAI_MODEL: "gpt-3.5-turbo"  # or "gpt-4" for more advanced capabilities
```

### 3. Deploy the Application

Use the provided deployment scripts (`Deploy-ChatFlow.ps1` or `deploy.sh`) to deploy your application with ChatGPT integration.

## How It Works

The integration has several components:

### 1. OpenAI Helper

Located at `src/ai/openai_helper.py`, this module:
- Manages communication with the OpenAI API
- Formats prompts for different purposes
- Handles error conditions gracefully

### 2. Conversation Store

Located at `src/ai/conversation_store.py`, this module:
- Stores user conversation history
- Provides context for AI responses
- Manages memory usage by limiting history length

### 3. ChatFlow Controller Integration

The main `RechargeController` class has been enhanced with:
- AI-based intent classification for new messages
- Response enhancement using OpenAI
- Special handlers for complex queries

## Features in Detail

### Chat with Aisyncy

The "Chat with Aisyncy" feature provides a dedicated conversational interface where users can:
- Ask any question about Aisyncy Recharge services
- Get help with troubleshooting issues
- Learn how to perform recharges
- Get information about plans and offers
- Ask for assistance with any aspect of the service

This feature is accessible from:
1. The main welcome screen (via "Chat with Aisyncy" button)
2. The Explore Aisyncy screen (via "Chat with Aisyncy" button)

During an AI chat session:
- The system maintains conversation history for context
- User-specific information is incorporated when available
- Users can return to the main menu at any time by clicking the "Main Menu" button
- Users can directly start a recharge by clicking the "Recharge Now" button

### Intent Classification

When a user sends a message, the system tries to classify it into one of these categories:
- `recharge`: Related to making a mobile recharge
- `plan_inquiry`: Questions about recharge plans
- `payment`: Payment-related questions
- `complaint`: Issues or complaints
- `greeting`: Simple greetings
- `general_query`: Other general questions

Based on this classification, the message is routed to appropriate handlers.

### Response Enhancement

For text-based responses, the system can enhance standard responses to make them:
- More personalized
- More helpful
- More natural sounding

This is especially useful for error messages and informational responses.

### Conversation History

The system maintains a history of conversations with users, which:
- Provides context for responses
- Improves response relevance
- Enables more natural conversation flow

## Examples

### Example 1: General Query

**User**: "What types of payment methods do you accept?"

**Without AI**: Standard welcome message or error

**With AI**: "At Aisyncy Recharge, we accept various payment methods including UPI, QR code payments, and credit/debit cards. You can select your preferred payment method during the recharge process."

### Example 2: Enhanced Standard Response

**User**: "My recharge failed"

**Without AI**: "Please raise a complaint through the menu"

**With AI**: "I'm sorry to hear that your recharge failed. You can raise a formal complaint by selecting 'Raise Complaint' from the menu, or provide details of the issue here and I'll help you resolve it. Please include your transaction ID if available."

## Monitoring and Maintenance

### 1. Monitor API Usage

Keep track of your OpenAI API usage to manage costs. The OpenAI dashboard provides usage statistics.

### 2. Review Response Quality

Periodically review AI-generated responses to ensure they maintain quality and accuracy.

### 3. Update the Model

Consider updating to newer models as they become available for improved capabilities.

## Troubleshooting

If the ChatGPT integration isn't working:

1. Check that the API key is correctly configured in `app.yaml`
2. Verify the OpenAI API is operational
3. Check application logs for errors related to OpenAI API calls
4. Ensure the application has internet access to reach the OpenAI API

## Customization

You can customize the AI behavior by modifying the system prompts in `openai_helper.py`. The primary prompts are:

1. The main system message that defines the assistant's persona
2. The enhancement prompt that guides response improvement
3. The classification prompt that determines user intent

Adjust these prompts to get different responses based on your business needs. 