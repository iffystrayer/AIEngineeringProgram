# U-AIP Remediation Task List

A prioritized, actionable task list for addressing security, reliability, and quality issues.

---

## Priority Levels

| Priority | Timeline | Description |
|----------|----------|-------------|
| **P0** | 1-3 days | Critical security - MUST fix before any external access |
| **P1** | 1-2 weeks | High priority - Fix before beta testing |
| **P2** | 1-2 months | Production hardening - Fix before GA release |

---

## P0: Critical Security Fixes (Days)

### P0-1: Remove Hardcoded JWT Secret

**File:** `src/auth/security.py:17`

**Current Code:**
```python
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Load from environment
```

**Fix:**
```python
import os

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable is required")
```

**Verification:**
```bash
# Should fail if JWT_SECRET not set
unset JWT_SECRET && python -c "from src.auth.security import SECRET_KEY"
```

---

### P0-2: Add JWT_SECRET Validation on Startup

**File:** `src/api/main.py` - in `startup_event()`

**Add:**
```python
@app.on_event("startup")
async def startup_event():
    # Validate required secrets
    if not os.getenv("JWT_SECRET"):
        raise RuntimeError("JWT_SECRET environment variable is required")
    if len(os.getenv("JWT_SECRET", "")) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters")
    # ... rest of startup
```

---

### P0-3: Remove Hardcoded DB Password from Connection Module

**File:** `src/database/connection.py:35`

**Current Code:**
```python
password: str = "changeme",
```

**Fix:**
```python
password: str = Field(..., description="Database password - required")
```

Or if using dataclass:
```python
password: str  # No default - must be provided
```

---

### P0-4: Remove Hardcoded DB Passwords from CLI

**File:** `src/cli/main.py`

**Locations to fix:** Lines 195, 426, 665, 866, 980, 1117

**Pattern to find:**
```bash
grep -n "changeme" src/cli/main.py
```

**Fix each occurrence:**
```python
# Before
password = os.getenv("DB_PASSWORD", "changeme")

# After
password = os.getenv("DB_PASSWORD")
if not password:
    raise click.ClickException("DB_PASSWORD environment variable is required")
```

---

### P0-5: Add Authentication to All Endpoints

**File:** `src/api/app.py`

