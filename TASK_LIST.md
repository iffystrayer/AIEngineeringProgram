# U-AIP Scoping Assistant - Atomic Task List

**Project:** U-AIP Scoping Assistant v1.0
**Current Phase:** Phase 1 - Foundation (Weeks 1-2)
**Sprint:** Week 1
**Last Updated:** 2025-10-12 16:00

---

## 📊 Progress Overview

**Phase 1 Progress:** 0% (0/25 tasks completed)

```
Foundation Setup:     [░░░░░░░░░░] 0/10 tasks
Database Layer:       [░░░░░░░░░░] 0/8 tasks
CLI Interface:        [░░░░░░░░░░] 0/4 tasks
Docker Setup:         [░░░░░░░░░░] 0/3 tasks
```

---

## 🔄 Active Tasks (In Progress)

*No tasks currently in progress*

---

## ⏳ Pending Tasks (Ready to Start)

### Foundation Setup (F1)

- [ ] **F1.1** - Create project directory structure
  - **Owner:** Unassigned
  - **Dependencies:** None (can start immediately)
  - **Estimated:** 20 min
  - **TDD Required:** No (structure only)
  - **Description:** Create src/, tests/, config/, templates/, scripts/ directories
  - **Acceptance Criteria:**
    - Directory structure matches SWE spec Section 14
    - .gitignore configured
    - README.md with project overview
  - **Blockers:** None

- [ ] **F1.2** - Initialize uv project with pyproject.toml
  - **Owner:** Unassigned
  - **Dependencies:** F1.1
  - **Estimated:** 30 min
  - **TDD Required:** Yes (test imports work)
  - **Description:** Set up Python project with uv, configure dependencies
  - **Acceptance Criteria:**
    - pyproject.toml with all dependencies from SWE spec Section 11.12
    - Virtual environment created
    - Can import project modules
  - **Blockers:** None

- [ ] **F1.3** - Configure development tools (black, ruff, mypy)
  - **Owner:** Unassigned
  - **Dependencies:** F1.2
  - **Estimated:** 20 min
  - **TDD Required:** No (configuration only)
  - **Description:** Set up linting, formatting, type checking configs
  - **Acceptance Criteria:**
    - black.toml, ruff.toml, mypy.ini created
    - All tools run without errors on empty src/
  - **Blockers:** None

- [ ] **F1.4** - Set up pre-commit hooks
  - **Owner:** Unassigned
  - **Dependencies:** F1.3
  - **Estimated:** 25 min
  - **TDD Required:** No (tooling only)
  - **Description:** Configure .pre-commit-config.yaml per PROJECT_WORKFLOW.md
  - **Acceptance Criteria:**
    - Pre-commit hooks installed
    - Hooks run on test commit
    - All checks pass
  - **Blockers:** None

- [ ] **F1.5** - Create pytest configuration
  - **Owner:** Unassigned
  - **Dependencies:** F1.2
  - **Estimated:** 15 min
  - **TDD Required:** No (configuration only)
  - **Description:** Configure pytest.ini with markers, coverage settings
  - **Acceptance Criteria:**
    - pytest.ini matches SWE spec Section 13.5
    - Markers defined (regression, tier1, tier2, tier3)
    - Coverage thresholds set
  - **Blockers:** None

- [ ] **F1.6** - Create quality gate scripts
  - **Owner:** Unassigned
  - **Dependencies:** F1.2, F1.3, F1.5
  - **Estimated:** 30 min
  - **TDD Required:** No (scripts only)
  - **Description:** Create quality-gate-1.sh and quality-gate-3.sh
  - **Acceptance Criteria:**
    - Scripts match PROJECT_WORKFLOW.md Section 7
    - Scripts executable
    - Scripts run without errors (0 tests is OK)
  - **Blockers:** None

- [ ] **F1.7** - Create environment configuration template
  - **Owner:** Unassigned
  - **Dependencies:** F1.1
  - **Estimated:** 15 min
  - **TDD Required:** No (configuration only)
  - **Description:** Create .env.example with all required variables
  - **Acceptance Criteria:**
    - .env.example matches SWE spec Section 14.3
    - All variables documented
    - .env in .gitignore
  - **Blockers:** None

- [ ] **F1.8** - Define core data models (schemas.py)
  - **Owner:** Unassigned
  - **Dependencies:** F1.2
  - **Estimated:** 45 min
  - **TDD Required:** Yes
  - **Description:** Create all dataclasses from SWE spec Section 5.1
  - **Acceptance Criteria:**
    - All enums defined (MLArchetype, RiskLevel, etc.)
    - All dataclasses defined (ProblemStatement, KPI, etc.)
    - Tests verify structure and validation
  - **Blockers:** None

