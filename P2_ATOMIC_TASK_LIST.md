# P2: PRODUCTION FOUNDATION - ATOMIC TASK LIST

**Phase:** P2 - Security, Reliability & Integration
**Start Date:** October 24, 2025
**Target Completion:** November 7, 2025 (2 weeks)
**Duration Estimate:** 12-15 days of focused work

---

## 📊 CURRENT STATE (P1 Verified)

### ✅ P1 COMPLETION STATUS
- **Backend API:** Running on port 38937, all endpoints responding
- **Database:** PostgreSQL 16 healthy, 49 sessions persisted
- **Migrations:** Alembic configured, initial migration applied
- **Test Infrastructure:** 795 tests available, 75.3% pass rate documented
- **Documentation:** README updated with honest status

### ⚠️ KNOWN ISSUES FROM P1.5
1. **Session Retrieval Bug (CRITICAL)**
   - Sessions created successfully (POST /api/v1/sessions works)
   - Sessions persisted in database (verified in PostgreSQL)
   - Session GET returns 404 even though DB records exist
   - Session list returns empty array despite 49 records in DB
   - Root cause: Orchestrator.get_session() or SessionRepository.get_session()

2. **Frontend Integration Unverified**
   - Frontend code exists but dependency installation incomplete
   - API endpoint URLs hardcoded, not environment-driven
   - No live testing with backend

3. **No REST API Schema Documentation**
   - OpenAPI/Swagger docs endpoint needs verification
   - API client in frontend references unstable endpoints

---

## 🎯 P2 PHASE GOALS

### Primary Objectives
1. **Fix Critical Session CRUD Bug** - Get session retrieval working
2. **Implement Authentication** - Multi-user support, security baseline
3. **Establish CI/CD Pipeline** - Automated testing and deployment
4. **Harden LLM Integration** - Retry logic, error handling, cost tracking
5. **Verify Frontend Integration** - Full stack end-to-end test

### Success Criteria
- All session CRUD operations work (create, read, list, delete)
- Users can authenticate and only see their own sessions
- GitHub Actions CI runs tests on every commit
- LLM provider failures don't crash stages
- Frontend connects to backend and displays real data

---

## 📋 ATOMIC TASK BREAKDOWN

### PHASE 2A: CRITICAL BUG FIXES (Days 1-2)

#### P2A.1: Debug & Fix Session Retrieval Bug
**Priority:** CRITICAL
**Status:** NOT STARTED
**Effort:** 3-4 hours
**Risk:** HIGH (blocks integration testing)

**Description:**
Sessions are created and persisted in PostgreSQL but cannot be retrieved via API. The response returns 404 or empty list despite verified DB records.

**Root Cause Analysis:**
- API creation endpoint works correctly (session saved to DB)
- SessionRepository.list_sessions() returns empty
- SessionRepository.get_session(session_id) returns None
- Database query layer may be filtering or missing results

**Tasks:**

1. **Verify API Health & Database Connection**
   ```bash
   # Check API is running
   curl http://localhost:38937/api/v1/health

   # Count database sessions
   psql -h localhost -p 15432 -U uaip_user -d uaip_scoping \
     -c "SELECT COUNT(*) FROM sessions;"
   ```
   - [ ] API responds with healthy status
   - [ ] Database connection shows active sessions count

2. **Test Session Repository Directly**
   - [ ] Create test script to instantiate SessionRepository
   - [ ] Call get_session() with known session UUID
   - [ ] Call list_sessions() and check return value
   - [ ] Add logging to repository methods
   - [ ] Verify database connection pool is healthy

3. **Debug Orchestrator Session Management**
   - [ ] Check if Orchestrator is caching sessions in memory
   - [ ] Verify Orchestrator.get_session() delegates to repository
   - [ ] Check for session filtering logic that might hide results
   - [ ] Trace through session creation → storage → retrieval flow

4. **Examine Database Query Execution**
   - [ ] Log all SQL queries from asyncpg
   - [ ] Run equivalent SQL directly in psql
   - [ ] Compare query results between API and direct DB
   - [ ] Check for missing JSONB column access if applicable