**Step 1:** Create authentication dependency
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.security import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Validate JWT token and return user info."""
    token = credentials.credentials
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_data
```

**Step 2:** Add to each endpoint
```python
# Before
@app.post("/api/sessions")
async def create_session(request: SessionRequest):

# After
@app.post("/api/sessions")
async def create_session(
    request: SessionRequest,
    current_user: dict = Depends(get_current_user)
):
```

**Endpoints requiring authentication:**
- [ ] `POST /api/sessions` (line ~116)
- [ ] `GET /api/sessions/{session_id}` (line ~160)
- [ ] `GET /api/sessions` (line ~194)
- [ ] `DELETE /api/sessions/{session_id}` (line ~223)
- [ ] `GET /api/sessions/{session_id}/progress` (line ~252)
- [ ] `POST /api/sessions/{session_id}/answer` (line ~280)
- [ ] `GET /api/sessions/{session_id}/events` (line ~309)
- [ ] `GET /api/sessions/{session_id}/stream` (line ~331)

---

### P0-6: Add Session Ownership Validation

**File:** `src/api/main.py`

**Add helper function:**
```python
async def validate_session_ownership(
    session_id: UUID,
    current_user: dict,
    session_repo: SessionRepository
) -> Session:
    """Validate user owns the session."""
    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return session
```

**Apply to all session endpoints:**
```python
@app.get("/api/v1/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session_uuid = validate_uuid(session_id)
    session = await validate_session_ownership(
        session_uuid, current_user, session_repo
    )
    # ... rest of handler
```

---

### P0-7: Fix Error Message Information Disclosure

**Files:** `src/api/app.py`, `src/api/main.py`

**Current Pattern (INSECURE):**
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

**Fixed Pattern:**
```python
import uuid

except Exception as e:
    error_id = str(uuid.uuid4())[:8]
    logger.error(f"Error {error_id}: {e}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail=f"Internal server error. Reference: {error_id}"
    )
```

**Locations to fix:**
- `src/api/app.py`: Lines 157, 191, 220, 245, 277, 306, 324, 363
- `src/api/main.py`: Lines 434, 662

---

### P0-8: Fix Silent Data Loss in Orchestrator

**File:** `src/agents/orchestrator.py:401-403`

**Current Code (DANGEROUS):**
```python
except Exception as e:
    logger.error(f"Failed to persist stage completion: {e}")
    # Don't raise - allow session to continue even if persistence fails
```

**Fixed Code:**
```python
except Exception as e:
    logger.error(f"Failed to persist stage completion: {e}", exc_info=True)
    raise StageCompletionError(
        f"Failed to save stage data. Please retry. Error: {e}"
    )
```

**Also add exception class in `src/exceptions.py`:**
```python
class StageCompletionError(UAIPError):
    """Raised when stage completion fails to persist."""
    pass
```

---

## P1: High Priority Fixes (Weeks)

### P1-1: Fix Session Retrieval 404 Bug

**Investigation Steps:**
1. Check if session_id format matches between creation and retrieval
2. Verify UUID parsing in `validate_uuid()`
3. Check if session is being created in correct database
4. Verify repository `get_by_id` query

**Debug Commands:**
```bash
# Check database for sessions
docker exec -it uaip-db psql -U uaip_user -d uaip_scoping -c "SELECT session_id, user_id FROM sessions;"

# Test API directly
curl -X POST http://localhost:38937/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "project_name": "Test Project"}'

# Then try to retrieve
curl http://localhost:38937/api/v1/sessions/{returned_id}
```

---

### P1-2: Fix Session List Returning Empty

**Investigation Steps:**
1. Check query in `SessionRepository.list_all()` or `list_by_user()`
2. Verify connection is to correct database
3. Check if pagination is incorrectly filtering results

**File:** `src/database/repositories/session_repository.py`

---

### P1-3 & P1-4: Fix CLI Database Initialization

**File:** `src/cli/main.py`

**Fix delete_command (around line 860):**
```python
@cli.command("delete")
@click.argument("session_id")
def delete_command(session_id: str):
    """Delete a session."""
    async def _delete():
        db_config = DatabaseConfig.from_env()
        db_manager = DatabaseManager(db_config)
        try:
            await db_manager.initialize()  # ADD THIS
            session_repo = SessionRepository(db_manager)
            # ... rest of logic
        finally:
            await db_manager.close()  # ADD THIS

    asyncio.run(_delete())
```

**Apply same pattern to status_command (around line 1119)**

---

### P1-5: Add Resource Cleanup to All CLI Commands

**Pattern for all async CLI commands:**
```python
async def _async_operation():
    db_manager = None
    try:
        db_config = DatabaseConfig.from_env()
        db_manager = DatabaseManager(db_config)
        await db_manager.initialize()

        # ... operation logic ...

    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
    finally:
        if db_manager:
            await db_manager.close()
```

---

### P1-6: Fix Memory Leak in Session Locks

**File:** `src/agents/orchestrator.py:212-227`

**Option A: TTL-based cleanup**
```python
import time
from typing import Dict, Tuple

class Orchestrator:
    def __init__(self):
        self._session_locks: Dict[UUID, Tuple[asyncio.Lock, float]] = {}
        self._lock_ttl_seconds = 3600  # 1 hour

    async def _get_session_lock(self, session_id: UUID) -> asyncio.Lock:
        async with self._global_lock:
            self._cleanup_stale_locks()
            if session_id not in self._session_locks:
                self._session_locks[session_id] = (asyncio.Lock(), time.time())
            else:
                # Update last access time
                lock, _ = self._session_locks[session_id]
                self._session_locks[session_id] = (lock, time.time())
            return self._session_locks[session_id][0]

    def _cleanup_stale_locks(self):
        """Remove locks not accessed within TTL."""
        now = time.time()
        stale = [
            sid for sid, (_, last_access) in self._session_locks.items()
            if now - last_access > self._lock_ttl_seconds
        ]
        for sid in stale:
            del self._session_locks[sid]
```

**Option B: WeakValueDictionary (simpler)**
```python
from weakref import WeakValueDictionary

self._session_locks = WeakValueDictionary()
```

---

### P1-7: Add Email Validation

**File:** `src/api/models.py`

```python
from pydantic import BaseModel, Field, EmailStr

class UserRegisterRequest(BaseModel):
    email: EmailStr  # Changed from str
    password: str = Field(..., min_length=8)
```

---

### P1-8: Add Password Complexity

**File:** `src/api/models.py`

```python
import re
from pydantic import BaseModel, Field, validator

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_complexity(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
```

---

### P1-9: Add Input Field Validation

**File:** `src/api/models.py`

```python
from pydantic import BaseModel, Field, validator
import re

class SessionRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    project_name: str = Field(..., min_length=1, max_length=500)

    @validator('user_id')
    def validate_user_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('user_id must be alphanumeric with underscores/hyphens only')
        return v

    @validator('project_name')
    def validate_project_name(cls, v):
        # Prevent injection attempts
        if re.search(r'[<>"\']', v):
            raise ValueError('project_name contains invalid characters')
        return v.strip()
```

---

### P1-10: Remove Placeholder Tests

**Find all placeholder tests:**
```bash
grep -rn "assert True" tests/ | grep -v ".pyc"
```

**For each occurrence, either:**
1. Delete the test if it's pure specification
2. Replace with actual assertions
3. Mark as `@pytest.mark.skip(reason="Not implemented")` with TODO

---

### P1-11: Fix Broken Test Fixture

**File:** `tests/conftest.py:59-71`

**Current (broken):**
```python
async def mock_transaction():
    conn = AsyncMock()
    return conn

manager.transaction = AsyncMock(return_value=mock_transaction())
```

**Fixed:**
```python
@pytest_asyncio.fixture
async def mock_db_manager():
    manager = AsyncMock()

    @asynccontextmanager
    async def mock_transaction():
        conn = AsyncMock()
        conn.execute = AsyncMock(return_value=None)
        conn.fetchrow = AsyncMock(return_value=None)
        conn.fetch = AsyncMock(return_value=[])
        yield conn

    manager.transaction = mock_transaction
    manager.acquire = AsyncMock()
    return manager
```

---

### P1-12 & P1-13: Fix Test Fixture Credentials and Cleanup

**File:** `tests/conftest.py:87-106`

```python
@pytest_asyncio.fixture
async def test_db_manager():
    config = DatabaseConfig(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=int(os.getenv("TEST_DB_PORT", "15433")),
        database=os.getenv("TEST_DB_NAME", "uaip_scoping_test"),
        user=os.getenv("TEST_DB_USER"),
        password=os.getenv("TEST_DB_PASSWORD"),
    )

    if not config.user or not config.password:
        pytest.skip("Test database credentials not configured")

    manager = DatabaseManager(config)
    await manager.initialize()

    yield manager

    # Proper cleanup with error handling
    try:
        await manager.close()
    except Exception as e:
        logger.warning(f"Test cleanup warning: {e}")
        # Re-raise to make test failures visible
        raise
```

---

## P2: Production Hardening (Months)

### P2-1: Implement HTTPS/TLS

**Options:**
1. **Reverse Proxy (Recommended):** Add nginx/traefik in front
2. **Direct TLS:** Configure uvicorn with SSL certificates

**nginx example:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/uaip.crt;
    ssl_certificate_key /etc/ssl/private/uaip.key;

    location / {
        proxy_pass http://uaip-api:8000;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

---

### P2-2: Implement Per-User Rate Limiting

**File:** `src/api/rate_limiting.py`

```python
from slowapi import Limiter

def get_user_identifier(request: Request) -> str:
    """Get user ID from JWT token for rate limiting."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        user_data = verify_token(token)
        if user_data:
            return f"user:{user_data['user_id']}"
    # Fallback to IP for unauthenticated requests
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=get_user_identifier)
```

---

### P2-3: Add Audit Logging

**Create:** `src/utils/audit_logger.py`

```python
import structlog
from datetime import datetime
from typing import Optional