- [ ] **F1.9** - Write specification tests for Orchestrator
  - **Owner:** Unassigned
  - **Dependencies:** F1.2, F1.5
  - **Estimated:** 30 min
  - **TDD Required:** Yes (specification tests always pass)
  - **Description:** Create TestOrchestratorSpecification class
  - **Acceptance Criteria:**
    - tests/test_orchestrator.py created
    - TestOrchestratorSpecification with requirements documented
    - All tests passing (specification tests)
  - **Blockers:** None

- [ ] **F1.10** - Write specification tests for all 5 Stage Agents
  - **Owner:** Unassigned
  - **Dependencies:** F1.2, F1.5
  - **Estimated:** 60 min
  - **TDD Required:** Yes (specification tests always pass)
  - **Description:** Create specification test classes for Stage1-5 agents
  - **Acceptance Criteria:**
    - 5 test files created (test_stage1_agent.py through test_stage5_agent.py)
    - Each has TestSpecification class documenting requirements
    - All specification tests passing
  - **Blockers:** None

### Database Layer (DB)

- [ ] **DB1.1** - Create PostgreSQL schema SQL file
  - **Owner:** Unassigned
  - **Dependencies:** F1.1
  - **Estimated:** 40 min
  - **TDD Required:** Yes (test schema creation)
  - **Description:** Create database/init.sql per SWE spec Section 14.6
  - **Acceptance Criteria:**
    - init.sql with all 5 tables (sessions, stage_data, etc.)
    - Indexes defined
    - Triggers for updated_at columns
  - **Blockers:** None

- [ ] **DB1.2** - Create database connection module
  - **Owner:** Unassigned
  - **Dependencies:** F1.2, F1.8
  - **Estimated:** 45 min
  - **TDD Required:** Yes
  - **Description:** Implement src/database/connection.py with asyncpg pool
  - **Acceptance Criteria:**
    - Connection pool initialization
    - Connection health check
    - Tests verify connection (mock or test DB)
  - **Blockers:** None

- [ ] **DB1.3** - Implement Session CRUD operations
  - **Owner:** Unassigned
  - **Dependencies:** DB1.2
  - **Estimated:** 60 min
  - **TDD Required:** Yes
  - **Description:** Create SessionRepository with create/read/update/delete
  - **Acceptance Criteria:**
    - src/database/repositories/session_repo.py created
    - All CRUD operations implemented
    - Comprehensive tests (10+ tests)
  - **Blockers:** None

- [ ] **DB1.4** - Implement StageData CRUD operations
  - **Owner:** Unassigned
  - **Dependencies:** DB1.2
  - **Estimated:** 50 min
  - **TDD Required:** Yes
  - **Description:** Create StageDataRepository for storing stage responses
  - **Acceptance Criteria:**
    - StageDataRepository implemented
    - Store/retrieve stage data by session and stage number
    - Tests verify JSONB storage
  - **Blockers:** None

- [ ] **DB1.5** - Implement ConversationHistory CRUD operations
  - **Owner:** Unassigned
  - **Dependencies:** DB1.2
  - **Estimated:** 40 min
  - **TDD Required:** Yes
  - **Description:** Create ConversationRepository for logging Q&A
  - **Acceptance Criteria:**
    - ConversationRepository implemented
    - Append messages, retrieve by session
    - Tests verify message ordering
  - **Blockers:** None

- [ ] **DB1.6** - Implement Checkpoint CRUD operations
  - **Owner:** Unassigned
  - **Dependencies:** DB1.2
  - **Estimated:** 40 min
  - **TDD Required:** Yes
  - **Description:** Create CheckpointRepository for stage checkpoints
  - **Acceptance Criteria:**
    - CheckpointRepository implemented
    - Save/restore checkpoints
    - Tests verify data snapshot storage
  - **Blockers:** None

- [ ] **DB1.7** - Implement Charter CRUD operations
  - **Owner:** Unassigned
  - **Dependencies:** DB1.2
  - **Estimated:** 35 min
  - **TDD Required:** Yes
  - **Description:** Create CharterRepository for final charter storage
  - **Acceptance Criteria:**
    - CharterRepository implemented
    - Store charter with file paths
    - Tests verify governance decision storage
  - **Blockers:** None

- [ ] **DB1.8** - Integration test: Database layer end-to-end
  - **Owner:** Unassigned
  - **Dependencies:** DB1.3, DB1.4, DB1.5, DB1.6, DB1.7
  - **Estimated:** 45 min
  - **TDD Required:** Yes
  - **Description:** Test complete session workflow through database
  - **Acceptance Criteria:**
    - E2E test simulates session creation → stage data → checkpoint → charter
    - All repositories work together
    - Test in tests/integration/
  - **Blockers:** None