5. **Fix & Verify**
   - [ ] Identify root cause
   - [ ] Implement fix in SessionRepository or Orchestrator
   - [ ] Write integration test to verify fix
   - [ ] Test with multiple sessions
   - [ ] Verify API list endpoint returns all sessions

**Testing:**
```bash
# Create session
SESSION_ID=$(curl -s -X POST http://localhost:38937/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","project_name":"Test","description":"Test"}' \
  | jq -r '.session_id')

# Verify in database
psql -h localhost -p 15432 -U uaip_user -d uaip_scoping \
  -c "SELECT session_id, project_name FROM sessions WHERE session_id='$SESSION_ID';"

# Retrieve via API (should not fail)
curl http://localhost:38937/api/v1/sessions/$SESSION_ID
```

---

#### P2A.2: Fix Session List Filtering
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 1-2 hours
**Dependency:** P2A.1

**Description:**
Session list endpoint returns empty despite database records. May be related to user_id filtering or pagination.

**Tasks:**
- [ ] Check SessionRepository.list_sessions() filter logic
- [ ] Verify pagination parameters (skip/limit)
- [ ] Test without filters (should return all sessions)
- [ ] Verify user_id filter if implemented
- [ ] Add tests for edge cases (empty database, single session, many sessions)

---

### PHASE 2B: AUTHENTICATION & SECURITY (Days 3-4)

#### P2B.1: Implement JWT Authentication
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 4-6 hours
**Dependency:** None (parallel with P2A)

**Description:**
Add JWT-based authentication to secure API endpoints. Users must authenticate to create/access sessions.

**Architecture:**
```
1. Registration endpoint: POST /api/v1/auth/register
   - Input: email, password, name
   - Output: user_id, token
   - Store: users table (hashed password)

2. Login endpoint: POST /api/v1/auth/login
   - Input: email, password
   - Output: user_id, token, expires_in
   - Implement: Password hash comparison

3. JWT validation middleware
   - Verify token on protected endpoints
   - Extract user_id from token
   - Return 401 if invalid/expired

4. User isolation
   - All endpoints require auth
   - Sessions filtered by user_id
   - Users can only access their own sessions
```

**Database Schema:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add user_id FK to sessions (if not exists)
-- ALTER TABLE sessions ADD COLUMN user_id UUID REFERENCES users(user_id);
-- ALTER TABLE sessions ADD UNIQUE (user_id, session_id);
```

**Tasks:**

1. **Setup JWT Dependencies**
   - [ ] Install: `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`
   - [ ] Update pyproject.toml
   - [ ] Update uv.lock

2. **Create Authentication Models**
   - [ ] Pydantic models: UserRegister, UserLogin, TokenResponse, UserResponse
   - [ ] Database model: User with email, password_hash, name
   - [ ] Alembic migration for users table

3. **Implement Auth Endpoints**
   - [ ] POST /api/v1/auth/register
     - Validate email format
     - Hash password with bcrypt
     - Create user in DB
     - Return JWT token
   - [ ] POST /api/v1/auth/login
     - Find user by email
     - Verify password hash
     - Generate JWT token
     - Return token with expiry

4. **Create JWT Middleware**
   - [ ] Extract token from Authorization header
   - [ ] Verify JWT signature
   - [ ] Extract claims (user_id, exp)
   - [ ] Return 401 if invalid/expired
   - [ ] Inject user_id into request context

5. **Protect Endpoints**
   - [ ] Add `Depends(get_current_user)` to session endpoints
   - [ ] Filter sessions by user_id in list/get operations
   - [ ] Add user_id to session creation payload
   - [ ] Verify user owns session before allowing updates

6. **Test Authentication Flow**
   - [ ] Register new user
   - [ ] Login returns token
   - [ ] Token grants access to session endpoints
   - [ ] Invalid token returns 401
   - [ ] Expired token returns 401
   - [ ] Users can't access other users' sessions

**Testing:**
```bash
# Register
TOKEN=$(curl -s -X POST http://localhost:38937/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test"}' \
  | jq -r '.token')

