# Implementation Roadmap: From Alpha to Production

## 🎯 Phase 1: ALPHA FUNCTIONALITY (2-3 Days)
**Goal:** Make the application stateful and functional as documented

### Task 1.1: Wire Orchestrator to Database (4-6 hours)
**File:** `src/agents/orchestrator.py`

**Changes:**
1. Implement `_initialize_agent_registries()` (lines 99-150)
   - Instantiate all 5 stage agents
   - Instantiate reflection agents
   - Store in `self.stage_agents` and `self.reflection_agents`

2. Implement `run_stage()` method (lines 200-250)
   - Get agent from registry
   - Execute stage with session context
   - Capture output
   - Return stage deliverable

3. Implement `_persist_session()` (lines 300+)
   - Use SessionRepository to save session
   - Update current_stage and status
   - Save stage data

4. Implement `_load_session_from_db()` (lines 350+)
   - Use SessionRepository to load session
   - Restore stage data
   - Restore conversation history

**Testing:**
```bash
uv run pytest tests/test_orchestrator.py -v
```

---

### Task 1.2: Fix CLI Resume/List Commands (2-3 hours)
**File:** `src/cli/main.py`

**Changes:**
1. Resume command (lines 494-520)
   - Remove placeholder messages
   - Call orchestrator.run_stage() for remaining stages
   - Persist progress after each stage

2. List command (lines 664-677)
   - Already mostly implemented
   - Just remove placeholder text

3. Delete command (lines 770-812)
   - Implement actual deletion via SessionRepository
   - Add confirmation prompt

4. Status command (lines 1013-1040)
   - Load session from database
   - Display current stage, progress, quality scores
   - Show conversation history

**Testing:**
```bash
uv run pytest tests/test_cli_*.py -v
```

---

### Task 1.3: Complete Charter Generation (3-4 hours)
**File:** `src/agents/orchestrator.py` lines 700-750

**Changes:**
1. Aggregate stage data
   - Collect all 5 stage outputs
   - Validate completeness
   - Handle missing data gracefully

2. Implement governance decision logic
   - Calculate overall risk score
   - Apply decision thresholds
   - Return PROCEED/REVISE/HALT/SUBMIT_TO_COMMITTEE

3. Calculate residual risk
   - Sum ethical risks from Stage 5
   - Apply mitigation effectiveness
   - Return final risk score

4. Generate charter object
   - Populate all charter fields
   - Add metadata (timestamps, user info)
   - Persist to database

**Testing:**
```bash
uv run pytest tests/integration/test_orchestrator_end_to_end.py -v
```

---

## 🟡 Phase 2: BETA STABILITY (2-3 Weeks)
**Goal:** Stabilize tests, integrate reflection agents, improve documentation

### Task 2.1: Stabilize Test Suite (2-3 days)
**Files:** `tests/agents/test_response_quality_agent.py` and others

**Changes:**
1. Fix ResponseQualityAgent tests
   - Update mocks to match real LLM response format
   - Add bracket-counting algorithm tests
   - Test JSON parsing edge cases

2. Fix async test fixtures
   - Resolve event loop conflicts
   - Use proper pytest-asyncio markers
   - Add proper cleanup

3. Add integration tests
   - Test full 5-stage workflow
   - Test session persistence
   - Test charter generation

**Target:** 95%+ pass rate

---

### Task 2.2: Integrate Reflection Agents (2-3 days)
**Files:** `src/agents/orchestrator.py`, reflection agents

**Changes:**
1. Wire ConsistencyCheckerAgent
   - Call after Stage 5
   - Check cross-stage consistency
   - Block charter generation on critical contradictions

2. Wire StageGateValidatorAgent
   - Call after each stage
   - Validate stage-specific requirements
   - Provide feedback for improvement

3. Implement stage-gate enforcement
   - Don't advance to next stage if validation fails
   - Offer retry or escalation options

---

### Task 2.3: Update Documentation (1-2 days)
**Files:** `README.md`, `ALPHA_RELEASE_STATUS.md`

**Changes:**
1. Correct misleading claims
   - Remove "production-ready" badge
   - Update test pass rate to actual
   - Document known limitations

2. Add accurate status badges
   - Use real metrics
   - Link to detailed status documents

3. Document known issues
   - List all open issues
   - Provide workarounds
   - Set expectations

---

## 🟢 Phase 3: PRODUCTION READINESS (2-3 Weeks)
**Goal:** Performance, monitoring, deployment automation

### Task 3.1: Performance Optimization (1-2 days)
- LLM response caching
- Parallel stage execution (where applicable)
- Database query optimization
- Connection pool tuning