### CLI Interface (CLI)

- [ ] **CLI1.1** - Create basic CLI entry point
  - **Owner:** Unassigned
  - **Dependencies:** F1.2
  - **Estimated:** 30 min
  - **TDD Required:** Yes
  - **Description:** Implement src/cli/main.py with Click/Typer
  - **Acceptance Criteria:**
    - python -m src.cli.main --help works
    - Basic commands defined (start, resume, list)
    - Tests verify CLI loads
  - **Blockers:** None

- [ ] **CLI1.2** - Implement session start command
  - **Owner:** Unassigned
  - **Dependencies:** CLI1.1, DB1.3
  - **Estimated:** 40 min
  - **TDD Required:** Yes
  - **Description:** Implement 'start' command to begin new session
  - **Acceptance Criteria:**
    - python -m src.cli.main start prompts for project name
    - Creates session in database
    - Tests verify session creation
  - **Blockers:** None

- [ ] **CLI1.3** - Implement session resume command
  - **Owner:** Unassigned
  - **Dependencies:** CLI1.1, DB1.3
  - **Estimated:** 35 min
  - **TDD Required:** Yes
  - **Description:** Implement 'resume' command to continue session
  - **Acceptance Criteria:**
    - python -m src.cli.main resume <session-id> loads session
    - Retrieves session from database
    - Tests verify session loading
  - **Blockers:** None

- [ ] **CLI1.4** - Implement session list command
  - **Owner:** Unassigned
  - **Dependencies:** CLI1.1, DB1.3
  - **Estimated:** 25 min
  - **TDD Required:** Yes
  - **Description:** Implement 'list' command to show user's sessions
  - **Acceptance Criteria:**
    - python -m src.cli.main list shows sessions
    - Displays session status, progress
    - Tests verify listing
  - **Blockers:** None

### Docker Setup (DOC)

- [ ] **DOC1.1** - Create Dockerfile
  - **Owner:** Unassigned
  - **Dependencies:** F1.2
  - **Estimated:** 30 min
  - **TDD Required:** No (Docker build is the test)
  - **Description:** Create multi-stage Dockerfile per SWE spec Section 14.2
  - **Acceptance Criteria:**
    - Dockerfile builds successfully
    - Image size <500MB
    - Health check configured
  - **Blockers:** None

- [ ] **DOC1.2** - Create docker-compose.yml
  - **Owner:** Unassigned
  - **Dependencies:** DOC1.1, DB1.1
  - **Estimated:** 40 min
  - **TDD Required:** No (compose up is the test)
  - **Description:** Configure docker-compose per SWE spec Section 14.1
  - **Acceptance Criteria:**
    - docker-compose.yml with postgres + app services
    - Uses 5-digit ports (15432, 18000, 18080)
    - Services start successfully
  - **Blockers:** None

- [ ] **DOC1.3** - Verify Docker health checks and connectivity
  - **Owner:** Unassigned
  - **Dependencies:** DOC1.2, DB1.2
  - **Estimated:** 30 min
  - **TDD Required:** Yes (integration test)
  - **Description:** Test that app container can connect to DB container
  - **Acceptance Criteria:**
    - docker compose up -d starts all services
    - Health checks pass
    - App can query database
  - **Blockers:** None

---

## ✅ Completed Tasks

*No tasks completed yet*

---

## 🚫 Blocked Tasks

*No blocked tasks*

---

## 📈 Velocity Tracking

### Target Velocity
- **Week 1 Goal:** Complete 12-15 tasks (Foundation + Database)
- **Week 2 Goal:** Complete remaining Phase 1 tasks (CLI + Docker + Integration)

### Actual Velocity
- **Completed Today:** 0 tasks
- **Completed This Week:** 0 tasks

---

## 🎯 Next Steps

**Immediate Actions:**
1. Assign owner to F1.1 (Create project directory structure)
2. Begin Phase 1 work following TDD methodology
3. Commit after each completed task
4. Update this task list frequently

**To Start Work:**
```bash
# Choose a task (e.g., F1.1)
# Update this file: Change "Owner: Unassigned" → "Owner: Your Name"
# Update status: Move task to "Active Tasks" section
# Create feature branch
git checkout -b feature/phase1-F1.1-project-structure
# Begin work (TDD if applicable)
```

---

## 📝 Notes

- All tasks follow atomic task definition (30-90 min each)
- TDD required for all code implementation tasks
- Configuration/setup tasks don't require TDD but must be verified
- Checkpoint after EVERY completed task (no exceptions)
- Run quality gate 1 before requesting code review

---

**Last Updated:** 2025-10-12 16:00
**Next Review:** 2025-10-13 09:00 (daily standup)