# Create session with auth
curl -s -X POST http://localhost:38937/api/v1/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_name":"My Project"}'

# List sessions (should show only user's sessions)
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:38937/api/v1/sessions
```

---

#### P2B.2: Add Rate Limiting
**Priority:** MEDIUM
**Status:** NOT STARTED
**Effort:** 2-3 hours
**Dependency:** P2B.1

**Description:**
Implement per-user rate limiting to prevent abuse and control LLM API costs.

**Strategy:**
- **Per-User Limits:** 100 requests per hour per authenticated user
- **Global Limits:** 10,000 requests per hour per API
- **Stage Execution Limits:** 1 concurrent stage per user (prevent hammering LLM)
- **Response:** 429 Too Many Requests with Retry-After header

**Tools:** slowapi (FastAPI rate limiter)

**Tasks:**
- [ ] Install slowapi: `uv pip install slowapi`
- [ ] Create rate limit key function (user_id)
- [ ] Apply decorators to endpoints:
  ```python
  @limiter.limit("100/hour")
  def create_session(...)
  ```
- [ ] Test with concurrent requests
- [ ] Verify Retry-After header included in 429 response

---

### PHASE 2C: CI/CD PIPELINE (Days 5-6)

#### P2C.1: Setup GitHub Actions Workflows
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 4-5 hours
**Dependency:** P2A (tests must pass)

**Description:**
Automate testing, linting, security scanning, and builds on every commit.

**Workflows to Create:**

1. **test.yml - Run on every push & PR**
   ```yaml
   name: Test Suite
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         - name: Install uv
           run: curl -LsSf https://astral.sh/uv/install.sh | sh
         - name: Install dependencies
           run: uv pip install -e ".[dev]"
         - name: Run tests
           run: uv run pytest tests/ -v --cov
         - name: Lint with ruff
           run: uv run ruff check src/ tests/
         - name: Type check with mypy
           run: uv run mypy src/
   ```

2. **security.yml - Dependency scanning**
   ```yaml
   name: Security Scan
   on: [push]
   jobs:
     security:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         - name: Install uv
           run: curl -LsSf https://astral.sh/uv/install.sh | sh
         - name: Check dependencies with pip-audit
           run: uv run pip-audit
   ```

3. **build.yml - Docker image build (on main branch)**
   ```yaml
   name: Build & Push
   on:
     push:
       branches: [main]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: docker/setup-buildx-action@v2
         - name: Build Docker image
           run: docker build -t uaip:${{ github.sha }} .
   ```

**Tasks:**
- [ ] Create `.github/workflows/` directory
- [ ] Create test.yml workflow
  - Verify pytest works in CI
  - Check mypy runs successfully
  - Ensure ruff linting passes
- [ ] Create security.yml workflow
  - Add dependency scanning
  - Set up to fail on vulnerabilities
- [ ] Create build.yml workflow
  - Build Docker image
  - Tag with commit SHA
- [ ] Configure branch protection
  - Require tests to pass before merge
  - Require all status checks to pass
- [ ] Add status badges to README
  - ![Tests](https://github.com/.../workflows/Test%20Suite/badge.svg)
  - ![Security](https://github.com/.../workflows/Security/badge.svg)
- [ ] Test workflows on feature branch
  - Trigger test run
  - Verify all checks pass
  - Verify passing test allows merge

**Acceptance Criteria:**
- [ ] All workflows defined and passing
- [ ] Tests run automatically on push
- [ ] Linting and security checks automated
- [ ] Branch protection enabled
- [ ] Status badges display current state

---

#### P2C.2: Configure Container Registry & Deployment
**Priority:** MEDIUM
**Status:** NOT STARTED
**Effort:** 3-4 hours
**Dependency:** P2C.1

**Description:**
Push Docker images to registry and prepare for automated deployment.

**Strategy:**
1. Use GitHub Container Registry (ghcr.io)
2. Push on successful main branch builds
3. Tag with version and latest
4. Prepare deployment instructions

**Tasks:**
- [ ] Setup GitHub Container Registry credentials
- [ ] Update build workflow to push image:
  ```yaml
  - name: Push to GHCR
    run: |
      echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u $ --password-stdin
      docker tag uaip:latest ghcr.io/${{ github.repository }}:latest
      docker push ghcr.io/${{ github.repository }}:latest
  ```
- [ ] Create docker-compose.prod.yml
- [ ] Document deployment process

---

### PHASE 2D: LLM INTEGRATION HARDENING (Days 7-8)

#### P2D.1: Add Retry Logic & Fallback Chain
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 4-5 hours
**Dependency:** None (can run parallel)

**Description:**
Implement robust error handling for LLM API calls. Transient failures should retry automatically. Permanent failures should fallback to Ollama.

**Current Issues:**
- No retry on API rate limiting (429)
- No timeout handling
- No fallback to alternative provider
- Failures crash stage execution

**Solution Architecture:**
```
Call Chain: Claude (Haiku) → Claude (retry) → Ollama (fallback)

