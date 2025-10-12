# U-AIP Scoping Assistant: Project Workflow & Standards

**Project:** U-AIP Scoping Assistant
**Version:** 1.0.0
**Document Type:** Mandatory Development Standards
**Status:** ACTIVE - All contributors must follow these rules

---

## 📋 Table of Contents

1. [Core Principles](#core-principles)
2. [Atomic Task List Management](#atomic-task-list-management)
3. [Test-Driven Development (TDD) Rules](#test-driven-development-tdd-rules)
4. [Checkpoint & Commit Strategy](#checkpoint--commit-strategy)
5. [Code Review Process](#code-review-process)
6. [Vulnerability Testing](#vulnerability-testing)
7. [Regression Testing](#regression-testing)
8. [Quality Gates](#quality-gates)
9. [Workflow Enforcement](#workflow-enforcement)
10. [Tools & Automation](#tools--automation)

---

## Core Principles

### The Five Pillars of Quality

```
┌─────────────────────────────────────────────────────────────┐
│  1. ATOMIC TASKS    - Break work into smallest units        │
│  2. TEST FIRST      - Write tests before implementation     │
│  3. CHECKPOINT OFTEN - Commit early, commit frequently      │
│  4. PEER REVIEW     - No code merges without review         │
│  5. CONTINUOUS TEST - Regression & vulnerability checks     │
└─────────────────────────────────────────────────────────────┘
```

**Violations of these principles are NOT acceptable.**

---

## 1. Atomic Task List Management

### 1.1 What is an Atomic Task?

An **atomic task** is the smallest unit of work that:
- ✅ Can be completed in one focused session (30-90 minutes)
- ✅ Has a single, clear objective
- ✅ Produces a testable outcome
- ✅ Can be verified independently
- ✅ Does NOT depend on incomplete parallel work

**Examples:**

✅ **GOOD (Atomic):**
- "Write Stage1Agent.ask_question() method with tests"
- "Implement response quality scoring algorithm"
- "Create PostgreSQL sessions table schema"
- "Add Docker Compose health check for database"

❌ **BAD (Too Large):**
- "Implement Stage 1 agent" (too broad - break into 10+ atomic tasks)
- "Build reflection system" (too vague - what specifically?)
- "Set up infrastructure" (multiple unrelated tasks)

### 1.2 Task List File

**Location:** `TASK_LIST.md` (root directory)

**Format:**
```markdown
# U-AIP Scoping Assistant - Atomic Task List

**Current Phase:** Phase 1 - Foundation
**Sprint:** Week 1
**Last Updated:** 2025-10-12

## Active Tasks (In Progress)

- [ ] Task ID: F1.1 - Create project directory structure
  - Owner: Developer A
  - Started: 2025-10-12 10:00
  - Estimated: 30 min
  - Status: IN_PROGRESS
  - Blockers: None

## Pending Tasks (Ready to Start)

- [ ] Task ID: F1.2 - Initialize uv project with pyproject.toml
  - Dependencies: F1.1 (must complete first)
  - Estimated: 20 min
  - TDD Required: Yes (test import structure)

- [ ] Task ID: F1.3 - Create PostgreSQL schema (sessions table)
  - Dependencies: F1.2
  - Estimated: 45 min
  - TDD Required: Yes (test table creation, constraints)

## Completed Tasks

- [x] Task ID: F1.0 - Write SWE Specification
  - Completed: 2025-10-12 15:30
  - Commit: abc123
  - Tests Passing: N/A (documentation)
```

### 1.3 Task Lifecycle

```
[PENDING] → [IN_PROGRESS] → [TESTING] → [REVIEW] → [COMPLETED]
               ↓                ↓            ↓
           [BLOCKED]       [FAILED]    [REVISIONS]
```

**State Definitions:**

| State | Meaning | Actions Required |
|-------|---------|-----------------|
| **PENDING** | Ready to start, dependencies met | Assign owner, start work |
| **IN_PROGRESS** | Actively being worked on | Regular status updates (every 30min for long tasks) |
| **TESTING** | Implementation complete, running tests | Fix test failures |
| **REVIEW** | Tests pass, awaiting code review | Address review comments |
| **BLOCKED** | Cannot proceed due to dependency | Identify blocker, escalate if needed |
| **FAILED** | Tests failed or review rejected | Fix issues, return to IN_PROGRESS |
| **REVISIONS** | Review requested changes | Make changes, return to TESTING |
| **COMPLETED** | Merged to main, documented | Archive task, update task list |

### 1.4 Task List Rules

**MANDATORY:**

1. ✅ **Only ONE task in IN_PROGRESS per developer at a time**
   - Prevents context-switching and drift
   - Focus on completing before starting new work

2. ✅ **Update task status within 30 minutes of state change**
   - Keep task list current for team visibility
   - Use commit messages to reference task IDs

3. ✅ **Break large tasks immediately**
   - If task exceeds 90 minutes, STOP and break into sub-tasks
   - Better to have 5 atomic tasks than 1 multi-hour task

4. ✅ **Document blockers immediately**
   - As soon as you're blocked, update task list
   - Tag dependent tasks that are now blocked

5. ✅ **Estimate task duration**
   - Required for every task
   - Track actual vs. estimated to improve future estimates

### 1.5 Task Breakdown Example

**Original (Too Large):**
```markdown
- [ ] Implement Stage1BusinessTranslationAgent
```

**Broken Down (Atomic):**
```markdown
- [ ] S1.1 - Define Stage1Agent interface (methods, properties)
- [ ] S1.2 - Implement question loading from YAML config
- [ ] S1.3 - Implement ask_question() method
- [ ] S1.4 - Implement validate_response() method with quality checks
- [ ] S1.5 - Implement store_response() method (database write)
- [ ] S1.6 - Implement generate_deliverable() - ProblemStatement object
- [ ] S1.7 - Implement ML archetype validator tool
- [ ] S1.8 - Implement feature availability checker tool
- [ ] S1.9 - Write comprehensive test suite (all methods)
- [ ] S1.10 - Integration test with ResponseQualityAgent
```

---

## 2. Test-Driven Development (TDD) Rules

### 2.1 The Iron Law of TDD

**ABSOLUTE REQUIREMENT:**

```
┌────────────────────────────────────────────────────┐
│  NO CODE IS WRITTEN WITHOUT TESTS FIRST           │
│  NO EXCEPTIONS. NO SHORTCUTS. NO EXCUSES.         │
└────────────────────────────────────────────────────┘
```

**This is NOT negotiable.** Any code written without tests first will be rejected in code review.

### 2.2 TDD Workflow (Red-Green-Refactor)

```
1. RED    → Write failing test (component doesn't exist yet)
2. GREEN  → Write minimal code to make test pass
3. REFACTOR → Improve code while keeping tests green
4. REPEAT → Next test
```

**Example:**

```python
# STEP 1: RED - Write test first (fails because method doesn't exist)
def test_orchestrator_initializes_session():
    """Test orchestrator creates new session with valid UUID"""
    orchestrator = UAIPOrchestrator()
    session_id = orchestrator.initialize_session(user_id="test_user")

    assert isinstance(session_id, UUID)
    assert len(str(session_id)) == 36

# Run: pytest → FAILS (UAIPOrchestrator doesn't exist)

# STEP 2: GREEN - Implement minimal code
class UAIPOrchestrator:
    def initialize_session(self, user_id: str) -> UUID:
        return uuid4()

# Run: pytest → PASSES

# STEP 3: REFACTOR - Add validation, logging, etc.
class UAIPOrchestrator:
    def initialize_session(self, user_id: str) -> UUID:
        if not user_id:
            raise ValueError("user_id required")
        session_id = uuid4()
        logger.info("session_created", session_id=session_id, user_id=user_id)
        return session_id

# Run: pytest → STILL PASSES (add tests for new validation)
```

### 2.3 TDD Test Structure (Per CLAUDE.md)

**Required Test Classes:**

```python
# tests/test_component.py

class TestComponentSpecification:
    """ALWAYS PASSING - Documents requirements"""
    def test_component_requirements(self):
        """What this component should do"""
        pass

class TestComponentStructure:
    """SKIPPED until implementation - Tests interface"""
    @pytest.mark.skipif(not COMPONENT_AVAILABLE, ...)
    def test_has_required_methods(self):
        pass

class TestComponentExecution:
    """SKIPPED until implementation - Tests functionality"""
    @pytest.mark.skipif(not COMPONENT_AVAILABLE, ...)
    def test_successful_operation(self):
        pass

class TestComponentIntegration:
    """SKIPPED until implementation - Tests with other components"""
    @pytest.mark.skipif(not COMPONENT_AVAILABLE, ...)
    def test_integration_with_database(self):
        pass

class TestComponentErrorHandling:
    """SKIPPED until implementation - Tests error scenarios"""
    @pytest.mark.skipif(not COMPONENT_AVAILABLE, ...)
    def test_handles_invalid_input(self):
        pass
```

### 2.4 Conditional Import Pattern

**MANDATORY for all tests:**

```python
# Conditional import - component may not exist yet
try:
    from src.agents.stage1_agent import Stage1Agent
    COMPONENT_AVAILABLE = True
except ImportError:
    COMPONENT_AVAILABLE = False
    # Placeholder for testing structure
    class Stage1Agent:
        pass

@pytest.fixture
def agent():
    if not COMPONENT_AVAILABLE:
        pytest.skip("Stage1Agent not implemented yet")
    return Stage1Agent()
```

### 2.5 TDD Verification Commands

**Run these commands frequently:**

```bash
# Run all tests
uv run pytest -v

# Run only specification tests (should ALWAYS pass)
uv run pytest -k "Specification" -v

# Run only non-skipped tests (implemented components)
uv run pytest -v --tb=short

# Run with coverage report
uv run pytest --cov=src --cov-report=html --cov-report=term

# Check coverage threshold (minimum 80%)
uv run pytest --cov=src --cov-fail-under=80
```

### 2.6 TDD Quality Gates

**Before marking task as COMPLETED:**

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| All tests pass | `pytest -v` | ✅ 0 failures |
| Coverage ≥80% | `pytest --cov --cov-fail-under=80` | ✅ Threshold met |
| No skipped tests for implemented code | Manual review | ✅ Only unimplemented components skipped |
| Type checking | `mypy src/` | ✅ 0 errors |

---

## 3. Checkpoint & Commit Strategy

### 3.1 The Checkpoint Rule

**MANDATORY:**

```
Commit code to Git after EVERY completed atomic task.
Minimum: Every 60-90 minutes.
Ideal: Every 30-45 minutes.
```

**Why:**
- ✅ Prevents drift from specification
- ✅ Creates restore points if approach fails
- ✅ Enables easy rollback
- ✅ Provides progress visibility
- ✅ Facilitates code review (small diffs)

### 3.2 Checkpoint Types

#### Type 1: Task Completion Checkpoint (Primary)

**When:** Immediately after completing an atomic task

**Requirements:**
- ✅ All tests for this task pass
- ✅ Task marked as COMPLETED in task list
- ✅ Commit message references task ID

**Commit Message Format:**
```bash
git add .
git commit -m "[F1.3] Create PostgreSQL sessions table schema

- Added sessions table with UUID primary key
- Added indexes for user_id and status
- Included database init script
- Tests: test_sessions_table_creation (PASSING)

Task: F1.3
Status: COMPLETED
Tests: 3/3 passing
Coverage: 85%"
```

#### Type 2: Progress Checkpoint (WIP)

**When:** Task in progress for >60 minutes OR end of work session

**Requirements:**
- ⚠️ Tests may be failing (work in progress)
- ✅ Code compiles/imports successfully
- ✅ Clear WIP indicator in commit message

**Commit Message Format:**
```bash
git add .
git commit -m "[WIP][F1.5] Implement store_response() method

- Partially implemented database write logic
- TODO: Add transaction handling
- TODO: Add error handling for duplicate keys

Task: F1.5
Status: IN_PROGRESS (60% complete)
Tests: 2/5 passing (3 expected failures)
Next: Complete transaction logic"
```

#### Type 3: Checkpoint Before Refactor

**When:** Before making significant changes to working code

**Requirements:**
- ✅ All tests currently passing
- ✅ Create safety checkpoint before refactoring

**Commit Message Format:**
```bash
git commit -m "[CHECKPOINT] Before refactoring orchestrator session management

All tests passing. Creating checkpoint before restructuring
session initialization to use factory pattern.

Current state: 15 tests, 100% passing"
```

### 3.3 Commit Message Standards

**Format:**
```
[TYPE][TASK_ID] Brief description (max 50 chars)

- Detailed bullet points of changes
- What was added/modified/removed
- Test status and coverage

Task: [TASK_ID]
Status: [COMPLETED/IN_PROGRESS]
Tests: [X passing / Y failing]
Coverage: [percentage]
```

**Types:**
- `[FEAT]` - New feature implementation
- `[TEST]` - Test additions/modifications
- `[FIX]` - Bug fix
- `[REFACTOR]` - Code restructuring (no behavior change)
- `[DOCS]` - Documentation only
- `[CHORE]` - Build, dependencies, config
- `[WIP]` - Work in progress (not ready for review)
- `[CHECKPOINT]` - Safety checkpoint before major change

### 3.4 Branch Strategy

**Simple Git Flow:**

```
main (production-ready, protected)
  ↓
develop (integration branch)
  ↓
feature/[phase]-[task-id] (individual features)
```

**Rules:**
1. ✅ **NEVER commit directly to `main`**
2. ✅ **All work happens in feature branches**
3. ✅ Feature branches created from `develop`
4. ✅ Merge to `develop` after code review
5. ✅ Merge to `main` only after phase completion + QA

**Branch Naming:**
```bash
# Format: feature/[phase]-[brief-description]
feature/phase1-orchestrator
feature/phase1-database-schema
feature/phase2-stage1-agent
feature/phase3-reflection-agents
```

**Workflow:**
```bash
# Start new task
git checkout develop
git pull origin develop
git checkout -b feature/phase1-sessions-table

# Work on task, commit frequently
git add .
git commit -m "[F1.3] Create sessions table..."

# Push to remote for backup
git push origin feature/phase1-sessions-table

# When task complete, create pull request
# (Code review process - see section 4)

# After approval, merge to develop
git checkout develop
git merge --no-ff feature/phase1-sessions-table
git push origin develop
```

### 3.5 Checkpoint Frequency Tracking

**Keep a checkpoint log:**

```markdown
# CHECKPOINT_LOG.md

## Week 1 - Phase 1 Checkpoints

| Date | Time | Task | Commit | Tests | Coverage |
|------|------|------|--------|-------|----------|
| 2025-10-12 | 10:30 | F1.1 | abc123 | N/A | N/A |
| 2025-10-12 | 11:45 | F1.2 | def456 | 2/2 | 85% |
| 2025-10-12 | 13:15 | F1.3 | ghi789 | 5/5 | 90% |

**Checkpoint Frequency:** 3 commits in 3 hours = ✅ Good (60min avg)
```

---

## 4. Code Review Process

### 4.1 Code Review Rules

**MANDATORY:**

```
┌────────────────────────────────────────────────────┐
│  NO CODE MERGES TO DEVELOP WITHOUT REVIEW          │
│  Minimum 1 reviewer approval required              │
│  All review comments must be addressed             │
└────────────────────────────────────────────────────┘
```

### 4.2 When Code Review is Required

**ALWAYS:**
- ✅ Before merging feature branch to `develop`
- ✅ Before merging `develop` to `main`
- ✅ For any change touching critical paths (authentication, data storage, API calls)

**OPTIONAL (but recommended):**
- 🟡 WIP checkpoints (informal review for feedback)
- 🟡 Architecture decisions (before implementation)

### 4.3 Code Review Checklist

**Reviewer must verify:**

#### Functionality
- [ ] Code implements task requirements correctly
- [ ] No obvious bugs or logic errors
- [ ] Edge cases are handled
- [ ] Error handling is appropriate

#### Tests
- [ ] Tests were written FIRST (TDD compliance)
- [ ] All tests pass (`pytest -v`)
- [ ] Coverage ≥80% for new code
- [ ] Tests cover happy path, error cases, edge cases
- [ ] No test skips for implemented functionality

#### Code Quality
- [ ] Follows PEP 8 style guidelines (`ruff check`)
- [ ] Type hints present (`mypy` passes)
- [ ] Functions/classes have docstrings
- [ ] Variable names are clear and descriptive
- [ ] No code duplication (DRY principle)
- [ ] Appropriate use of abstractions

#### Security
- [ ] No hardcoded secrets or API keys
- [ ] Input validation present
- [ ] SQL injection prevention (parameterized queries)
- [ ] Sensitive data not logged

#### Documentation
- [ ] Task list updated (task marked COMPLETED)
- [ ] Checkpoint log updated
- [ ] Code comments for complex logic
- [ ] README updated if public interface changed

#### Commit Quality
- [ ] Commit message follows format standards
- [ ] Commit references task ID
- [ ] Atomic commit (single logical change)

### 4.4 Code Review Workflow

```
Developer                    Reviewer
    │                            │
    ├─ 1. Create PR              │
    ├─ 2. Fill PR template       │
    │       (Task ID, tests,     │
    │        coverage, etc.)     │
    │                            │
    │                         ┌──▼────────────────┐
    │                         │ Review code       │
    │                         │ Run tests locally │
    │                         │ Check checklist   │
    │                         └──┬────────────────┘
    │                            │
    ├◄── 3. Feedback ────────────┤
    │       (comments, requests) │
    │                            │
    ├─ 4. Address comments       │
    ├─ 5. Push updates           │
    │                            │
    │                         ┌──▼────────────────┐
    │                         │ Re-review changes │
    │                         └──┬────────────────┘
    │                            │
    ├◄── 6. APPROVED ────────────┤
    │                            │
    ├─ 7. Merge to develop       │
    └─ 8. Delete feature branch  │
```

### 4.5 Pull Request Template

**File: `.github/pull_request_template.md`**

```markdown
## Task Information
- **Task ID:** [e.g., F1.3]
- **Task Description:** [Brief description]
- **Phase:** [e.g., Phase 1 - Foundation]

## Changes Made
- [ ] List specific changes
- [ ] One per line
- [ ] Be detailed

## Testing
- **Tests Added:** [count]
- **Tests Modified:** [count]
- **All Tests Passing:** ✅ Yes / ❌ No
- **Coverage:** [percentage]%

```bash
# Copy/paste test run output
pytest -v --cov=src
```

## TDD Compliance
- [ ] Tests written FIRST before implementation
- [ ] Conditional imports used for components not yet implemented
- [ ] Specification tests are passing
- [ ] Implementation tests pass for completed code

## Checklist
- [ ] Code follows PEP 8 style
- [ ] Type hints added (mypy passes)
- [ ] Docstrings present
- [ ] No hardcoded secrets
- [ ] Task list updated
- [ ] Checkpoint log updated

## Review Focus Areas
[Specific areas where you want reviewer attention]

## Screenshots (if applicable)
[For CLI output, terminal screenshots, etc.]
```

### 4.6 Review Turnaround Time

**Targets:**
- Small PRs (<200 lines): Review within 4 hours
- Medium PRs (200-500 lines): Review within 8 hours
- Large PRs (>500 lines): Break into smaller PRs (anti-pattern)

**If PR sits unreviewed >24 hours:** Escalate to project lead

---

## 5. Vulnerability Testing

### 5.1 Vulnerability Testing Schedule

**Frequency:**

| Type | When | Tool | Pass Criteria |
|------|------|------|---------------|
| **Dependency Scan** | Every commit | `pip-audit` | ✅ 0 high/critical vulnerabilities |
| **Code Security Scan** | Daily (automated) | `bandit` | ✅ 0 high confidence issues |
| **Docker Image Scan** | Every image build | `trivy` | ✅ 0 critical vulnerabilities |
| **Full Security Audit** | End of each phase | Manual + tools | ✅ Security report signed off |

### 5.2 Dependency Vulnerability Scanning

**Tool:** `pip-audit` (integrated with `uv`)

**Commands:**
```bash
# Install pip-audit
uv pip install pip-audit

# Scan dependencies
uv run pip-audit

# Scan with JSON output for automation
uv run pip-audit --format json > vulnerability-report.json
```

**Automated Check (Pre-commit Hook):**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pypa/pip-audit
    rev: v2.6.1
    hooks:
      - id: pip-audit
        args: [--require-hashes, --disable-pip]
```

**Response to Vulnerabilities:**

| Severity | Action | Timeline |
|----------|--------|----------|
| **CRITICAL** | ⛔ Block merge, fix immediately | Within 4 hours |
| **HIGH** | ⚠️ Fix before merge | Within 24 hours |
| **MEDIUM** | 🟡 Create ticket, fix in next sprint | Within 1 week |
| **LOW** | 📝 Document, address opportunistically | Backlog |

### 5.3 Static Code Security Analysis

**Tool:** `bandit` (Python security linter)

**Commands:**
```bash
# Install bandit
uv pip install bandit

# Scan all source code
uv run bandit -r src/

# Scan with config file
uv run bandit -r src/ -c bandit.yaml

# Generate HTML report
uv run bandit -r src/ -f html -o security-report.html
```

**Configuration:**
```yaml
# bandit.yaml
tests:
  - B201  # flask_debug_true
  - B301  # pickle usage
  - B302  # marshal usage
  - B303  # md5/sha1 usage
  - B304  # insecure ciphers
  - B305  # insecure cipher modes
  - B306  # mktemp usage
  - B307  # eval usage
  - B308  # mark_safe usage
  - B310  # urllib urlopen
  - B311  # random usage
  - B312  # telnetlib usage
  - B313  # xml parsing
  - B314  # xml parsing
  - B315  # xml parsing
  - B316  # xml parsing
  - B317  # xml parsing
  - B318  # xml parsing
  - B319  # xml parsing
  - B320  # xml parsing
  - B321  # ftplib usage
  - B323  # unverified context
  - B324  # hashlib usage
  - B501  # request with verify=False
  - B502  # ssl with bad version
  - B503  # ssl with bad defaults
  - B504  # ssl with no version
  - B505  # weak cryptographic key
  - B506  # yaml load
  - B507  # ssh no host key verification
  - B601  # paramiko calls
  - B602  # shell=True
  - B603  # subprocess without shell
  - B604  # shell=True in call
  - B605  # shell=True in call
  - B606  # no shell with command
  - B607  # start_process_with_partial_path
  - B608  # hardcoded_sql_expressions
  - B609  # wildcard injection

skips:
  - "*/tests/*"  # Don't scan test files as strictly
```

**Automated Check (Pre-commit Hook):**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "bandit.yaml"]
```

### 5.4 Docker Image Vulnerability Scanning

**Tool:** `trivy` (Container security scanner)

**Commands:**
```bash
# Install trivy (macOS)
brew install aquasecurity/trivy/trivy

# Scan Docker image
trivy image uaip-assistant:latest

# Scan with severity filter (only high/critical)
trivy image --severity HIGH,CRITICAL uaip-assistant:latest

# Scan and fail build if critical found
trivy image --exit-code 1 --severity CRITICAL uaip-assistant:latest
```

**Integration with Docker Build:**
```yaml
# docker-compose.yml
services:
  uaip-app:
    build:
      context: .
      dockerfile: Dockerfile
    # Add security scanning step
    # Run: docker compose build && trivy image uaip-assistant:latest
```

### 5.5 Vulnerability Report Template

**File: `security/vulnerability-report-[date].md`**

```markdown
# Vulnerability Scan Report

**Date:** 2025-10-12
**Phase:** Phase 1 - Foundation
**Scan Type:** Full Security Audit

## Dependency Vulnerabilities (pip-audit)

| Package | Version | Vulnerability | Severity | Fix Available |
|---------|---------|---------------|----------|---------------|
| [None found] | - | - | - | - |

**Status:** ✅ PASS - No vulnerabilities detected

## Code Security Issues (bandit)

| File | Line | Issue | Severity | Confidence |
|------|------|-------|----------|------------|
| [None found] | - | - | - | - |

**Status:** ✅ PASS - No high confidence issues

## Docker Image Vulnerabilities (trivy)

| Image Layer | Package | Vulnerability | Severity | Fix |
|-------------|---------|---------------|----------|-----|
| [None found] | - | - | - | - |

**Status:** ✅ PASS - No critical vulnerabilities

## Manual Security Review

- [ ] API keys stored in environment variables only
- [ ] No secrets in Git history
- [ ] Input validation implemented for all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] HTTPS enforced for Claude API calls
- [ ] Database connections use SSL/TLS
- [ ] Rate limiting implemented
- [ ] Session timeout configured

**Status:** ✅ PASS - All checks passed

## Overall Security Status: ✅ APPROVED

**Signed off by:** [Security Reviewer]
**Date:** 2025-10-12
```

---

## 6. Regression Testing

### 6.1 What is Regression Testing?

**Definition:** Ensuring new code changes don't break existing functionality.

**When to Run:**
- ✅ Before every merge to `develop`
- ✅ After completing each phase
- ✅ Daily (automated CI/CD)
- ✅ Before release to production

### 6.2 Regression Test Suite

**Components:**

1. **Unit Tests** - Fast, isolated tests for each component
2. **Integration Tests** - Tests for component interactions
3. **End-to-End Tests** - Full user workflow tests
4. **Database Migration Tests** - Schema changes don't break queries
5. **API Compatibility Tests** - Claude API integration still works

### 6.3 Regression Testing Strategy

**Three Tiers:**

```
┌──────────────────────────────────────────────────────┐
│  TIER 1: Fast Regression (Every commit)             │
│  - Unit tests only                                   │
│  - Runtime: <30 seconds                              │
│  - Run: Pre-commit hook                              │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  TIER 2: Full Regression (Every merge to develop)   │
│  - All unit + integration tests                      │
│  - Runtime: <5 minutes                               │
│  - Run: CI/CD pipeline                               │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  TIER 3: Complete Regression (Phase completion)     │
│  - All tests + E2E + performance                     │
│  - Runtime: <30 minutes                              │
│  - Run: Manual trigger before production             │
└──────────────────────────────────────────────────────┘
```

### 6.4 Regression Test Commands

```bash
# Tier 1: Fast regression (pre-commit)
uv run pytest tests/unit/ -v --maxfail=1

# Tier 2: Full regression (CI/CD)
uv run pytest tests/ -v --cov=src --cov-fail-under=80

# Tier 3: Complete regression (manual)
uv run pytest tests/ -v --cov=src --cov-report=html --durations=10

# Run only regression test markers
uv run pytest -m regression -v

# Run with parallel execution (faster)
uv run pytest -n auto tests/
```

### 6.5 Regression Test Markers

**Mark tests as regression tests:**

```python
import pytest

@pytest.mark.regression
@pytest.mark.tier1
def test_orchestrator_initialization():
    """Critical path: Orchestrator must always initialize correctly"""
    orchestrator = UAIPOrchestrator()
    assert orchestrator is not None

@pytest.mark.regression
@pytest.mark.tier2
async def test_stage1_agent_integration():
    """Integration: Stage1 agent works with database"""
    agent = Stage1Agent()
    session_id = await agent.create_session()
    assert session_id is not None

@pytest.mark.regression
@pytest.mark.tier3
async def test_complete_session_workflow():
    """E2E: Full session from start to charter generation"""
    # 30+ line test covering entire workflow
    pass
```

**pytest.ini configuration:**
```ini
[pytest]
markers =
    regression: Regression test (critical functionality)
    tier1: Fast regression tests (<30s total)
    tier2: Full regression tests (<5min total)
    tier3: Complete regression tests (E2E, slow)
    integration: Integration tests
    unit: Unit tests
```

### 6.6 Regression Test Matrix

**Test Coverage by Component:**

| Component | Unit Tests | Integration Tests | E2E Tests | Total |
|-----------|-----------|------------------|-----------|-------|
| Orchestrator | 15 | 5 | 2 | 22 |
| Stage1Agent | 20 | 8 | 1 | 29 |
| Stage2Agent | 18 | 7 | 1 | 26 |
| Stage3Agent | 22 | 9 | 1 | 32 |
| Stage4Agent | 16 | 6 | 1 | 23 |
| Stage5Agent | 25 | 10 | 1 | 36 |
| ResponseQualityAgent | 18 | 5 | - | 23 |
| StageGateValidator | 15 | 4 | - | 19 |
| ConsistencyChecker | 12 | 6 | - | 18 |
| Database | 10 | 8 | - | 18 |
| CLI | 8 | 5 | 2 | 15 |
| **TOTAL** | **179** | **73** | **9** | **261** |

**Target:** Maintain >80% coverage across all components

### 6.7 Regression Test Failure Protocol

**When regression test fails:**

1. ⛔ **STOP all new development immediately**
2. 🔍 **Investigate root cause** (which commit broke it?)
3. 🔄 **Revert breaking commit** if fix is not immediate
4. 🔧 **Fix the issue** with tests
5. ✅ **Verify all regression tests pass** before resuming development
6. 📝 **Document in incident log**

**Incident Log Entry:**
```markdown
## Regression Failure Incident

**Date:** 2025-10-12 14:30
**Test:** test_stage1_generate_problem_statement
**Failure:** AssertionError: ml_archetype field missing
**Root Cause:** Commit def456 changed ProblemStatement schema
**Fix:** Added ml_archetype to ProblemStatement dataclass
**Fix Commit:** ghi789
**Time to Resolution:** 45 minutes
**Lesson:** Schema changes must update all dependent tests
```

---

## 7. Quality Gates

### 7.1 Quality Gate Definition

**Quality Gates are GO/NO-GO checkpoints** that must be passed before work can proceed.

**Gates in our workflow:**

```
[Task Start] → [Code] → [GATE 1] → [Review] → [GATE 2] → [Merge] → [GATE 3] → [Done]
                         Tests              Approval           Regression
```

### 7.2 Gate 1: Testing Quality Gate

**MUST PASS before code review request:**

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| ✅ All tests pass | `pytest -v` | 0 failures, 0 errors |
| ✅ Coverage ≥80% | `pytest --cov --cov-fail-under=80` | Threshold met |
| ✅ No type errors | `mypy src/` | 0 errors |
| ✅ Linting passes | `ruff check src/` | 0 errors |
| ✅ Format check | `black --check src/` | All files formatted |
| ✅ Dependency security | `pip-audit` | 0 high/critical vulnerabilities |
| ✅ Code security | `bandit -r src/` | 0 high confidence issues |

**Automated Check Script:**
```bash
#!/bin/bash
# scripts/quality-gate-1.sh

echo "Running Quality Gate 1: Testing..."

set -e  # Exit on first failure

echo "1/7 Running tests..."
uv run pytest -v

echo "2/7 Checking coverage..."
uv run pytest --cov=src --cov-fail-under=80

echo "3/7 Type checking..."
uv run mypy src/

echo "4/7 Linting..."
uv run ruff check src/

echo "5/7 Format checking..."
uv run black --check src/

echo "6/7 Dependency security scan..."
uv run pip-audit

echo "7/7 Code security scan..."
uv run bandit -r src/ -ll

echo "✅ Quality Gate 1 PASSED - Ready for code review"
```

### 7.3 Gate 2: Code Review Quality Gate

**MUST PASS before merge to develop:**

| Check | Responsible | Pass Criteria |
|-------|-------------|---------------|
| ✅ Reviewer approval | Code reviewer | At least 1 approval |
| ✅ All comments addressed | PR author | 0 unresolved comments |
| ✅ TDD compliance verified | Code reviewer | Tests written first |
| ✅ Security checklist | Code reviewer | No security issues |
| ✅ Task list updated | PR author | Task marked COMPLETED |

### 7.4 Gate 3: Regression Quality Gate

**MUST PASS before merge to main (production):**

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| ✅ All regression tests pass | `pytest -m regression` | 0 failures |
| ✅ Integration tests pass | `pytest tests/integration/` | 0 failures |
| ✅ E2E tests pass | `pytest tests/e2e/` | 0 failures |
| ✅ Docker builds successfully | `docker compose build` | Success |
| ✅ Docker image security | `trivy image ...` | 0 critical vulns |
| ✅ Performance benchmarks | Manual verification | Within targets |

**Automated Check Script:**
```bash
#!/bin/bash
# scripts/quality-gate-3.sh

echo "Running Quality Gate 3: Regression..."

set -e

echo "1/6 Running regression tests..."
uv run pytest -m regression -v

echo "2/6 Running integration tests..."
uv run pytest tests/integration/ -v

echo "3/6 Running E2E tests..."
uv run pytest tests/e2e/ -v

echo "4/6 Building Docker images..."
docker compose build

echo "5/6 Scanning Docker images..."
trivy image --severity CRITICAL --exit-code 1 uaip-assistant:latest

echo "6/6 Checking performance benchmarks..."
# Run performance tests if implemented

echo "✅ Quality Gate 3 PASSED - Ready for production"
```

### 7.5 Quality Gate Enforcement

**Pre-commit Hook (Gate 1 - Partial):**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-quick
        name: Quick test check
        entry: uv run pytest tests/unit/ --maxfail=1
        language: system
        pass_filenames: false
        always_run: true

      - id: ruff
        name: Ruff linting
        entry: uv run ruff check
        language: system
        types: [python]

      - id: black
        name: Black formatting
        entry: uv run black --check
        language: system
        types: [python]
```

**GitHub Actions (Gate 1 & 3 - Full):**
```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on:
  pull_request:
    branches: [develop, main]

jobs:
  gate-1-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: uv pip install -r pyproject.toml
      - run: ./scripts/quality-gate-1.sh

  gate-3-regression:
    if: github.base_ref == 'main'
    runs-on: ubuntu-latest
    needs: gate-1-testing
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install uv
      - run: uv pip install -r pyproject.toml
      - run: ./scripts/quality-gate-3.sh
```

---

## 8. Workflow Enforcement

### 8.1 Developer Checklist (Daily)

**Before starting work:**
```
□ Pull latest changes from develop
□ Review task list, select atomic task
□ Move task to IN_PROGRESS
□ Create feature branch
```

**During work:**
```
□ Write tests FIRST (TDD)
□ Implement minimal code to pass tests
□ Refactor while keeping tests green
□ Commit every 30-60 minutes
□ Update task list status
```

**Before requesting review:**
```
□ Run Quality Gate 1 checks
□ All tests passing
□ Coverage ≥80%
□ Update task list (mark COMPLETED)
□ Update checkpoint log
□ Push to feature branch
□ Create pull request
```

**After review approval:**
```
□ Merge to develop
□ Delete feature branch
□ Pull latest develop
□ Start next atomic task
```

### 8.2 Team Lead Checklist (Weekly)

```
□ Review task list progress
□ Check checkpoint frequency (minimum 1/day per developer)
□ Review vulnerability scan reports
□ Run full regression suite (Tier 3)
□ Check code coverage trends
□ Review incident log (regression failures)
□ Update project status report
```

### 8.3 Phase Completion Checklist

**Before marking phase as COMPLETE:**

```
□ All phase tasks marked COMPLETED
□ All tests passing (unit + integration + E2E)
□ Code coverage ≥80% for phase components
□ All code reviewed and merged to develop
□ Vulnerability scan completed and approved
□ Full regression suite (Tier 3) passed
□ Performance benchmarks met
□ Documentation updated
□ Phase security report signed off
□ Phase merged to main
□ Git tag created (e.g., v1.0-phase1)
□ Retrospective completed
```

### 8.4 Violation Consequences

**If workflow rules are violated:**

| Violation | Consequence |
|-----------|-------------|
| Code merged without tests | ⛔ Immediate revert, tests must be added |
| Code merged without review | ⛔ Immediate revert, formal review required |
| Tests not written first (TDD) | ⚠️ Code review rejection |
| Checkpoint frequency <1/day | ⚠️ Warning, discussion with lead |
| Quality gate bypass | ⛔ Merge blocked, must pass gates |
| Hardcoded secrets committed | 🚨 Immediate key rotation, Git history scrub |

---

## 9. Tools & Automation

### 9.1 Required Development Tools

**Install all before starting:**

```bash
# Python environment
brew install python@3.11
pip install uv

# Testing & Quality
uv pip install pytest pytest-asyncio pytest-cov
uv pip install black ruff mypy
uv pip install bandit pip-audit

# Security scanning
brew install aquasecurity/trivy/trivy

# Git hooks
uv pip install pre-commit
pre-commit install

# Docker
brew install --cask docker
```

### 9.2 Pre-commit Configuration

**File: `.pre-commit-config.yaml`**

```yaml
repos:
  # Fast checks (run on every commit)
  - repo: local
    hooks:
      # Quick unit tests
      - id: pytest-quick
        name: Fast unit tests
        entry: uv run pytest tests/unit/ -x --tb=short
        language: system
        pass_filenames: false
        always_run: true

      # Code formatting
      - id: black
        name: Black code formatter
        entry: uv run black
        language: system
        types: [python]

      # Linting
      - id: ruff
        name: Ruff linter
        entry: uv run ruff check --fix
        language: system
        types: [python]

      # Type checking
      - id: mypy
        name: MyPy type checker
        entry: uv run mypy
        language: system
        types: [python]

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-ll", "-r", "src/"]

  # Prevent secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # File checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
```

### 9.3 VS Code Configuration (Recommended)

**File: `.vscode/settings.json`**

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.analysis.typeCheckingMode": "strict",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true
  }
}
```

**File: `.vscode/extensions.json`**

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-azuretools.vscode-docker"
  ]
}
```

### 9.4 Automation Scripts

**Location: `scripts/`**

```bash
scripts/
├── quality-gate-1.sh      # Run all Gate 1 checks
├── quality-gate-3.sh      # Run all Gate 3 checks
├── run-regression.sh      # Run all regression tests
├── security-scan.sh       # Run all security scans
├── update-task-list.sh    # Helper to update task list
└── create-checkpoint.sh   # Standardized commit helper
```

**Example: `scripts/create-checkpoint.sh`**

```bash
#!/bin/bash
# Helper script for standardized commits

echo "Creating checkpoint..."

# Check if tests pass
if ! uv run pytest -x; then
    echo "❌ Tests failing - fix before committing"
    exit 1
fi

# Prompt for task ID
read -p "Task ID (e.g., F1.3): " TASK_ID
read -p "Brief description: " DESCRIPTION
read -p "Status (COMPLETED/IN_PROGRESS): " STATUS

# Get test stats
TEST_STATS=$(uv run pytest --co -q | wc -l)
COVERAGE=$(uv run pytest --cov=src --cov-report=term | grep "TOTAL" | awk '{print $4}')

# Create commit
git add .
git commit -m "[$TASK_ID] $DESCRIPTION

Task: $TASK_ID
Status: $STATUS
Tests: $TEST_STATS passing
Coverage: $COVERAGE"

echo "✅ Checkpoint created"
```

---

## 10. Summary: The Development Loop

```
┌─────────────────────────────────────────────────────────────┐
│                  DAILY DEVELOPMENT CYCLE                    │
└─────────────────────────────────────────────────────────────┘

1. SELECT ATOMIC TASK from task list
   → Move to IN_PROGRESS
   → Create feature branch

2. WRITE TESTS FIRST (TDD)
   → Red: Write failing test
   → Green: Minimal implementation
   → Refactor: Improve code

3. CHECKPOINT FREQUENTLY
   → Commit every 30-60 minutes
   → Reference task ID
   → Update task list

4. RUN QUALITY GATE 1
   → All tests pass
   → Coverage ≥80%
   → Security scans pass

5. REQUEST CODE REVIEW
   → Create pull request
   → Address reviewer comments

6. MERGE TO DEVELOP
   → After approval
   → Run regression tests
   → Delete feature branch

7. REPEAT
   → Select next atomic task
```

---

## Document Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-12 | Initial workflow standards document | Project Lead |

---

## Acknowledgment

**By contributing to this project, I acknowledge:**

- ✅ I have read and understand this workflow document
- ✅ I agree to follow all mandatory rules and processes
- ✅ I understand that violations will result in code rejection
- ✅ I will checkpoint code frequently to avoid drift
- ✅ I will write tests FIRST (TDD) without exception
- ✅ I will not merge code without review
- ✅ I will run security scans regularly

**Signed:** ___________________________ Date: __________

---

**END OF WORKFLOW DOCUMENT**

*This document governs all development work on the U-AIP Scoping Assistant project. Adherence is mandatory for all contributors.*
