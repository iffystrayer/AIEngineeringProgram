# Detailed Technical Findings & Code References

## 🔴 CRITICAL ISSUE #1: Orchestrator Not Wired to Database

### Location
`src/agents/orchestrator.py` lines 76-100, 200-250

### Problem
```python
def __init__(self, db_pool, llm_router=None, config=None):
    self.db_pool = db_pool
    self.llm_router = llm_router
    self.config = config or {}
    
    # Agent registries - will be populated when agents are implemented
    self.stage_agents: dict[int, Any] = {}
    self.reflection_agents: dict[str, Any] = {}
    
    # Initialize registries (placeholder until agents exist)
    self._initialize_agent_registries()  # ← EMPTY STUB!
```

The `_initialize_agent_registries()` method (lines 99-150) is a placeholder that doesn't actually instantiate agents.

### Impact
- `run_stage()` method (lines 200-250) can't execute stages
- Session data never persisted to database
- Resume functionality impossible
- Charter generation incomplete

### Fix Required
```python
def _initialize_agent_registries(self):
    """Initialize all stage agents and reflection agents."""
    self.stage_agents = {
        1: Stage1Agent(llm_router=self.llm_router),
        2: Stage2Agent(llm_router=self.llm_router),
        3: Stage3Agent(llm_router=self.llm_router),
        4: Stage4Agent(llm_router=self.llm_router),
        5: Stage5Agent(llm_router=self.llm_router),
    }
    self.reflection_agents = {
        'quality': ResponseQualityAgent(llm_router=self.llm_router),
        'consistency': ConsistencyCheckerAgent(llm_router=self.llm_router),
        'gate': StageGateValidatorAgent(llm_router=self.llm_router),
    }
```

---

## 🔴 CRITICAL ISSUE #2: CLI Resume/List Commands Are Stubs

### Location
`src/cli/main.py` lines 494-520 (resume), 664-677 (list)

### Problem
```python
# In resume_command (line 494-520):
console.print("\n[cyan]Next Steps:[/cyan]")
console.print(
    f"  1. [dim]Initialize Stage {session.current_stage} Agent[/dim] "
    f"[yellow]→ Coming in Phase 2[/yellow]"  # ← PLACEHOLDER!
)
console.print(
    "  2. [dim]Resume interactive conversation[/dim] "
    "[yellow]→ Coming in Phase 2[/yellow]"  # ← PLACEHOLDER!
)
```

### Impact
- Users can't actually resume sessions
- List command doesn't filter properly
- Delete command is non-functional
- Status command is empty

### Fix Required
Replace placeholder logic with actual orchestrator calls:
```python
# In _resume_session_async:
orchestrator = Orchestrator(db_pool=db_manager.pool, llm_router=llm_router)
orchestrator.active_sessions[session.session_id] = session

# Continue from current stage
for stage_num in range(session.current_stage, 6):
    stage_output = await orchestrator.run_stage(session, stage_num)
    # ... persist and advance
```

---

## 🔴 CRITICAL ISSUE #3: Database Repositories Orphaned

### Location
`src/database/repositories/` - all files exist but unused

### Problem
- SessionRepository fully implemented (740 lines)
- CharterRepository fully implemented (400+ lines)
- But Orchestrator never calls them!
- Session data never persisted

### Evidence
Orchestrator methods that should use repositories:
- `_persist_session()` - never called
- `_load_session_from_db()` - never called
- `_save_checkpoint()` - never called

### Fix Required
In `orchestrator.py`, replace placeholder methods with actual repository calls:
```python
async def _persist_session(self, session: Session) -> None:
    """Persist session to database."""
    session_repo = SessionRepository(self.db_pool)
    await session_repo.update(session)
```

---

## 🟡 MEDIUM ISSUE #1: Charter Generation Incomplete

### Location
`src/agents/orchestrator.py` lines 700-750

### Problem
```python
async def generate_charter(self, session: Session) -> AIProjectCharter:
    """Generate final AI Project Charter."""
    # ← Missing implementation!
    # - Doesn't aggregate stage data
    # - No governance decision logic
    # - No residual risk calculation
```

### Impact
- Export command fails
- No charter document generated
- Governance decision missing