Config:
  - Haiku: max_retries=3, timeout=30s
  - Fallback: Ollama (llama2, faster but lower quality)
  - Backoff: exponential (1s, 2s, 4s, 8s)
```

**Tasks:**

1. **Install Dependencies**
   - [ ] `uv pip install tenacity` (retry library)
   - [ ] `uv pip install pydantic` (already installed)
   - [ ] Update pyproject.toml

2. **Create Retry Wrapper**
   ```python
   from tenacity import (
       retry,
       stop_after_attempt,
       wait_exponential,
       retry_if_exception_type
   )

   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((APIConnectionError, RateLimitError))
   )
   async def call_llm_with_retry(provider, prompt):
       return await provider.generate(prompt)
   ```
   - [ ] Handle RateLimitError (429) - retry
   - [ ] Handle APIConnectionError - retry
   - [ ] Handle ValidationError - don't retry
   - [ ] Handle TokenLimitError - fallback

3. **Implement Fallback Chain**
   ```python
   async def call_llm_with_fallback(prompt, preferred_model="haiku"):
       try:
           return await call_claude_with_retry(prompt, model=preferred_model)
       except PermanentError as e:
           logger.warning(f"Claude failed, using Ollama fallback: {e}")
           return await call_ollama(prompt)
   ```
   - [ ] Try Claude first
   - [ ] Log failures with reason
   - [ ] Fallback to Ollama on PermanentError
   - [ ] Raise if Ollama also fails

4. **Add Timeout Configuration**
   ```python
   TIMEOUTS = {
       "haiku": 30,      # seconds
       "sonnet": 60,
       "ollama": 120     # local, might be slower
   }
   ```
   - [ ] Apply per-provider timeouts
   - [ ] Treat timeout as transient (retry)

5. **Token & Cost Tracking**
   ```python
   class TokenUsage(BaseModel):
       input_tokens: int
       output_tokens: int
       total_tokens: int
       cost_usd: float
       provider: str
       model: str

   async def track_token_usage(response, provider, model):
       usage = response.usage
       cost = (usage.input_tokens * INPUT_RATE +
               usage.output_tokens * OUTPUT_RATE)
       return TokenUsage(
           input_tokens=usage.input_tokens,
           output_tokens=usage.output_tokens,
           total_tokens=usage.input_tokens + usage.output_tokens,
           cost_usd=cost,
           provider=provider,
           model=model
       )
   ```
   - [ ] Extract token counts from response
   - [ ] Calculate cost based on provider rates
   - [ ] Log to database for reporting
   - [ ] Aggregate per session

6. **Health Check for Providers**
   ```python
   async def check_provider_health(provider):
       try:
           result = await provider.generate("Test prompt", timeout=5)
           return True
       except Exception:
           return False
   ```
   - [ ] Check Claude API availability on startup
   - [ ] Check Ollama availability on startup
   - [ ] Fail fast if both unavailable
   - [ ] Add retry loop on startup

7. **Test Resilience**
   - [ ] Simulate API rate limiting (mock 429)
   - [ ] Verify retry happens
   - [ ] Verify fallback to Ollama
   - [ ] Test with multiple concurrent calls
   - [ ] Verify token tracking accuracy

**Testing:**
```python
# Mock rate limit
with patch('anthropic.Anthropic') as mock:
    mock.return_value.generate.side_effect = [
        RateLimitError(),
        RateLimitError(),
        SuccessfulResponse()
    ]
    result = await call_llm_with_retry(prompt)
    assert result == SuccessfulResponse()
    assert mock.call_count == 3
