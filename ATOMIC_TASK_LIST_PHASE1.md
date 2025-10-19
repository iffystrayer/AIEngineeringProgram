# Phase 1: Atomic Task List for Critical Blockers
**Date:** October 19, 2025 | **Approach:** Test-Driven Development (TDD) | **SWE Spec Alignment:** Strict

---

## 📋 TASK STRUCTURE

Each task follows this pattern:
1. **SWE Spec Reference** - Which requirement(s) this addresses
2. **Test First** - Write failing test
3. **Implementation** - Make test pass
4. **Regression Check** - Verify no breakage
5. **Acceptance Criteria** - How to verify completion

---

## 🎯 BLOCKER 1: Wire Orchestrator to Database (FR-1, FR-8)

### Task 1.1: Implement Agent Registry Initialization
**SWE Spec:** FR-1.1, FR-1.2, Section 7.1 (Orchestrator Agent)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
def test_orchestrator_initializes_all_stage_agents():
    """Verify all 5 stage agents are instantiated and registered"""
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    
    assert len(orchestrator.stage_agents) == 5
    assert 1 in orchestrator.stage_agents
    assert 2 in orchestrator.stage_agents
    assert 3 in orchestrator.stage_agents
    assert 4 in orchestrator.stage_agents
    assert 5 in orchestrator.stage_agents
    
    assert isinstance(orchestrator.stage_agents[1], Stage1Agent)
    assert isinstance(orchestrator.stage_agents[2], Stage2Agent)
    # ... etc

def test_orchestrator_initializes_reflection_agents():
    """Verify all 3 reflection agents are instantiated"""
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    
    assert len(orchestrator.reflection_agents) == 3
    assert 'response_quality' in orchestrator.reflection_agents
    assert 'stage_gate' in orchestrator.reflection_agents
    assert 'consistency' in orchestrator.reflection_agents
```

**Implementation:**
- Replace placeholder `_initialize_agent_registries()` in orchestrator.py
- Instantiate all 5 stage agents with db_pool and llm_router
- Instantiate all 3 reflection agents
- Store in `self.stage_agents` and `self.reflection_agents` dicts

**Regression Check:**
```bash
pytest tests/test_orchestrator.py -v
pytest tests/integration/test_orchestrator_end_to_end.py -v
```

**Acceptance Criteria:**
- ✅ All 5 stage agents registered
- ✅ All 3 reflection agents registered
- ✅ Agents receive db_pool and llm_router
- ✅ No existing tests broken

---

### Task 1.2: Implement Session Persistence on Stage Completion
**SWE Spec:** FR-8.1, Section 7.1 (Session Management)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
@pytest.mark.asyncio
async def test_orchestrator_saves_session_after_stage_completion():
    """Verify session is persisted after each stage completes"""
    session = Session(id=uuid4(), user_id="test_user", status=SessionStatus.IN_PROGRESS)
    mock_session_repo = AsyncMock()
    
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    orchestrator.session_repository = mock_session_repo
    
    # Simulate stage 1 completion
    await orchestrator.complete_stage(stage_num=1, stage_data=mock_stage1_data)
    
    # Verify session was saved
    mock_session_repo.update.assert_called_once()
    call_args = mock_session_repo.update.call_args
    assert call_args[0][0].current_stage == 1
    assert call_args[0][0].status == SessionStatus.IN_PROGRESS
```

**Implementation:**
- Add `session_repository` property to Orchestrator
- Implement `complete_stage()` method that:
  - Calls stage agent
  - Validates stage output
  - Updates session.current_stage
  - Calls `session_repository.update(session)`
  - Returns stage deliverable

**Regression Check:**
```bash
pytest tests/test_orchestrator.py::test_orchestrator_saves_session_after_stage_completion -v
pytest tests/integration/test_database_integration.py -v
```

**Acceptance Criteria:**
- ✅ Session saved after each stage
- ✅ Session.current_stage updated correctly
- ✅ Session.updated_at timestamp updated
- ✅ No data loss on crash

---

### Task 1.3: Implement Session Resume Functionality
**SWE Spec:** FR-8.2, Section 7.1 (Session Resumption)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
@pytest.mark.asyncio
async def test_orchestrator_resumes_session_from_checkpoint():
    """Verify orchestrator can resume from saved checkpoint"""
    session_id = uuid4()
    mock_session_repo = AsyncMock()
    mock_session_repo.get_by_id.return_value = Session(
        id=session_id,
        user_id="test_user",
        current_stage=2,
        status=SessionStatus.IN_PROGRESS,
        stage_data={1: mock_stage1_data}
    )
    
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    orchestrator.session_repository = mock_session_repo
    
    resumed_session = await orchestrator.resume_session(session_id)
    
    assert resumed_session.id == session_id
    assert resumed_session.current_stage == 2
    assert 1 in resumed_session.stage_data