### Task 3.2: Monitoring & Observability (2-3 days)
- Prometheus metrics
- Structured logging
- Error tracking (Sentry)
- Performance monitoring

### Task 3.3: Deployment Automation (1-2 days)
- CI/CD pipeline (GitHub Actions)
- Automated testing on push
- Staging environment
- Production deployment

---

## 📋 DETAILED TASK BREAKDOWN

### Phase 1, Task 1.1: Orchestrator Wiring

**Subtask 1.1.1:** Implement agent registry initialization
```python
def _initialize_agent_registries(self) -> None:
    """Initialize all stage and reflection agents."""
    # Stage agents
    self.stage_agents = {
        1: Stage1Agent(llm_router=self.llm_router),
        2: Stage2Agent(llm_router=self.llm_router),
        3: Stage3Agent(llm_router=self.llm_router),
        4: Stage4Agent(llm_router=self.llm_router),
        5: Stage5Agent(llm_router=self.llm_router),
    }
    
    # Reflection agents
    self.reflection_agents = {
        'quality': ResponseQualityAgent(llm_router=self.llm_router),
        'consistency': ConsistencyCheckerAgent(llm_router=self.llm_router),
        'gate': StageGateValidatorAgent(llm_router=self.llm_router),
    }
```

**Subtask 1.1.2:** Implement run_stage method
```python
async def run_stage(self, session: Session, stage_num: int) -> Any:
    """Execute a specific stage."""
    if stage_num not in self.stage_agents:
        raise InvalidStageNumberError(f"Invalid stage: {stage_num}")
    
    agent = self.stage_agents[stage_num]
    stage_output = await agent.conduct_interview(session)
    
    # Persist
    await self._persist_session(session)
    
    return stage_output
```

**Subtask 1.1.3:** Implement persistence methods
```python
async def _persist_session(self, session: Session) -> None:
    """Persist session to database."""
    repo = SessionRepository(self.db_pool)
    await repo.update(session)

async def _load_session_from_db(self, session_id: UUID) -> Session:
    """Load session from database."""
    repo = SessionRepository(self.db_pool)
    return await repo.get_by_id(session_id)
```

---

## 🎯 SUCCESS CRITERIA

### Phase 1 (Alpha)
- [ ] All 5 stages execute end-to-end
- [ ] Sessions persist to database
- [ ] Resume functionality works
- [ ] Charter generation completes
- [ ] Export produces valid documents
- [ ] 90%+ test pass rate

### Phase 2 (Beta)
- [ ] 95%+ test pass rate
- [ ] Reflection agents integrated
- [ ] Documentation accurate
- [ ] No critical bugs
- [ ] Performance acceptable

### Phase 3 (Production)
- [ ] 98%+ test pass rate
- [ ] Monitoring in place
- [ ] CI/CD automated
- [ ] Load testing passed
- [ ] Security audit passed

---

## 📊 EFFORT ESTIMATION

| Phase | Duration | Effort | Risk |
|-------|----------|--------|------|
| Phase 1 (Alpha) | 2-3 days | 18-24h | Medium |
| Phase 2 (Beta) | 2-3 weeks | 60-80h | Low |
| Phase 3 (Production) | 2-3 weeks | 40-60h | Low |
| **TOTAL** | **6-8 weeks** | **120-160h** | **Medium** |

---

## 🚀 QUICK START FOR IMPLEMENTATION

1. **Start with Phase 1, Task 1.1**
   - Most critical blocker
   - Unblocks all other work
   - Relatively straightforward

2. **Then Phase 1, Task 1.2**
   - Depends on 1.1
   - Enables user-facing functionality

3. **Then Phase 1, Task 1.3**
   - Depends on 1.1 and 1.2
   - Completes alpha functionality

4. **Then Phase 2**
   - Stabilize and enhance
   - Prepare for beta

5. **Then Phase 3**
   - Production hardening
   - Deployment automation

---

## ⚠️ RISKS & MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Orchestrator integration complex | Medium | High | Start with simple case, iterate |
| Test suite needs major refactor | Medium | Medium | Use TDD for new code |
| LLM response format changes | Low | Medium | Add robust parsing, retry logic |
| Database schema needs changes | Low | Medium | Use migrations, test thoroughly |
| Performance issues emerge | Low | Medium | Profile early, optimize iteratively |

---

## 📞 NEXT STEPS

1. **Approve this roadmap**
2. **Assign Phase 1 tasks to developer**
3. **Set 2-3 day deadline for Phase 1**
4. **Daily standups during Phase 1**
5. **Code review after each task**
6. **Test thoroughly before Phase 2**

