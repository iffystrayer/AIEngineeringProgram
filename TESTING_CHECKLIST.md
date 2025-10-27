# U-AIP Scoping Assistant - Manual Testing Checklist

**Date:** October 27, 2025
**Status:** Ready for Manual Testing
**System Status:** All components operational and healthy

---

## 🚀 Quick Start - Verify System is Running

```bash
# Check API health
curl http://localhost:38937/api/v1/health | jq .

# View API documentation
open http://localhost:38937/docs
# or
open http://localhost:38937/redoc
```

**Expected Result:** API responds with `"status": "healthy"` and all components healthy

---

## 📋 Testing Workflow

Follow this checklist to test the complete user experience end-to-end:

### Phase 1: User Registration & Authentication ✅

- [ ] **Test 1.1: Register a new user**
  ```bash
  curl -X POST http://localhost:38937/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{
      "email": "testuser@example.com",
      "password": "SecurePass123!",
      "name": "Test User"
    }' | jq .
  ```
  **Expected:** Returns 201 with `access_token`, `user_id`, and `expires_in: 86400`
  **Save:** Copy the `access_token` and `user_id` for next tests

- [ ] **Test 1.2: Attempt duplicate registration**
  ```bash
  curl -X POST http://localhost:38937/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{
      "email": "testuser@example.com",
      "password": "DifferentPass456!",
      "name": "Duplicate User"
    }' | jq .
  ```
  **Expected:** Returns 409 Conflict error

- [ ] **Test 1.3: Login with valid credentials**
  ```bash
  curl -X POST http://localhost:38937/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{
      "email": "testuser@example.com",
      "password": "SecurePass123!"
    }' | jq .
  ```
  **Expected:** Returns 200 with new `access_token`

- [ ] **Test 1.4: Login with wrong password**
  ```bash
  curl -X POST http://localhost:38937/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{
      "email": "testuser@example.com",
      "password": "WrongPassword"
    }' | jq .
  ```
  **Expected:** Returns 401 Unauthorized

---

### Phase 2: Session Management 🎯

- [ ] **Test 2.1: Create a new session**
  ```bash
  TOKEN="your_access_token_here"
  USER_ID="your_user_id_here"

  curl -X POST http://localhost:38937/api/v1/sessions \
    -H "Authorization: bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": "'$USER_ID'",
      "project_name": "Customer Churn Prediction"
    }' | jq .
  ```
  **Expected:** Returns 201 with `session_id`, `current_stage: 1`, `status: "in_progress"`
  **Save:** Copy the `session_id` for next tests

- [ ] **Test 2.2: Retrieve session by ID**
  ```bash
  TOKEN="your_access_token_here"
  SESSION_ID="your_session_id_here"

  curl -X GET http://localhost:38937/api/v1/sessions/$SESSION_ID \
    -H "Authorization: bearer $TOKEN" | jq .
  ```
  **Expected:** Returns 200 with complete session details including `stage_data` object

- [ ] **Test 2.3: List user sessions**
  ```bash
  TOKEN="your_access_token_here"
  USER_ID="your_user_id_here"

  curl -X GET "http://localhost:38937/api/v1/sessions?user_id=$USER_ID" \
    -H "Authorization: bearer $TOKEN" | jq .
  ```
  **Expected:** Returns 200 with array of sessions (at least the one just created)

- [ ] **Test 2.4: Create a second session**
  ```bash
  TOKEN="your_access_token_here"
  USER_ID="your_user_id_here"

  curl -X POST http://localhost:38937/api/v1/sessions \
    -H "Authorization: bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": "'$USER_ID'",
      "project_name": "Fraud Detection AI"
    }' | jq .
  ```
  **Expected:** Returns 201 with different `session_id`

- [ ] **Test 2.5: Verify sessions list now shows both**
  ```bash
  TOKEN="your_access_token_here"
  USER_ID="your_user_id_here"

  curl -X GET "http://localhost:38937/api/v1/sessions?user_id=$USER_ID" \
    -H "Authorization: bearer $TOKEN" | jq .
  ```
  **Expected:** Returns 200 with array containing both sessions

---

### Phase 3: Rate Limiting 🚦

- [ ] **Test 3.1: Verify rate limiting is active**
  ```bash
  TOKEN="your_access_token_here"

  # Make 101 requests quickly (should trigger rate limit on 101st)
  for i in {1..101}; do
    curl -X GET http://localhost:38937/api/v1/health \
      -H "Authorization: bearer $TOKEN" -s -o /dev/null -w "%{http_code}\n"
  done
  ```
  **Expected:** First 100 return 200, 101st returns 429 (Too Many Requests)