```

---

#### P2D.2: Add Observability for LLM Calls
**Priority:** MEDIUM
**Status:** NOT STARTED
**Effort:** 2-3 hours
**Dependency:** P2D.1

**Description:**
Add structured logging and metrics for all LLM API calls to track performance and costs.

**Logging Format:**
```json
{
  "timestamp": "2025-10-24T12:34:56Z",
  "event": "llm_call",
  "provider": "anthropic",
  "model": "claude-haiku-4.5",
  "session_id": "uuid",
  "stage": 1,
  "prompt_length": 1250,
  "response_tokens": 450,
  "input_tokens": 1250,
  "total_tokens": 1700,
  "cost_usd": 0.00255,
  "latency_ms": 2340,
  "status": "success",
  "retry_count": 0
}
```

**Tasks:**
- [ ] Create LLMCallLogger with structlog
- [ ] Log before call (prompt, model, session_id)
- [ ] Log after call (tokens, cost, latency, status)
- [ ] Add to database for analytics
- [ ] Create queries for cost/token reporting

---

### PHASE 2E: FRONTEND INTEGRATION (Days 9-10)

#### P2E.1: Install & Setup Frontend Dependencies
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 1-2 hours
**Dependency:** None

**Description:**
Install all frontend npm packages and verify dev server starts.

**Tasks:**
- [ ] `cd frontend && npm install`
- [ ] Verify no critical vulnerabilities
- [ ] Check package-lock.json
- [ ] Run `npm run dev` and verify on http://localhost:5173
- [ ] Document environment setup in README

**Acceptance:**
- [ ] npm install completes without errors
- [ ] Frontend dev server runs
- [ ] No console errors in browser

---

#### P2E.2: Configure Frontend API Base URL
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 2-3 hours
**Dependency:** P2E.1

**Description:**
Make API endpoint configurable instead of hardcoded. Support both dev and production URLs.

**Current Issue:**
- Frontend likely has `http://localhost:38937` hardcoded
- Can't work in production
- Need environment-driven configuration

**Strategy:**
```
1. Create .env.example for frontend:
   VITE_API_BASE_URL=http://localhost:38937/api/v1

2. Create frontend/.env.local (not committed):
   VITE_API_BASE_URL=http://localhost:38937/api/v1

3. Update src/services/api.ts:
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

4. Support prod config:
   VITE_API_BASE_URL=https://api.example.com/api/v1
```

**Tasks:**
- [ ] Create frontend/.env.example
- [ ] Create frontend/.env.local (dev only)
- [ ] Update src/services/api.ts to use env var
- [ ] Test with different base URLs
- [ ] Document in QUICK_START.md

---

#### P2E.3: Verify Full Stack End-to-End
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 3-4 hours
**Dependency:** P2E.2, P2B.1 (auth)

**Description:**
Test complete user workflow: register → login → create session → execute stage → view results.

**User Flow:**
1. Register account in frontend
2. Login and receive JWT
3. Create new session via UI
4. Execute stage 1 (answer questions)
5. Proceed to stage 2
6. View generated charter

**Tasks:**

1. **Start Services**
   - [ ] Verify PostgreSQL running: `docker ps | grep postgres`
   - [ ] Verify backend running: `ps aux | grep uvicorn`
   - [ ] Start frontend: `npm run dev`