audit_log = structlog.get_logger("audit")

def log_data_access(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    success: bool,
    details: Optional[dict] = None
):
    audit_log.info(
        "data_access",
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        success=success,
        details=details,
        timestamp=datetime.utcnow().isoformat()
    )
```

**Usage in endpoints:**
```python
@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    log_data_access(
        user_id=current_user["user_id"],
        action="READ",
        resource_type="session",
        resource_id=session_id,
        success=True
    )
```

---

### P2-4 & P2-5: Implement Refresh Tokens

**File:** `src/auth/security.py`

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour (down from 24)
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "refresh"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def verify_refresh_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None
```

**Add refresh endpoint:**
```python
@app.post("/api/v1/auth/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Issue new access token
    new_access_token = create_access_token(user_id, email)
    return {"access_token": new_access_token, "token_type": "bearer"}
```

---

### P2-6: Add LLM Output Sanitization

**File:** `src/llm/providers/anthropic_provider.py`

```python
import re
import html

def sanitize_llm_output(text: str) -> str:
    """Sanitize LLM output before storage/display."""
    # Remove potential script injection
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Escape HTML entities
    text = html.escape(text)
    # Remove null bytes
    text = text.replace('\x00', '')
    # Limit length
    return text[:50000]  # Max 50k chars
```