- [ ] **Test 3.2: Verify error message for rate limit**
  ```bash
  TOKEN="your_access_token_here"

  # After hitting rate limit
  curl -X GET http://localhost:38937/api/v1/health \
    -H "Authorization: bearer $TOKEN" | jq .
  ```
  **Expected:** Returns 429 with error message about rate limit

---

### Phase 4: Data Persistence 💾

- [ ] **Test 4.1: Verify session persists after retrieval**
  - Create a session (Test 2.1)
  - Retrieve it multiple times (Test 2.2)
  - Each retrieval should return identical data
  **Expected:** All retrievals return same `session_id`, `project_name`, `created_at`

- [ ] **Test 4.2: Verify user sessions are isolated**
  - Register second user
  - Create sessions for second user
  - Use first user's token to list sessions
  **Expected:** First user only sees their own sessions

---

### Phase 5: Error Handling ⚠️

- [ ] **Test 5.1: Missing authentication token**
  ```bash
  curl -X GET http://localhost:38937/api/v1/sessions \
    -H "Content-Type: application/json" | jq .
  ```
  **Expected:** Returns 403 Forbidden

- [ ] **Test 5.2: Invalid authentication token**
  ```bash
  curl -X GET http://localhost:38937/api/v1/sessions \
    -H "Authorization: bearer invalid_token_xyz" | jq .
  ```
  **Expected:** Returns 401 Unauthorized

- [ ] **Test 5.3: Non-existent session**
  ```bash
  TOKEN="your_access_token_here"

  curl -X GET http://localhost:38937/api/v1/sessions/00000000-0000-0000-0000-000000000000 \
    -H "Authorization: bearer $TOKEN" | jq .
  ```
  **Expected:** Returns 404 Not Found

- [ ] **Test 5.4: Invalid request data**
  ```bash
  TOKEN="your_access_token_here"

  curl -X POST http://localhost:38937/api/v1/sessions \
    -H "Authorization: bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "project_name": "Missing user_id"
    }' | jq .
  ```
  **Expected:** Returns 422 Unprocessable Entity with validation errors

---

## 📊 Verification Checklist

After completing all tests above, verify:

- [ ] **All 200 status codes returned for valid requests**
- [ ] **Appropriate error codes (4xx/5xx) for invalid requests**
- [ ] **Sessions persist across multiple API calls**
- [ ] **User isolation working (can't see other users' sessions)**
- [ ] **Rate limiting properly enforced (100/hour per user)**
- [ ] **Authentication tokens working correctly**
- [ ] **No unhandled exceptions in API logs**

---

## 🔍 Viewing Logs

```bash
# View API logs
docker logs uaip-api -f

# View database logs
docker logs uaip-db -f

# View specific error
docker logs uaip-api --tail 50
```

---

## 🛠️ Troubleshooting

### Issue: Connection refused to localhost:38937
- **Check:** `docker-compose ps` - verify uaip-api is running and healthy
- **Fix:** `docker-compose restart uaip-api`

### Issue: Database connection error
- **Check:** `docker logs uaip-db` for connection errors
- **Fix:** `docker-compose restart uaip-db`

### Issue: 401/403 errors on authenticated endpoints
- **Check:** Token is properly copied from registration/login response
- **Fix:** Re-run registration test and copy new token

### Issue: Sessions not persisting
- **Check:** `docker exec uaip-db psql -U uaip_user -d uaip_scoping -c "\dt"`
- **Verify:** `sessions` table exists

---

## 📝 Test Results Template

After completing tests, document results:

```markdown
## Test Results - [Date]

### Phase 1: Authentication
- Registration: ✅ / ❌
- Login: ✅ / ❌
- Token validation: ✅ / ❌

### Phase 2: Sessions
- Create session: ✅ / ❌
- Retrieve session: ✅ / ❌
- List sessions: ✅ / ❌
- Session persistence: ✅ / ❌

### Phase 3: Rate Limiting
- Rate limit enforcement: ✅ / ❌
- Per-user limits: ✅ / ❌

### Phase 4: Error Handling
- Authentication errors: ✅ / ❌
- Validation errors: ✅ / ❌
- Not found errors: ✅ / ❌

### Overall Assessment
[PASS / FAIL / PARTIAL]

### Issues Found
[List any issues, errors, or unexpected behaviors]
```

---

## 🚀 Next Steps After Testing

Once manual testing is complete:

1. **Document results** - Use the template above
2. **Report any issues** - List bugs or unexpected behaviors
3. **Request fixes** - Specify which tests failed
4. **Proceed with next phase** - Frontend integration (P2E) or enable encryption

---

**Last Updated:** October 27, 2025
**System Status:** ✅ Ready for testing
**Documentation:** See USER_TUTORIAL.md for detailed API examples