2. **Test Registration Flow**
   - [ ] Open http://localhost:5173
   - [ ] Click register
   - [ ] Fill form: email, password, name
   - [ ] Submit
   - [ ] Verify token returned and stored in localStorage
   - [ ] Verify redirected to dashboard

3. **Test Session Creation**
   - [ ] Click "New Session"
   - [ ] Fill form: project name, description
   - [ ] Submit
   - [ ] Verify session created in database
   - [ ] Verify session ID displayed in UI
   - [ ] Verify session appears in list

4. **Test Stage Execution**
   - [ ] Click into session
   - [ ] View stage 1 form
   - [ ] Fill in answers for stage 1 questions
   - [ ] Submit
   - [ ] Verify API call succeeds
   - [ ] Verify data persisted in database
   - [ ] Verify UI shows stage 1 complete
   - [ ] Verify able to advance to stage 2

5. **Test Session Listing**
   - [ ] Navigate to dashboard
   - [ ] Verify own sessions displayed
   - [ ] Verify other users' sessions NOT displayed
   - [ ] Verify pagination works

6. **Test Error Scenarios**
   - [ ] Submit with invalid input
   - [ ] Verify validation error displayed
   - [ ] Try to access other user's session
   - [ ] Verify 403 Forbidden or redirected
   - [ ] Disconnect from backend
   - [ ] Verify error message displayed

7. **Document Issues Found**
   - [ ] List any bugs found
   - [ ] Categorize by severity
   - [ ] Create GitHub issues for blockers

---

#### P2E.4: Implement Real-Time Progress Feedback
**Priority:** MEDIUM
**Status:** NOT STARTED
**Effort:** 3-4 hours
**Dependency:** P2E.3

**Description:**
Show real-time progress while stage executes. LLM calls can take 5-10 seconds per stage.

**Solution:**
- Show spinner while waiting for response
- Display "Processing..." with estimated time
- Show token usage after completion
- Display any validation warnings

**Tasks:**
- [ ] Add loading state to stage execution
- [ ] Show spinner with elapsed time
- [ ] Display estimated remaining time
- [ ] Show cost/tokens after execution
- [ ] Test with slow network (DevTools throttling)

---

### PHASE 2F: ORCHESTRATOR REFACTORING (Days 11-13)

#### P2F.1: Extract SessionManager from Orchestrator
**Priority:** MEDIUM
**Status:** NOT STARTED
**Effort:** 3-4 hours
**Dependency:** P2A (Session bugs fixed)

**Description:**
Reduce Orchestrator god object by extracting session management logic.

**Current State:**
```python
# Orchestrator handles:
- create_session()
- get_session()
- list_sessions()
- update_session()
- delete_session()
```

**Target State:**
```python
# SessionManager handles all session CRUD
# Orchestrator only coordinates stages

class SessionManager:
    async def create_session(self, user_id, project_name)
    async def get_session(self, session_id)
    async def list_sessions(self, user_id, limit, skip)
    async def update_session(self, session_id, data)
    async def delete_session(self, session_id)

class Orchestrator:
    def __init__(self, session_manager, agent_registry):
        self.sessions = session_manager
        self.agents = agent_registry

    async def execute_stage(self, session_id, stage_num)
```

**Tasks:**
- [ ] Create SessionManager class
- [ ] Move all session methods from Orchestrator
- [ ] Inject SessionRepository into SessionManager
- [ ] Update Orchestrator to use SessionManager
- [ ] Update tests to mock SessionManager
- [ ] Verify all tests still pass
- [ ] Run integration tests
- [ ] Measure Orchestrator size reduction

---

#### P2F.2: Extract AgentRegistry from Orchestrator
**Priority:** MEDIUM
**Status:** NOT STARTED
**Effort:** 2-3 hours
**Dependency:** P2F.1

**Description:**
Extract agent initialization and management.

**Current State:**
```python
# Orchestrator manages:
- agent initialization
- agent registry/lookup
- agent selection by stage
```