```

**Implementation:**
- Implement `resume_session(session_id)` method
- Load session from repository
- Validate session state
- Return session with all stage data loaded
- Restore conversation context

**Regression Check:**
```bash
pytest tests/test_orchestrator.py::test_orchestrator_resumes_session_from_checkpoint -v
pytest tests/integration/test_e2e_workflow.py -v
```

**Acceptance Criteria:**
- ✅ Session loaded from database
- ✅ All stage data restored
- ✅ Conversation context preserved
- ✅ Can continue from current_stage

---

## 🎯 BLOCKER 2: Integrate Reflection Agents (FR-3, FR-4, FR-5)

### Task 2.1: Wire ResponseQualityAgent into Stage Flow
**SWE Spec:** FR-3.1-FR-3.5, Section 7.2 (Reflection Agents)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
@pytest.mark.asyncio
async def test_orchestrator_validates_response_quality_after_stage_question():
    """Verify ResponseQualityAgent is called after user response"""
    mock_quality_agent = AsyncMock()
    mock_quality_agent.evaluate.return_value = QualityAssessment(
        score=8,
        is_acceptable=True,
        feedback="Good response"
    )
    
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    orchestrator.reflection_agents['response_quality'] = mock_quality_agent
    
    quality = await orchestrator.validate_response_quality(
        stage_num=1,
        question="What is the business problem?",
        response="We need to predict customer churn"
    )
    
    assert quality.score >= 7
    assert quality.is_acceptable is True
    mock_quality_agent.evaluate.assert_called_once()
```

**Implementation:**
- Add `validate_response_quality()` method to Orchestrator
- Call ResponseQualityAgent.evaluate()
- Return QualityAssessment
- Integrate into stage flow (after each user response)

**Regression Check:**
```bash
pytest tests/agents/test_response_quality_agent.py -v
pytest tests/test_orchestrator.py::test_orchestrator_validates_response_quality_after_stage_question -v
```

**Acceptance Criteria:**
- ✅ ResponseQualityAgent called after each response
- ✅ Quality score returned (0-10)
- ✅ Feedback provided for low scores
- ✅ Responses <7 rejected with feedback

---

### Task 2.2: Wire StageGateValidatorAgent into Stage Completion
**SWE Spec:** FR-4.1-FR-4.4, Section 7.2 (Stage Gate Validation)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
@pytest.mark.asyncio
async def test_orchestrator_validates_stage_gate_before_progression():
    """Verify StageGateValidatorAgent blocks progression if validation fails"""
    mock_gate_validator = AsyncMock()
    mock_gate_validator.validate.return_value = StageValidation(
        is_valid=False,
        missing_fields=['problem_statement'],
        errors=['Problem statement is required']
    )
    
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    orchestrator.reflection_agents['stage_gate'] = mock_gate_validator
    
    validation = await orchestrator.validate_stage_gate(
        stage_num=1,
        stage_data=incomplete_stage1_data
    )
    
    assert validation.is_valid is False
    assert 'problem_statement' in validation.missing_fields
```

**Implementation:**
- Add `validate_stage_gate()` method to Orchestrator
- Call StageGateValidatorAgent.validate()
- Return StageValidation result
- Block progression if validation fails
- Provide specific error messages

**Regression Check:**
```bash
pytest tests/agents/test_stage_gate_validator_agent.py -v
pytest tests/test_orchestrator.py::test_orchestrator_validates_stage_gate_before_progression -v
```

**Acceptance Criteria:**
- ✅ Stage gate validation called before progression
- ✅ Missing fields identified
- ✅ Progression blocked if validation fails
- ✅ Clear error messages provided

---

### Task 2.3: Wire ConsistencyCheckerAgent After Stage 5
**SWE Spec:** FR-5.1-FR-5.5, Section 7.2 (Consistency Checking)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
@pytest.mark.asyncio
async def test_orchestrator_checks_cross_stage_consistency_after_stage5():
    """Verify ConsistencyCheckerAgent validates alignment across all stages"""
    mock_consistency_agent = AsyncMock()
    mock_consistency_agent.check.return_value = ConsistencyReport(
        is_consistent=True,
        contradictions=[],
        warnings=[]
    )
    
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    orchestrator.reflection_agents['consistency'] = mock_consistency_agent
    
    report = await orchestrator.check_cross_stage_consistency(
        all_stage_data=complete_stage_data
    )
    
    assert report.is_consistent is True
    mock_consistency_agent.check.assert_called_once()
```

