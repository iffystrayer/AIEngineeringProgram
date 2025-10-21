# 🔧 TEST FIX ACTION PLAN

**Objective:** Fix 109 failing tests and 117 errors  
**Current Status:** 525/634 passing (82.8%)  
**Target:** 634/634 passing (100%)  
**Estimated Effort:** 6-8 hours

---

## 📋 ISSUE BREAKDOWN & FIXES

### ISSUE #1: Repository Initialization (40 errors)
**Files Affected:**
- `tests/test_session_repository.py` (40 errors)
- `tests/test_stage_data_repository.py` (30 errors)

**Error:** `TypeError: SessionRepository.__init__() missing 1 required positional argument: 'db_manager'`

**Root Cause:** Tests creating repositories without `db_manager` parameter

**Fix Strategy:**
1. Update `conftest.py` to create mock `db_manager` fixture
2. Update all repository test fixtures to pass `db_manager`
3. Verify repository methods work with mock database

**Code Changes Needed:**
```python
# In conftest.py
@pytest.fixture
async def mock_db_manager():
    """Create mock database manager for tests."""
    manager = AsyncMock()
    manager.acquire = AsyncMock()
    manager.transaction = AsyncMock()
    return manager

# In test files
def test_create_session(mock_db_manager):
    repo = SessionRepository(mock_db_manager)
    # ... rest of test
```

**Effort:** 2 hours

---

### ISSUE #2: Test Database Not Created (17 errors)
**Files Affected:**
- `tests/integration/test_database_integration.py` (17 errors)

**Error:** `database "uaip_scoping_test" does not exist`

**Root Cause:** Integration tests need test database setup

**Fix Strategy:**
1. Create `tests/conftest.py` with database setup
2. Add pytest fixture to create/drop test database
3. Use fixture in integration tests

**Code Changes Needed:**
```python
# In tests/conftest.py
@pytest.fixture(scope="session")
async def test_database():
    """Create test database."""
    # Connect to postgres
    # Create uaip_scoping_test database
    # Run migrations
    yield
    # Drop test database

@pytest.fixture
async def db_manager(test_database):
    """Create real database manager for integration tests."""
    manager = DatabaseManager()
    await manager.initialize()
    yield manager
    await manager.close()
```

**Effort:** 1.5 hours

---

### ISSUE #3: Asyncio Event Loop Conflicts (8 failures)
**Files Affected:**
- `tests/test_cli_resume_command.py` (8 failures)

**Error:** `asyncio.run() cannot be called from a running event loop`

**Root Cause:** CLI tests using `asyncio.run()` inside pytest-asyncio context

**Fix Strategy:**
1. Replace `asyncio.run()` with `pytest.mark.asyncio`
2. Use `await` instead of `asyncio.run()`
3. Update CLI test fixtures

**Code Changes Needed:**
```python
# OLD (broken)
def test_resume_command():
    result = asyncio.run(cli_runner.invoke(resume, [session_id]))

# NEW (fixed)
@pytest.mark.asyncio
async def test_resume_command():
    result = await cli_runner.invoke(resume, [session_id])
```

**Effort:** 1 hour

---

### ISSUE #4: Schema Mismatch (30+ errors)
**Files Affected:**
- `tests/integration/test_stage2_conversation_integration.py` (8 errors)
- `tests/integration/test_stage3_conversation_integration.py` (8 errors)
- `tests/integration/test_stage4_conversation_integration.py` (8 errors)
- `tests/integration/test_stage5_conversation_integration.py` (10 errors)

**Error:** `TypeError: ProblemStatement.__init__() got an unexpected keyword argument 'success_criteria'`

**Root Cause:** Test fixtures using old schema field names

**Fix Strategy:**
1. Review current schema in `src/models/schemas.py`
2. Update test fixtures to use correct field names
3. Verify all model instantiations match current schema

**Code Changes Needed:**
```python
# OLD (broken)
problem = ProblemStatement(
    success_criteria="...",  # OLD FIELD
    ...
)

# NEW (fixed)
problem = ProblemStatement(
    business_problem="...",  # CORRECT FIELD
    ...
)
```

**Effort:** 2 hours

---

### ISSUE #5: Logging Sanitizer (2 failures)
**Files Affected:**
- `tests/test_logging_sanitizer.py` (2 failures)

**Error:** Email/IP masking not working

**Root Cause:** Sanitizer configuration issue

**Fix Strategy:**
1. Review sanitizer configuration
2. Verify masking rules are applied
3. Update test expectations if needed

**Effort:** 0.5 hours

---

## 🎯 EXECUTION PLAN

### Phase 1: Setup (1.5 hours)
- [ ] Create/update `tests/conftest.py`
- [ ] Add mock `db_manager` fixture
- [ ] Add test database setup fixture
- [ ] Verify fixtures work

### Phase 2: Repository Tests (2 hours)
- [ ] Update `tests/test_session_repository.py`
- [ ] Update `tests/test_stage_data_repository.py`
- [ ] Run tests: `pytest tests/test_session_repository.py -v`
- [ ] Run tests: `pytest tests/test_stage_data_repository.py -v`

### Phase 3: Integration Tests (1.5 hours)
- [ ] Update `tests/integration/test_database_integration.py`
- [ ] Update stage conversation integration tests
- [ ] Run tests: `pytest tests/integration/ -v`

### Phase 4: CLI Tests (1 hour)
- [ ] Update `tests/test_cli_resume_command.py`
- [ ] Update `tests/test_cli_start_command.py`
- [ ] Run tests: `pytest tests/test_cli_*.py -v`

### Phase 5: Verification (1 hour)
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify 634/634 tests pass
- [ ] Check for regressions
- [ ] Run E2E tests: `npm run e2e`

---

## 📊 SUCCESS CRITERIA

- [ ] All 634 tests passing
- [ ] No errors or failures
- [ ] E2E tests passing
- [ ] No regressions from previous runs
- [ ] Code coverage maintained

---

## 🚀 TIMELINE

| Phase | Duration | Status |
|-------|----------|--------|
| Setup | 1.5h | ⏳ TODO |
| Repository Tests | 2h | ⏳ TODO |
| Integration Tests | 1.5h | ⏳ TODO |
| CLI Tests | 1h | ⏳ TODO |
| Verification | 1h | ⏳ TODO |
| **TOTAL** | **7 hours** | ⏳ TODO |

---

## 📝 NOTES

- All changes are test-only (no production code changes)
- Fixes are backward compatible
- No breaking changes to API
- All fixes follow existing patterns in codebase