**Target State:**
```python
class AgentRegistry:
    def get_agent(self, stage_num: int) -> Agent
    def initialize_all_agents(self) -> None
    def validate_agent_config(self) -> bool

# Orchestrator delegates to registry
agent = self.agent_registry.get_agent(stage_num)
```

**Tasks:**
- [ ] Create AgentRegistry class
- [ ] Move agent initialization code
- [ ] Implement get_agent() method
- [ ] Implement initialize_all_agents()
- [ ] Update Orchestrator to use registry
- [ ] Update tests
- [ ] Verify all tests pass

---

#### P2F.3: Extract StageExecutor from Orchestrator
**Priority:** MEDIUM
**Status:** NOT STARTED
**Effort:** 3-4 hours
**Dependency:** P2F.1, P2F.2

**Description:**
Extract stage execution logic into dedicated class.

**Current State:**
```python
# Orchestrator handles:
- stage execution coordination
- validation before/after
- checkpoint creation
```

**Target State:**
```python
class StageExecutor:
    async def execute_stage(self, session_id, stage_num) -> StageResult
    async def validate_stage_output(self, output) -> ValidationResult
    async def create_checkpoint(self, session_id, stage_num) -> None

# Orchestrator becomes thin coordinator
result = await self.executor.execute_stage(session_id, stage_num)
```

**Tasks:**
- [ ] Create StageExecutor class
- [ ] Move execute_stage() logic
- [ ] Move validation logic
- [ ] Move checkpoint creation
- [ ] Update Orchestrator to delegate
- [ ] Update tests
- [ ] Verify tests pass

---

### PHASE 2G: TESTING & QUALITY (Days 14-15)

#### P2G.1: Add Integration Tests
**Priority:** HIGH
**Status:** NOT STARTED
**Effort:** 4-5 hours
**Dependency:** P2A (bugs fixed), P2B (auth), P2E (frontend working)

**Description:**
Test complete workflows end-to-end with live database and API.

**Test Scenarios:**

1. **Session Lifecycle**
   ```python
   def test_complete_session_workflow():
       # 1. Create user
       user = create_user("test@example.com")

       # 2. Create session
       session = create_session(user_id, "Test Project")

       # 3. Execute stage 1
       result = execute_stage(session_id, 1)
       assert result.status == "success"

       # 4. Verify persistence
       persisted_session = get_session(session_id)
       assert persisted_session.current_stage == 1

       # 5. Execute remaining stages
       for stage in [2, 3, 4, 5]:
           execute_stage(session_id, stage)

       # 6. Generate charter
       charter = generate_charter(session_id)
       assert charter.content is not None
   ```

2. **User Isolation**
   ```python
   def test_user_isolation():
       user1_session = create_session(user1_id, "Project 1")
       user2_sessions = list_sessions(user2_id)
       assert user1_session.session_id not in [s.id for s in user2_sessions]
   ```

3. **Error Handling**
   ```python
   def test_invalid_stage():
       with pytest.raises(InvalidStageError):
           execute_stage(session_id, 99)

   def test_unauthenticated_access():
       response = api_client.get(f"/sessions/{session_id}")
       assert response.status_code == 401
   ```

**Tasks:**
- [ ] Create tests/integration/ directory
- [ ] Write session lifecycle test
- [ ] Write user isolation test
- [ ] Write error handling tests
- [ ] Write stage progression tests
- [ ] Create fixtures for test data
- [ ] Run full integration test suite
- [ ] Achieve 80%+ coverage

---

#### P2G.2: Performance Testing
**Priority:** LOW
**Status:** NOT STARTED
**Effort:** 2-3 hours
**Dependency:** P2G.1

**Description:**
Verify API can handle expected load and measure performance.

**Metrics to Measure:**
- Session creation latency (<100ms)
- Session listing latency (<500ms)
- Stage execution latency (varies, depends on LLM)
- Database query time (<100ms)
- Peak concurrent users (target: 10)

**Tools:** Apache JMeter or k6