**Implementation:**
- Add `check_cross_stage_consistency()` method
- Call ConsistencyCheckerAgent.check()
- Return ConsistencyReport
- Call after Stage 5 completion
- Flag contradictions for review

**Regression Check:**
```bash
pytest tests/agents/test_consistency_checker_agent.py -v
pytest tests/test_orchestrator.py::test_orchestrator_checks_cross_stage_consistency_after_stage5 -v
```

**Acceptance Criteria:**
- ✅ Consistency check called after Stage 5
- ✅ Cross-stage contradictions identified
- ✅ Warnings provided for logical issues
- ✅ Report included in final charter

---

## 🎯 BLOCKER 3: Complete Charter Generation (FR-7, FR-6)

### Task 3.1: Implement Charter Data Aggregation
**SWE Spec:** FR-7.1-FR-7.5, FR-6.1-FR-6.4, Section 10 (Output Specifications)
**Effort:** 3-4 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
@pytest.mark.asyncio
async def test_orchestrator_aggregates_all_stage_data_into_charter():
    """Verify all stage deliverables aggregated into charter"""
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    
    charter = await orchestrator.generate_charter(
        session_id=uuid4(),
        all_stage_data=complete_stage_data,
        consistency_report=mock_consistency_report,
        ethical_risk_report=mock_ethical_risk_report
    )
    
    assert isinstance(charter, AIProjectCharter)
    assert charter.problem_statement is not None
    assert charter.metric_alignment_matrix is not None
    assert charter.data_quality_scorecard is not None
    assert charter.user_context is not None
    assert charter.ethical_risk_report is not None
    assert charter.governance_decision is not None
```

**Implementation:**
- Implement `generate_charter()` method
- Aggregate all stage deliverables
- Include consistency report
- Include ethical risk assessment
- Determine governance decision
- Return complete AIProjectCharter

**Regression Check:**
```bash
pytest tests/export/test_charter_generator.py -v
pytest tests/test_orchestrator.py::test_orchestrator_aggregates_all_stage_data_into_charter -v
```

**Acceptance Criteria:**
- ✅ All 5 stage deliverables included
- ✅ Consistency report included
- ✅ Ethical risk report included
- ✅ Governance decision determined
- ✅ Charter complete and valid

---

### Task 3.2: Implement Governance Decision Logic
**SWE Spec:** FR-6.2, Section 10.2 (Governance Decisions)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_orchestrator.py - NEW TEST
def test_orchestrator_determines_governance_decision_proceed():
    """Verify PROCEED decision when all risks acceptable"""
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    
    decision = orchestrator.determine_governance_decision(
        ethical_risk_report=EthicalRiskReport(
            residual_risks={'fairness': 0.2, 'transparency': 0.3, ...},
            high_risk_flags=[]
        )
    )
    
    assert decision == GovernanceDecision.PROCEED

def test_orchestrator_determines_governance_decision_halt():
    """Verify HALT decision when critical risks present"""
    orchestrator = Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm)
    
    decision = orchestrator.determine_governance_decision(
        ethical_risk_report=EthicalRiskReport(
            residual_risks={'fairness': 0.9, ...},
            high_risk_flags=['Critical fairness risk']
        )
    )
    
    assert decision == GovernanceDecision.HALT
```

**Implementation:**
- Implement `determine_governance_decision()` method
- Analyze residual risk scores
- Check for high-risk flags
- Return appropriate GovernanceDecision
- Document decision rationale

**Regression Check:**
```bash
pytest tests/test_orchestrator.py::test_orchestrator_determines_governance_decision_* -v
```

**Acceptance Criteria:**
- ✅ PROCEED when all risks <0.5
- ✅ REVISE when some risks 0.5-0.7
- ✅ HALT when any risk >0.8
- ✅ Decision rationale documented

---

## 🎯 BLOCKER 4: Fix CLI Commands (FR-8)

### Task 4.1: Implement Resume Command
**SWE Spec:** FR-8.2, Section 4.2 (CLI Interface)
**Effort:** 2-3 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_cli_resume_command.py - EXISTING, NEEDS UPDATES
@pytest.mark.asyncio
async def test_resume_command_loads_session_and_continues():
    """Verify resume command loads session and continues from current stage"""
    runner = CliRunner()
    
    result = runner.invoke(cli, ['resume', str(session_id)])
    
    assert result.exit_code == 0
    assert 'Resuming session' in result.output
    assert 'Stage 2' in result.output  # Should continue from stage 2
