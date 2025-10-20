# Stabilization & Frontend Development Plan

## 🎯 Overview

**Phase**: Stabilization + Frontend MVP  
**Duration**: 2-3 weeks  
**Approach**: Test-Driven Development (TDD)  
**SWE Spec Compliance**: Maintain 95%+ compliance  

---

## 📋 Phase 1: Stabilization (Week 1)

### Task 1.1: Remove Stubs & Placeholders

**Files to Fix**:
- `src/cli/main.py` (lines 810-812, 1035-1040, 506-520)
- `src/agents/stage1_business_translation.py` - Remove mock implementations
- `src/agents/stage2_agent.py` through `stage5_agent.py` - Verify real LLM usage
- `src/database/repositories/*` - Complete all CRUD operations

**TDD Approach**:
1. Write tests for each CLI command (delete, status)
2. Implement the commands
3. Verify tests pass
4. Remove placeholder messages

**Acceptance Criteria**:
- [ ] All CLI commands fully implemented
- [ ] No "Coming in Phase 2" messages
- [ ] All stage agents use real LLM (not mocks)
- [ ] All database operations tested
- [ ] Tests pass: `pytest tests/test_cli.py -v`

**Estimated Effort**: 8-12 hours

---

### Task 1.2: Fix Async/Await Issues

**Issues Found**:
- Coroutine not awaited in consistency checker (line 321)
- Deprecation warning in datetime handling

**TDD Approach**:
1. Write test that reproduces the issue
2. Fix the async/await handling
3. Verify test passes
4. Run full test suite

**Acceptance Criteria**:
- [ ] No runtime warnings
- [ ] All tests pass
- [ ] No deprecation warnings

**Estimated Effort**: 2-4 hours

---

### Task 1.3: Verify Database Operations

**Tests Needed**:
- [ ] Session CRUD operations
- [ ] Checkpoint save/load
- [ ] Stage data persistence
- [ ] Charter export

**TDD Approach**:
1. Write integration tests for each operation
2. Run against real PostgreSQL
3. Verify data integrity
4. Test error scenarios

**Acceptance Criteria**:
- [ ] All database operations tested
- [ ] Tests pass: `pytest tests/test_database.py -v`
- [ ] Data integrity verified

**Estimated Effort**: 6-8 hours

---

## 🎨 Phase 2: Frontend MVP (Week 2-3)

### Task 2.1: Project Setup

**Stack**:
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Vitest (testing)
- React Query (data fetching)

**Setup Steps**:
```bash
npm create vite@latest uaip-frontend -- --template react-ts
cd uaip-frontend
npm install
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install react-query axios
```

**TDD Approach**:
1. Write test for component structure
2. Create component
3. Verify test passes

**Acceptance Criteria**:
- [ ] Project created with all dependencies
- [ ] Build works: `npm run build`
- [ ] Tests run: `npm run test`
- [ ] Dev server starts: `npm run dev`

**Estimated Effort**: 2-3 hours

---

### Task 2.2: Questionnaire UI Components

**Components to Build** (TDD):

1. **QuestionnaireContainer**
   - Test: Renders all 5 stages
   - Test: Tracks current stage
   - Test: Handles stage navigation

2. **StageComponent** (Generic)
   - Test: Displays questions
   - Test: Collects responses
   - Test: Validates input
   - Test: Handles next/previous

3. **Stage1Component** (Business Translation)
   - Test: Asks 4 question groups
   - Test: Validates responses
   - Test: Generates problem statement

4. **Stage2Component** (Value Quantification)
   - Test: Asks about metrics
   - Test: Validates metric definitions
   - Test: Generates alignment matrix

5. **Stage3Component** (Data Feasibility)
   - Test: Asks about data sources
   - Test: Validates data availability
   - Test: Generates feasibility report

6. **Stage4Component** (User Centricity)
   - Test: Asks about users
   - Test: Validates user context
   - Test: Generates user report

7. **Stage5Component** (Ethical Governance)
   - Test: Asks about ethics
   - Test: Validates governance
   - Test: Generates ethics report

**TDD Approach**:
1. Write test for component
2. Implement component
3. Verify test passes
4. Move to next component

**Acceptance Criteria**:
- [ ] All 5 stage components built
- [ ] All tests passing: `npm run test`
- [ ] Components render correctly
- [ ] User can navigate between stages

**Estimated Effort**: 16-20 hours

---

### Task 2.3: Session Management UI

**Components**:
1. **SessionDashboard**
   - Test: Lists all sessions
   - Test: Shows session status
   - Test: Allows session selection

2. **SessionDetail**
   - Test: Shows session progress
   - Test: Displays stage data
   - Test: Shows charter preview

3. **ExportModal**
   - Test: Offers export formats (PDF, JSON, Markdown)
   - Test: Handles export action
   - Test: Shows success message

**TDD Approach**:
1. Write test for each component
2. Implement component
3. Verify test passes

**Acceptance Criteria**:
- [ ] All session components built
- [ ] All tests passing
- [ ] User can view sessions
- [ ] User can export charters

**Estimated Effort**: 8-10 hours

---

### Task 2.4: API Integration

**Backend API Endpoints Needed**:
```
POST   /api/sessions              - Create session
GET    /api/sessions              - List sessions
GET    /api/sessions/{id}         - Get session details
POST   /api/sessions/{id}/stages/{n}  - Run stage
GET    /api/sessions/{id}/charter - Get charter
POST   /api/sessions/{id}/export  - Export charter
```

**TDD Approach**:
1. Write test for API call
2. Implement API integration
3. Mock API responses in tests
4. Verify tests pass

**Acceptance Criteria**:
- [ ] All API endpoints integrated
- [ ] API calls tested with mocks
- [ ] Error handling implemented
- [ ] Loading states working

**Estimated Effort**: 6-8 hours

---

## 🧪 Testing Strategy

### Unit Tests
- Component rendering
- User interactions
- State management
- API calls (mocked)

### Integration Tests
- Multi-stage flow
- Session persistence
- Data flow between components

### E2E Tests
- Complete questionnaire flow
- Session creation to charter export
- Error scenarios

---

## 📊 SWE Spec Compliance Checklist

- [ ] All components have TypeScript types
- [ ] All functions have JSDoc comments
- [ ] All tests follow naming convention
- [ ] Error handling implemented
- [ ] Loading states implemented
- [ ] Accessibility (a11y) considered
- [ ] Mobile responsive design
- [ ] Performance optimized

---

## 🚀 Deployment

### Frontend Deployment
```bash
npm run build
# Deploy dist/ to Vercel/Netlify/AWS S3
```

### Backend Integration
- FastAPI endpoints for session management
- Database persistence
- Charter generation

---

## 📅 Timeline

| Week | Task | Hours | Status |
|------|------|-------|--------|
| 1 | Stabilization | 16-24 | Not Started |
| 2 | Frontend Setup + Components | 22-30 | Not Started |
| 3 | Session UI + Integration | 14-18 | Not Started |

**Total**: 52-72 hours (2-3 weeks)

---

## ✅ Success Criteria

- [ ] All 52 existing tests still passing
- [ ] Stabilization tasks complete
- [ ] Frontend MVP deployed
- [ ] User can run complete questionnaire via web UI
- [ ] Charter can be exported
- [ ] SWE spec compliance maintained at 95%+

---

Generated: October 20, 2025

