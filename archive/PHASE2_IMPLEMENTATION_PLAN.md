# Phase 2 Implementation Plan - Advanced Features

**Branch**: `phase2/advanced-features`  
**Status**: 🟢 **READY TO START**  
**Duration**: 2-3 weeks  
**Target**: 95%+ SWE Spec Compliance  
**Expected Tests**: 45+ passing

---

## 🎯 Phase 2 Objectives

### Primary Goals

1. **Stage Agent Mocking** (7 tests)
   - Implement mock stage agents for interactive testing
   - Mock user input handling
   - Mock stage data generation

2. **LLM Router Configuration** (3 tests)
   - Proper mock LLM router setup
   - JSON response formatting
   - Model selection logic

3. **Phase 2 Model Enhancements** (6 tests)
   - Add missing model fields
   - Implement data validation
   - Add checkpoint integrity checking

### Secondary Goals

- Achieve 95%+ SWE spec compliance
- Maintain 100% test pass rate
- Improve code coverage
- Full integration testing

---

## 📋 Detailed Task Breakdown

### Task Group 1: Stage Agent Mocking (7 tests)

**Tests to Enable**:
- `test_orchestrator_stage1_agent_integration`
- `test_orchestrator_routes_to_correct_stage_agent`
- `test_orchestrator_passes_context_between_agents`
- `test_orchestrator_handles_agent_communication_failure`
- `test_save_checkpoint_after_stage_completion`
- `test_checkpoint_preserves_stage_validation_results`
- Plus 1 additional integration test

**Implementation Steps**:

1. **Create Mock Stage Agent Factory**
   - Location: `src/agents/mocks/mock_stage_agents.py`
   - Implement MockStage1Agent through MockStage5Agent
   - Mock `run_stage()` method
   - Mock user input handling

2. **Mock User Input Handler**
   - Location: `src/agents/mocks/mock_input_handler.py`
   - Mock `ask_user_question()` function
   - Return predefined responses
   - Track question history

3. **Update Orchestrator Tests**
   - Replace `pytest.skip()` with actual test logic
   - Use mock stage agents
   - Verify stage progression
   - Verify context passing

**Estimated Time**: 6-8 hours

---

### Task Group 2: LLM Router Configuration (3 tests)

**Tests to Enable**:
- `test_quality_loop_integration`
- `test_orchestrator_invokes_quality_agent_after_response`
- `test_orchestrator_invokes_stage_gate_before_progression`

**Implementation Steps**:

1. **Create Mock LLM Router**
   - Location: `src/llm/mocks/mock_router.py`
   - Mock `route_request()` method
   - Return predefined JSON responses
   - Support multiple model types

2. **Mock Response Formatting**
   - Implement JSON response templates
   - Mock quality assessment responses
   - Mock validation responses
   - Mock consistency check responses

3. **Update Quality Agent Tests**
   - Replace `pytest.skip()` with actual test logic
   - Use mock LLM router
   - Verify quality loop logic
   - Verify agent invocation

**Estimated Time**: 4-6 hours

---

### Task Group 3: Model Enhancements (6 tests)

**Tests to Enable**:
- `test_checkpoint_data_integrity_validation`
- `test_get_session_state_returns_current_progress`
- Plus 4 additional model-related tests

**Implementation Steps**:

1. **Enhance Session Model**
   - Add `progress_percentage` field
   - Add `data_hash` field for integrity
   - Add validation methods
   - Update `src/models/schemas.py`

2. **Enhance Checkpoint Model**
   - Add `checksum` field
   - Add integrity validation
   - Add `cross_stage_issues` tracking
   - Update checkpoint repository

3. **Add Data Validation**
   - Implement hash calculation
   - Implement checksum validation
   - Add integrity checks on load
   - Add error handling

**Estimated Time**: 5-7 hours

---

## 🧪 Test Execution Strategy

### Phase 2A: Stage Agent Mocking (Week 1)

1. Create mock stage agent infrastructure
2. Enable 7 stage-related tests
3. Verify all tests passing
4. Commit changes

### Phase 2B: LLM Router Configuration (Week 1-2)

1. Create mock LLM router
2. Enable 3 quality/validation tests
3. Verify all tests passing
4. Commit changes

### Phase 2C: Model Enhancements (Week 2-3)

1. Enhance data models
2. Enable 6 model-related tests
3. Verify all tests passing
4. Final verification

### Final Verification (Week 3)

1. Run full test suite
2. Verify 45+ tests passing
3. Check SWE spec compliance
4. Prepare for merge to main

---

## 📊 Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Tests Passing | 45+ | ⏳ In Progress |
| Tests Failing | 0 | ⏳ In Progress |
| SWE Compliance | 95%+ | ⏳ In Progress |
| Code Coverage | 40%+ | ⏳ In Progress |
| All Blockers | Complete | ✅ Done |

---

## 📁 Files to Create/Modify

### New Files

- `src/agents/mocks/mock_stage_agents.py` - Mock stage agents
- `src/agents/mocks/mock_input_handler.py` - Mock user input
- `src/llm/mocks/mock_router.py` - Mock LLM router
- `src/llm/mocks/mock_responses.py` - Mock response templates

### Modified Files

- `src/models/schemas.py` - Add new fields
- `tests/test_orchestrator.py` - Enable skipped tests
- `src/database/repositories/checkpoint_repository.py` - Add validation

---

## 🚀 Getting Started

### Prerequisites

- ✅ Phase 1 complete and committed
- ✅ New branch created: `phase2/advanced-features`
- ✅ All Phase 1 tests passing

### First Steps

1. Review this plan
2. Create mock infrastructure
3. Enable first batch of tests
4. Run tests and iterate

---

## 📞 Notes

- All Phase 1 code remains unchanged
- Phase 2 is additive (no breaking changes)
- Easy rollback to Phase 1 if needed
- Merge to main after all tests pass

**Status**: 🟢 **READY TO BEGIN PHASE 2**