### Fix Required
Implement full charter generation with:
1. Aggregate all 5 stage outputs
2. Calculate governance decision (PROCEED/REVISE/HALT)
3. Compute residual risk scores
4. Generate narrative sections

---

## 🟡 MEDIUM ISSUE #2: ResponseQualityAgent JSON Parsing Fragile

### Location
`src/agents/reflection/response_quality_agent.py` lines 215-227

### Problem
Recently fixed with bracket-counting algorithm, but still vulnerable:
- Assumes LLM returns valid JSON
- No retry logic on parse failure
- Fallback to score 0/10 is harsh

### Evidence
From FIX_SUMMARY.md:
```
Failed to parse JSON from LLM response: Extra data: line 10 column 1
LLM response missing quality_score, using default
Score: 0/10
```

### Fix Required
Add retry logic and better error handling:
```python
async def evaluate_response(self, response: str, context: str) -> QualityAssessment:
    for attempt in range(3):
        try:
            # ... LLM call
            return self._parse_quality_assessment(llm_response)
        except JSONDecodeError:
            if attempt < 2:
                await asyncio.sleep(1)  # Retry
                continue
            # Fallback: return conservative assessment
            return QualityAssessment(quality_score=5, issues=["Unable to parse response"])
```

---

## 🟡 MEDIUM ISSUE #3: Test Suite Unstable

### Location
`tests/agents/test_response_quality_agent.py` - 25+ failures

### Problem
```
test_excellent_response_scores_9_to_10 FAILED
test_good_response_scores_7_to_8 FAILED
test_needs_improvement_response_scores_5_to_6 FAILED
...
```

### Root Cause
- Mock LLM responses don't match real behavior
- JSON parsing tests fail due to format variations
- Event loop conflicts in async tests

### Fix Required
1. Update mocks to match actual LLM response format
2. Add real LLM integration tests (marked as slow)
3. Fix async test fixtures

---

## 🟠 MINOR ISSUE #1: Inconsistent Naming

### Location
`src/agents/` directory

### Problem
```
stage1_business_translation.py  ← snake_case with full name
stage2_agent.py                 ← snake_case with "agent"
stage3_agent.py                 ← inconsistent
stage4_agent.py                 ← inconsistent
stage5_agent.py                 ← inconsistent
```

### Fix
Rename to consistent pattern:
```
stage1_business_translation_agent.py
stage2_value_quantification_agent.py
stage3_data_feasibility_agent.py
stage4_user_centricity_agent.py
stage5_ethical_governance_agent.py
```

---

## 🟠 MINOR ISSUE #2: Missing Error Handling

### Location
`src/cli/main.py` lines 163-190 (database connection)

### Problem
```python
try:
    await db_manager.initialize()
except Exception as e:
    console.print(f"[dim]Details: {e}[/dim]")
    # ← Generic exception handling, no specific recovery
```

### Fix
Add specific exception handling:
```python
except asyncpg.InvalidCatalogNameError:
    console.print("Database does not exist. Run: docker compose up -d")
except asyncpg.CannotConnectNowError:
    console.print("PostgreSQL not running. Run: docker compose up -d uaip-db")
except asyncpg.AuthenticationFailedError:
    console.print("Invalid database credentials. Check .env file")
```

---

## 📊 SUMMARY OF FINDINGS

| Issue | Severity | Location | Lines | Fix Time |
|-------|----------|----------|-------|----------|
| Orchestrator not wired | 🔴 CRITICAL | orchestrator.py | 76-250 | 4-6h |
| CLI stubs | 🔴 CRITICAL | main.py | 494-520 | 2-3h |
| Repos orphaned | 🔴 CRITICAL | orchestrator.py | 700+ | 3-4h |
| Charter generation | 🟡 MEDIUM | orchestrator.py | 700-750 | 3-4h |
| JSON parsing | 🟡 MEDIUM | response_quality_agent.py | 215-227 | 2-3h |
| Test failures | 🟡 MEDIUM | test_response_quality_agent.py | all | 2-3h |
| Naming inconsistency | 🟠 MINOR | src/agents/ | all | 1h |
| Error handling | 🟠 MINOR | main.py | 163-190 | 1h |

**Total Fix Time: 18-24 hours (2-3 days)**