```

**Implementation:**
- Replace placeholder in `src/cli/main.py` resume command
- Load session from database
- Validate session exists and is resumable
- Continue from current_stage
- Restore conversation context

**Regression Check:**
```bash
pytest tests/test_cli_resume_command.py -v
pytest tests/integration/test_e2e_workflow.py -v
```

**Acceptance Criteria:**
- ✅ Resume command functional
- ✅ Session loaded correctly
- ✅ Continues from current_stage
- ✅ Conversation context restored

---

### Task 4.2: Implement List Command
**SWE Spec:** FR-8.3, Section 4.2 (CLI Interface)
**Effort:** 1-2 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_cli_list_command.py - EXISTING, NEEDS UPDATES
def test_list_command_shows_all_user_sessions():
    """Verify list command shows all sessions for user"""
    runner = CliRunner()
    
    result = runner.invoke(cli, ['list'])
    
    assert result.exit_code == 0
    assert 'Session ID' in result.output
    assert 'Status' in result.output
    assert 'Stage' in result.output
```

**Implementation:**
- Replace placeholder in `src/cli/main.py` list command
- Query SessionRepository for user sessions
- Format output as table
- Show session ID, status, current_stage, created_at

**Regression Check:**
```bash
pytest tests/test_cli_list_command.py -v
```

**Acceptance Criteria:**
- ✅ List command functional
- ✅ Shows all user sessions
- ✅ Formatted as readable table
- ✅ Includes session metadata

---

### Task 4.3: Implement Delete Command
**SWE Spec:** FR-8.3, Section 4.2 (CLI Interface)
**Effort:** 1-2 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_cli_main.py - NEW TEST
def test_delete_command_removes_session():
    """Verify delete command removes session"""
    runner = CliRunner()
    
    result = runner.invoke(cli, ['delete', str(session_id)])
    
    assert result.exit_code == 0
    assert 'Session deleted' in result.output
```

**Implementation:**
- Implement delete command in `src/cli/main.py`
- Call SessionRepository.delete()
- Confirm deletion
- Handle not-found errors

**Regression Check:**
```bash
pytest tests/test_cli_main.py::test_delete_command_removes_session -v
```

**Acceptance Criteria:**
- ✅ Delete command functional
- ✅ Session removed from database
- ✅ Confirmation message shown
- ✅ Error handling for missing sessions

---

### Task 4.4: Implement Status Command
**SWE Spec:** FR-8.3, Section 4.2 (CLI Interface)
**Effort:** 1-2 hours
**Status:** NOT_STARTED

**Test First:**
```python
# tests/test_cli_main.py - NEW TEST
def test_status_command_shows_session_details():
    """Verify status command shows detailed session info"""
    runner = CliRunner()
    
    result = runner.invoke(cli, ['status', str(session_id)])
    
    assert result.exit_code == 0
    assert 'Session ID' in result.output
    assert 'Current Stage' in result.output
    assert 'Status' in result.output
```

**Implementation:**
- Implement status command in `src/cli/main.py`
- Load session details
- Show current stage, status, progress
- Show stage deliverables completed

**Regression Check:**
```bash
pytest tests/test_cli_main.py::test_status_command_shows_session_details -v
```

**Acceptance Criteria:**
- ✅ Status command functional
- ✅ Shows session details
- ✅ Shows current stage
- ✅ Shows progress percentage

---

## 📊 REGRESSION TEST SUITE

Run after each task to ensure no breakage:

```bash
# Unit tests for modified components
pytest tests/test_orchestrator.py -v

# Integration tests
pytest tests/integration/test_orchestrator_end_to_end.py -v
pytest tests/integration/test_database_integration.py -v
pytest tests/integration/test_e2e_workflow.py -v

# CLI tests
pytest tests/test_cli_*.py -v

# All tests
pytest tests/ -v --tb=short
```

---

## ✅ PHASE 1 COMPLETION CRITERIA

- ✅ All 12 tasks completed
- ✅ All tests passing (>95% pass rate)
- ✅ No regressions in existing functionality
- ✅ SWE spec compliance: 80%+
- ✅ Code coverage: >80%
- ✅ All critical blockers resolved

---

**Estimated Total Effort:** 18-24 hours (2-3 days)
**Approach:** Test-Driven Development (TDD)
**Quality Gate:** All tests passing + SWE spec compliance verified