---

### P2-7: Session Timeout/Revocation

**Database addition:**
```sql
CREATE TABLE revoked_tokens (
    token_jti VARCHAR(255) PRIMARY KEY,
    revoked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255)
);

CREATE INDEX idx_revoked_tokens_jti ON revoked_tokens(token_jti);
```

**Token verification update:**
```python
async def verify_token_not_revoked(token: str, db: DatabaseManager) -> bool:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload.get("jti")
    if not jti:
        return True  # Legacy tokens without jti

    async with db.transaction() as conn:
        result = await conn.fetchrow(
            "SELECT 1 FROM revoked_tokens WHERE token_jti = $1",
            jti
        )
        return result is None
```

---

### P2-8 & P2-9: Write Real Integration Tests

**Create:** `tests/integration/test_auth_flow.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_full_auth_flow(test_client: AsyncClient):
    # Register
    response = await test_client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201

    # Login
    response = await test_client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Access protected route
    response = await test_client.get(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Verify unauthorized access fails
    response = await test_client.get("/api/v1/sessions")
    assert response.status_code == 401
```

---

### P2-10: Add Load Testing

**Create:** `tests/load/locustfile.py`

```python
from locust import HttpUser, task, between

class UAIPUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "LoadTest123!"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_sessions(self):
        self.client.get("/api/v1/sessions", headers=self.headers)

    @task(1)
    def create_session(self):
        self.client.post("/api/v1/sessions",
            headers=self.headers,
            json={"project_name": "Load Test Project"}
        )
```

**Run with:**
```bash
locust -f tests/load/locustfile.py --host=http://localhost:38937
```

---

## Verification Checklist

After completing all P0 tasks, verify:

- [ ] `grep -r "your-secret-key" src/` returns nothing
- [ ] `grep -r "changeme" src/` returns nothing
- [ ] All endpoints return 401 without auth token
- [ ] Users cannot access other users' sessions
- [ ] Error responses don't contain stack traces
- [ ] Stage completion failures are reported to user

After completing P1 tasks, verify:

- [ ] Session creation and retrieval works end-to-end
- [ ] All CLI commands work without crashes
- [ ] `pytest --tb=short` shows no `assert True` tests
- [ ] Test coverage report shows >70% coverage

---

## Quick Reference: Files to Modify

| Priority | File | Lines |
|----------|------|-------|
| P0 | `src/auth/security.py` | 17 |
| P0 | `src/database/connection.py` | 35 |
| P0 | `src/cli/main.py` | 195, 426, 665, 866, 980, 1117 |
| P0 | `src/api/app.py` | 116-370 |
| P0 | `src/api/main.py` | 451-468, 434, 662 |
| P0 | `src/agents/orchestrator.py` | 401-403 |
| P1 | `src/cli/main.py` | 860, 1119 |
| P1 | `src/agents/orchestrator.py` | 212-227 |
| P1 | `src/api/models.py` | 19-100 |
| P1 | `tests/conftest.py` | 59-71, 87-106 |

---

*Task list generated December 8, 2025*
