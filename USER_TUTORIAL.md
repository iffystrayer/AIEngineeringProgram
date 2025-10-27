# U-AIP Scoping Assistant - User Tutorial

**Quick Start Guide for End Users**

This tutorial will guide you through using the U-AIP Scoping Assistant to scope your enterprise AI project in 5 structured stages.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [User Registration](#user-registration)
3. [Creating a Session](#creating-a-session)
4. [Understanding the 5 Stages](#understanding-the-5-stages)
5. [API Usage Examples](#api-usage-examples)
6. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Getting Started

### Prerequisites
- An internet connection
- API access credentials (username/password or registration)
- A JSON client like Postman, curl, or integrated API client

### Base URL
```
http://localhost:38937/api/v1
```

### API Documentation
- **Swagger UI:** http://localhost:38937/docs
- **ReDoc:** http://localhost:38937/redoc

---

## User Registration

### Step 1: Register a New Account

**Endpoint:** `POST /api/v1/auth/register`

**Request:**
```bash
curl -X POST http://localhost:38937/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d {
    "email": "your.email@company.com",
    "password": "SecurePassword123!",
    "name": "Your Full Name"
  }
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "your.email@company.com"
}
```

**What to Do With the Token:**
1. Copy the `access_token` value
2. Save it securely (don't share with others)
3. Use it in the `Authorization` header for authenticated requests

### Step 2: Understanding Your Token

Your JWT token contains:
- **access_token:** The actual token to use for authentication
- **token_type:** Always "bearer" (used in Authorization header)
- **expires_in:** Seconds until token expires (86400 = 24 hours)
- **user_id:** Your unique identifier
- **email:** Your registered email

**Token Expiration:**
- Tokens expire after 24 hours
- After expiration, you'll need to log in again
- Login returns a new token each time

---

## User Login

### Step 3: Login to Get a Token

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```bash
curl -X POST http://localhost:38937/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d {
    "email": "your.email@company.com",
    "password": "SecurePassword123!"
  }
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "your.email@company.com"
}
```

**How to Use the Token:**
```bash
curl -X GET http://localhost:38937/api/v1/sessions \
  -H "Authorization: bearer <your_access_token>"
```

---

## Creating a Session

### Step 4: Create Your First Session

**Endpoint:** `POST /api/v1/sessions`

**What is a Session?**
A session is your workspace for scoping an AI project. Each session guides you through 5 stages:
1. Business Translation
2. Value Quantification
3. Data Feasibility
4. User Centricity
5. Ethics & Risk Assessment

**Request:**
```bash
curl -X POST http://localhost:38937/api/v1/sessions \
  -H "Authorization: bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d {
    "user_id": "<your_user_id>",
    "project_name": "Customer Churn Prediction AI"
  }
```

**Response:**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "user_id": "<your_user_id>",
  "project_name": "Customer Churn Prediction AI",
  "current_stage": 1,
  "status": "in_progress",
  "started_at": "2025-10-26T20:27:47.600692",
  "last_updated_at": "2025-10-26T20:27:47.600694",
  "stage_data": {}
}
```

**Important Fields:**
- **session_id:** Your unique session identifier (save this!)
- **current_stage:** Which stage you're on (1-5)
- **status:** Can be "in_progress", "completed", "paused", or "abandoned"
- **stage_data:** Your responses for each stage (empty at start)

---

## Understanding the 5 Stages

### Stage 1: Business Translation 🎯
**Goal:** Define the business problem and expected outcomes

**Key Questions:**
- What is the business problem you're trying to solve?
- What are your success metrics?
- What's your projected ROI?
- What are the constraints?

**Example Response:**
```json
{
  "problem_statement": "High customer churn is costing us $2M annually",
  "success_metrics": ["Reduce churn by 15%", "Increase customer lifetime value"],
  "expected_roi": "10:1 (for every $1 spent, save $10)",
  "constraints": ["Must comply with GDPR", "Budget limited to $500K"]
}
```

### Stage 2: Value Quantification 💰
**Goal:** Measure the quantifiable benefits of your AI solution

**Key Questions:**
- What is the financial impact?
- How will you measure success?
- What are the implementation costs?
- What's your break-even timeframe?

**Example Response:**
```json
{
  "annual_value": "$2M (from churn reduction)",
  "implementation_cost": "$500K",
  "payback_period": "3 months",
  "confidence_level": "High (based on similar projects)"
}
```

### Stage 3: Data Feasibility 📊
**Goal:** Assess whether you have the data needed

**Key Questions:**
- What data do you need?
- Do you have access to it?
- What's the data quality?
- How much historical data do you have?

**Example Response:**
```json
{
  "required_data": ["Customer transaction history", "Support tickets", "Demographics"],
  "data_availability": "Complete for 5 years",
  "quality_score": 8.5,
  "completeness": "95% (some gaps in older records)"
}
```

### Stage 4: User Centricity 👥
**Goal:** Ensure the solution meets user needs

**Key Questions:**
- Who are the end users?
- How will they interact with the solution?
- What's their feedback?
- Are they prepared for the change?

**Example Response:**
```json
{
  "end_users": ["Customer Success team", "Marketing team", "Support team"],
  "user_readiness": "Moderate (need training)",
  "expected_adoption_rate": "80% within 6 months",
  "change_management_plan": "2-week training program"
}
```

### Stage 5: Ethics & Risk Assessment ⚖️
**Goal:** Identify and mitigate ethical and business risks

**Key Questions:**
- What are the ethical implications?
- What's your bias mitigation strategy?
- What are the regulatory requirements?
- How will you handle edge cases?

**Example Response:**
```json
{
  "ethical_risks": ["Potential discrimination", "Privacy concerns"],
  "mitigation_strategies": ["Regular bias audits", "Opt-out mechanisms"],
  "regulatory_compliance": "GDPR, CCPA compliant",
  "monitoring_plan": "Quarterly audits"
}
```

---

## API Usage Examples

### Complete Workflow Example

```bash
#!/bin/bash

# 1. Register
REGISTER=$(curl -s -X POST http://localhost:38937/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@company.com",
    "password": "SecurePass123!",
    "name": "Alice Johnson"
  }')

TOKEN=$(echo $REGISTER | jq -r '.access_token')
USER_ID=$(echo $REGISTER | jq -r '.user_id')

echo "✅ Registered successfully"
echo "Token: $TOKEN"
echo "User ID: $USER_ID"

# 2. Create a session
SESSION=$(curl -s -X POST http://localhost:38937/api/v1/sessions \
  -H "Authorization: bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d {
    "user_id": "$USER_ID",
    "project_name": "Fraud Detection AI"
  })

SESSION_ID=$(echo $SESSION | jq -r '.session_id')
echo "✅ Created session: $SESSION_ID"

# 3. List your sessions
curl -s -X GET "http://localhost:38937/api/v1/sessions?user_id=$USER_ID" \
  -H "Authorization: bearer $TOKEN" | jq

# 4. Get session details
curl -s -X GET http://localhost:38937/api/v1/sessions/$SESSION_ID \
  -H "Authorization: bearer $TOKEN" | jq
```

### Using Postman

1. **Create an Environment:**
   - `base_url`: http://localhost:38937/api/v1
   - `token`: (leave empty, will be filled)
   - `user_id`: (leave empty, will be filled)

2. **Register Request:**
   - Method: POST
   - URL: `{{base_url}}/auth/register`
   - Body (JSON):
     ```json
     {
       "email": "your@email.com",
       "password": "SecurePass123!",
       "name": "Your Name"
     }
     ```
   - In Tests tab:
     ```javascript
     pm.environment.set("token", pm.response.json().access_token);
     pm.environment.set("user_id", pm.response.json().user_id);
     ```

3. **Create Session Request:**
   - Method: POST
   - URL: `{{base_url}}/sessions`
   - Headers: `Authorization: bearer {{token}}`
   - Body (JSON):
     ```json
     {
       "user_id": "{{user_id}}",
       "project_name": "My AI Project"
     }
     ```

---

## FAQ & Troubleshooting

### Q: How long does my token last?
**A:** 24 hours. After that, you need to log in again. You'll get a new token each login.

### Q: Can I use the same email to register twice?
**A:** No, email must be unique. You'll get a 409 Conflict error. Use the login endpoint instead.

### Q: What if I forget my password?
**A:** Currently, there's no password reset feature. You'll need to contact support to reset it manually.

### Q: Can I delete a session?
**A:** Yes, but currently only admins can do this. Contact support if you need a session deleted.

### Q: How many sessions can I create?
**A:** Unlimited. Rate limiting applies to API calls (100/hour per user), not session count.

### Q: Can I export my session?
**A:** Yes, after completing all 5 stages, you'll receive an AI Project Charter in multiple formats.

### Q: What happens if my token expires mid-session?
**A:** Your session is saved. Log in again to continue. Your data is not lost.

### Q: Can multiple people work on the same session?
**A:** Currently, each session belongs to one user. For team collaboration, each person creates their own session.

### Q: Is my data encrypted?
**A:** Yes, all data is stored securely in PostgreSQL. Session data can optionally be encrypted at rest (feature in development).

### Q: How do I report a bug?
**A:** Create an issue on GitHub or contact support with:
  - Error message
  - Steps to reproduce
  - Your session ID
  - Timestamp of the error

### Q: What's the rate limit?
**A:** 100 requests per hour per user. If exceeded, you'll get a 429 error. Wait 1 hour to reset.

---

## Best Practices

### 1. Save Your Credentials
```bash
# Create a .env file (DO NOT commit to Git)
USER_EMAIL="your@email.com"
USER_PASSWORD="SecurePassword123!"
API_TOKEN="your_jwt_token_here"
```

### 2. Use Environment Variables
```bash
export API_BASE_URL="http://localhost:38937/api/v1"
export API_TOKEN="your_token"

# Then use in curl
curl -X GET $API_BASE_URL/sessions \
  -H "Authorization: bearer $API_TOKEN"
```

### 3. Keep Detailed Notes
As you go through each stage, keep notes of:
- Key decisions made
- Stakeholder feedback
- Metrics and data sources
- Risk mitigation strategies

### 4. Review Before Completing
Before marking a stage complete:
- Verify all information is accurate
- Get stakeholder approval
- Ensure data is backed up
- Review compliance requirements

### 5. Plan for the Next Stage
At the end of each stage:
- Review what you learned
- Plan any additional research needed
- Adjust estimates and timelines
- Prepare for the next stage

---

## Support Contacts

**For API Issues:**
- Check Swagger docs: http://localhost:38937/docs
- Review error messages carefully
- Check DATABASE logs: `docker logs uaip-api`

**For Feature Requests:**
- Create a GitHub issue
- Include use case and expected behavior
- Provide example workflow

**For Bugs:**
- Provide reproducible steps
- Include error message and stacktrace
- Include your session ID
- Include timestamp of error

---

**Last Updated:** October 26, 2025
**Version:** 1.0
**For Questions:** See PROJECT_STATUS.md or contact support