**Tasks:**
- [ ] Create performance test scripts
- [ ] Test session creation (100 requests)
- [ ] Test session listing (1000 records)
- [ ] Measure p50/p95/p99 latencies
- [ ] Identify bottlenecks
- [ ] Document baseline metrics

---

## 📈 SUCCESS METRICS & COMPLETION CRITERIA

### Overall Phase 2 Success Criteria
- [ ] All P2A critical bugs fixed and tested
- [ ] JWT authentication implemented and working
- [ ] CI/CD pipeline configured and passing
- [ ] LLM integration hardened with retry logic
- [ ] Frontend connects to backend successfully
- [ ] Users can complete full workflow
- [ ] All tests passing (pytest + frontend)
- [ ] No regressions from P1

### Detailed Acceptance Criteria

| Task | Definition of Done |
|------|-------------------|
| P2A.1: Session CRUD Bug | GET /sessions/{id} returns 200, data matches DB |
| P2B.1: JWT Auth | Users register, login, token validates, endpoints require auth |
| P2C.1: CI/CD | Tests run on every commit, status checks prevent merge |
| P2D.1: LLM Retry | Retries on 429, fallback to Ollama works, token tracking accurate |
| P2E.3: E2E Test | User can complete stage 1-5 flow, data persists, UI responsive |
| P2F.1-3: Refactor | Orchestrator <200 lines, each class has single responsibility |
| P2G.1: Integration Tests | 80%+ coverage, all workflows tested, error cases handled |

---

## 📅 TIMELINE & MILESTONES

### Weekly Breakdown

**Week 1 (Oct 28 - Nov 3)**
- Day 1-2: P2A (bug fixes)
- Day 3-4: P2B (authentication)
- Day 5-6: P2C (CI/CD)
- Day 7-8: P2D (LLM hardening)

**Week 2 (Nov 4 - Nov 7)**
- Day 9-10: P2E (frontend integration)
- Day 11-13: P2F (refactoring)
- Day 14-15: P2G (testing)

### Milestones
- **Oct 31:** P2A, P2B complete (tests passing, auth working)
- **Nov 3:** P2C, P2D complete (CI/CD running, LLM resilient)
- **Nov 6:** P2E, P2F complete (frontend working, code clean)
- **Nov 7:** P2G complete (high test coverage, performance baseline)

---

## 🔧 DEPENDENCIES & BLOCKERS

### Task Dependencies
```
P2A.1 (Session Bug Fix) → P2E.3 (E2E Test) → P2G.1 (Integration Tests)
                            ↑
P2B.1 (Authentication) ────┘
                            ↑
P2C.1 (CI/CD) ──────────────┘

P2D.1 (LLM Retry) → P2G.2 (Performance Test)

P2F.1 (SessionManager) → P2F.2 (AgentRegistry) → P2F.3 (StageExecutor)
```

### Known Blockers
- Session retrieval 404 error (P2A.1 critical blocker)
- Frontend npm install might have conflicts
- Ollama availability for fallback testing

---

## 📝 DOCUMENTATION UPDATES REQUIRED

After each major phase completion, update:
1. README.md - Add auth section
2. QUICK_START.md - Add authentication steps
3. API.md - Document all endpoints (auto-generate from OpenAPI)
4. ARCHITECTURE.md - Update class diagrams with new structure
5. DEPLOYMENT.md - Add CI/CD section

---

## 🎯 SUCCESS VISION

**By end of P2 (November 7):**

✅ **Security:** Users authenticate, sessions isolated, API protected
✅ **Reliability:** LLM failures handled gracefully with retries
✅ **Automation:** Tests run on every commit, builds automated
✅ **Integration:** Frontend fully connected to backend
✅ **Quality:** 80%+ test coverage, no regressions
✅ **Maintainability:** Code refactored, classes follow SRP

**Result:** Production-ready foundation for P3 (monitoring, features, scaling)

---

**Created:** October 24, 2025
**Last Updated:** October 24, 2025
**Next Review:** After P2A completion (Oct 31)
**Status:** READY TO START
